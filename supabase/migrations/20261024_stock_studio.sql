-- Stock Studio: authenticated RPC only. Existing business rows are not migrated.
-- The existing private inventario schema is not exposed through the Data API.
create schema if not exists stock_studio_private;
revoke all on schema stock_studio_private from public, anon, authenticated;

create table if not exists stock_studio_private.requests (
  user_id integer not null,
  request_id uuid not null,
  action text not null,
  payload jsonb not null,
  result jsonb,
  created_at timestamptz not null default now(),
  primary key (user_id, request_id)
);
revoke all on stock_studio_private.requests from public, anon, authenticated;

create or replace function stock_studio_private.actor()
returns inventario.usuarios language plpgsql security definer
set search_path = '' stable as $$
declare actor inventario.usuarios;
begin
  select u.* into actor
  from inventario.usuarios u join auth.users a on lower(a.email)=lower(u.email)
  where a.id=auth.uid() and a.email_confirmed_at is not null and u.activo;
  if actor.id is null then
    raise exception 'Tu correo verificado no tiene acceso activo al inventario.' using errcode='42501';
  end if;
  return actor;
end $$;
revoke all on function stock_studio_private.actor() from public, anon, authenticated;

create or replace function stock_studio_private.number_value(data jsonb, field text, allow_zero boolean default true)
returns numeric language plpgsql set search_path = '' immutable as $$
declare n numeric;
begin
  n := (data->>field)::numeric;
  if n is null or n::text in ('NaN','Infinity','-Infinity') or n<0 or (not allow_zero and n=0) then
    raise exception 'Revisa el valor de %.',field using errcode='22023';
  end if;
  return n;
exception when invalid_text_representation or numeric_value_out_of_range then
  raise exception 'Revisa el valor de %.',field using errcode='22023';
end $$;
revoke all on function stock_studio_private.number_value(jsonb,text,boolean) from public, anon, authenticated;

create or replace function public.stock_studio_data()
returns jsonb language plpgsql security definer set search_path = '' stable as $$
declare a inventario.usuarios; result jsonb;
begin
  a:=stock_studio_private.actor();
  select jsonb_build_object(
    'user',jsonb_build_object('id',a.id,'nombre',a.nombre_completo,'write',a.has_permisos,'rol',a.rol),
    'products',coalesce((select jsonb_agg(jsonb_build_object('id',p.id,'nombre',p.nombre,'sku',p.sku,
      'categoria',c.nombre,'categoria_id',p.categoria_id,'descripcion',p.descripcion,'precio',p.precio,
      'stock',p.cantidad_stock,'minimo',p.stock_minimo,'se_vende',p.se_vende,'litros_por_unidad',p.litros_por_unidad) order by p.nombre)
      from inventario.productos p join inventario.categorias c on c.id=p.categoria_id where p.activo),'[]'::jsonb),
    'categories',coalesce((select jsonb_agg(jsonb_build_object('id',id,'nombre',nombre,'color',color,'descripcion',descripcion) order by nombre) from inventario.categorias where activa),'[]'::jsonb),
    'movements',coalesce((select jsonb_agg(to_jsonb(m) order by m.fecha desc) from (
      select m.id,p.nombre as producto,m.tipo,m.cantidad,m.motivo,m.observaciones,
      to_char(m.fecha,'YYYY-MM-DD"T"HH24:MI:SS')||'Z' as fecha,u.nombre_completo as usuario
      from inventario.movimientos_stock m join inventario.productos p on p.id=m.producto_id join inventario.usuarios u on u.id=m.usuario_id
      order by m.fecha desc limit 500) m),'[]'::jsonb),
    'sales',coalesce((select jsonb_agg(to_jsonb(v) order by v.fecha desc) from (
      select v.id,p.nombre as producto,v.cantidad,v.total,v.precio_unitario,v.observaciones,v.motivo,v.vendedor_id,
      to_char(v.fecha,'YYYY-MM-DD"T"HH24:MI:SS')||'Z' as fecha from inventario.ventas v join inventario.productos p on p.id=v.producto_id
      order by v.fecha desc limit 500) v),'[]'::jsonb),
    'daily_sales',coalesce((select jsonb_agg(jsonb_build_object('day',d.day::date::text,'total',coalesce(s.total,0)) order by d.day)
      from generate_series((now() at time zone 'America/Lima')::date-6,(now() at time zone 'America/Lima')::date,interval '1 day') d(day)
      left join (select (fecha at time zone 'UTC' at time zone 'America/Lima')::date as day,sum(total) as total
        from inventario.ventas where fecha >= ((now() at time zone 'America/Lima')::date-6)::timestamp at time zone 'America/Lima' at time zone 'UTC'
        group by 1) s on s.day=d.day::date),'[]'::jsonb),
    'sellers',coalesce((select jsonb_agg(jsonb_build_object('id',id,'nombre',nombre,'email',email,'telefono',telefono,'comision_porcentaje',comision_porcentaje) order by nombre) from inventario.vendedores where activo),'[]'::jsonb),
    'users',coalesce((select jsonb_agg(jsonb_build_object('id',id,'nombre',nombre_completo,'activo',activo,
      'write',case when a.has_permisos then has_permisos else null end,'rol',case when a.has_permisos then rol else null end,
      'email',case when a.has_permisos then email else null end) order by nombre_completo) from inventario.usuarios
      where a.has_permisos or activo),'[]'::jsonb),
    'lots',coalesce((select jsonb_agg(to_jsonb(l) order by l.fecha_preparacion desc) from (
      select l.id,l.nombre,l.descripcion,l.cantidad_preparada,l.cantidad_vendida,l.costo_total,l.fecha_preparacion,
      coalesce((select jsonb_agg(jsonb_build_object('producto',p.nombre,'cantidad',i.cantidad_usada,'costo',i.costo_unitario))
      from inventario.ingredientes_lote i join inventario.productos p on p.id=i.producto_id where i.lote_id=l.id),'[]'::jsonb) as ingredientes
      from inventario.lotes l order by l.fecha_preparacion desc limit 200) l),'[]'::jsonb),
    'bar_controls',coalesce((select jsonb_agg(to_jsonb(b) order by b.fecha_creacion desc) from (
      select b.id,b.fecha_operacion,b.hora_cierre,b.total_esperado,b.monto_entregado,b.diferencia_caja,b.observaciones,b.fecha_creacion,
      u.nombre_completo as responsable,coalesce((select jsonb_agg(to_jsonb(d)-'control_id') from inventario.detalle_controles_barra d where d.control_id=b.id),'[]'::jsonb) as detalles
      from inventario.controles_barra b join inventario.usuarios u on u.id=b.responsable_id order by b.fecha_creacion desc limit 200) b),'[]'::jsonb),
    'history_limit',500,'provider','supabase') into result;
  return result;
end $$;
revoke all on function public.stock_studio_data() from public, anon;
grant execute on function public.stock_studio_data() to authenticated;

create or replace function public.stock_studio_write(p_action text,p_data jsonb,p_request_id uuid)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  a inventario.usuarios; p inventario.productos; ingredient inventario.productos;
  previous stock_studio_private.requests; n numeric; price numeric; minimum numeric;
  target integer; new_id integer; quantity integer; category integer; seller integer; lot integer;
  label text; v_sku text; kind text; reason text; row jsonb; response_data jsonb; total numeric:=0;
  start_stock integer; end_stock integer; unit_price numeric;
begin
  a:=stock_studio_private.actor();
  if not coalesce(a.has_permisos,false) then raise exception 'Tu cuenta tiene acceso de solo lectura.' using errcode='42501'; end if;
  if p_request_id is null or p_data is null or jsonb_typeof(p_data)<>'object' then raise exception 'Solicitud no válida.' using errcode='22023'; end if;
  insert into stock_studio_private.requests(user_id,request_id,action,payload)
    values(a.id,p_request_id,p_action,p_data) on conflict do nothing;
  if not found then
    select * into previous from stock_studio_private.requests where user_id=a.id and request_id=p_request_id;
    if previous.action<>p_action or previous.payload<>p_data then raise exception 'La solicitud ya se utilizó con otros datos.' using errcode='22023'; end if;
    return previous.result;
  end if;
  if p_action in ('product_save','product_archive') then
    target:=nullif(p_data->>'id','')::integer;
    if p_action='product_archive' then
      update inventario.productos set activo=false,fecha_actualizacion=now() at time zone 'UTC' where id=target;
      if not found then raise exception 'Producto no encontrado.' using errcode='22023'; end if;
      new_id:=target;
    else
      label:=trim(p_data->>'nombre'); v_sku:=trim(p_data->>'sku');
      price:=stock_studio_private.number_value(p_data,'precio'); minimum:=stock_studio_private.number_value(p_data,'minimo');
      category:=(p_data->>'categoria_id')::integer;
      if coalesce(label,'')='' or length(label)>150 or coalesce(v_sku,'')='' or length(v_sku)>50 or minimum<>floor(minimum)
        or not exists(select 1 from inventario.categorias where id=category and activa) then raise exception 'Revisa la ficha del producto.' using errcode='22023'; end if;
      if target is null then
        n:=case when p_data ? 'litros_por_unidad' then stock_studio_private.number_value(p_data,'litros_por_unidad',false) else 1 end;
        insert into inventario.productos(nombre,sku,categoria_id,descripcion,precio,cantidad_stock,stock_minimo,litros_por_unidad,se_vende,activo,fecha_creacion,fecha_actualizacion)
        values(label,v_sku,category,left(p_data->>'descripcion',5000),price,0,minimum,n,coalesce((p_data->>'se_vende')::boolean,true),true,now() at time zone 'UTC',now() at time zone 'UTC') returning id into new_id;
      else
        update inventario.productos set nombre=label,sku=v_sku,categoria_id=category,descripcion=left(p_data->>'descripcion',5000),precio=price,stock_minimo=minimum,
        se_vende=coalesce((p_data->>'se_vende')::boolean,true),fecha_actualizacion=now() at time zone 'UTC' where id=target and activo returning id into new_id;
        if not found then raise exception 'Producto no encontrado.' using errcode='22023'; end if;
      end if;
    end if;
  elsif p_action='movement' then
    n:=stock_studio_private.number_value(p_data,'cantidad',p_data->>'tipo'='ajuste');
    if n<>floor(n) then raise exception 'La cantidad debe ser un número entero de unidades.' using errcode='22023'; end if;
    quantity:=n; kind:=p_data->>'tipo'; target:=(p_data->>'producto_id')::integer;
    if kind not in ('entrada','salida','venta','ajuste') then raise exception 'Tipo de movimiento no válido.' using errcode='22023'; end if;
    select * into p from inventario.productos where id=target and activo for update;
    if not found then raise exception 'Producto no encontrado.' using errcode='22023'; end if;
    if kind='venta' and not p.se_vende then raise exception 'Este producto es un insumo.' using errcode='22023'; end if;
    if kind in ('salida','venta') and p.cantidad_stock<quantity then raise exception 'Stock insuficiente.' using errcode='22023'; end if;
    reason:=coalesce(nullif(trim(p_data->>'motivo'),''),case when kind='venta' then 'Venta' else 'Movimiento de stock' end);
    if kind='ajuste' then
      quantity:=n-p.cantidad_stock;
      if coalesce(nullif(trim(p_data->>'motivo'),''),'')='' then raise exception 'Indica el motivo del ajuste.' using errcode='22023'; end if;
    end if;
    update inventario.productos set cantidad_stock=case when kind='ajuste' then n when kind='entrada' then cantidad_stock+quantity else cantidad_stock-quantity end,
      fecha_actualizacion=now() at time zone 'UTC' where id=target;
    insert into inventario.movimientos_stock(producto_id,usuario_id,tipo,cantidad,motivo,observaciones,fecha)
      values(target,a.id,case when kind='venta' then 'salida' else kind end,quantity,left(reason,200),left(p_data->>'observaciones',5000),now() at time zone 'UTC') returning id into new_id;
    if kind='venta' then
      price:=stock_studio_private.number_value(p_data,'precio'); seller:=nullif(p_data->>'vendedor_id','')::integer;
      if seller is not null and not exists(select 1 from inventario.vendedores where id=seller and activo) then raise exception 'Vendedor no válido.' using errcode='22023'; end if;
      insert into inventario.ventas(producto_id,usuario_id,vendedor_id,cantidad,precio_unitario,total,motivo,observaciones,fecha)
      values(target,a.id,seller,quantity,price,quantity*price,left(reason,100),left(p_data->>'observaciones',5000),now() at time zone 'UTC') returning id into new_id;
    end if;
    if (select cantidad_stock<stock_minimo from inventario.productos where id=target)
      and not exists(select 1 from inventario.alertas_stock where producto_id=target and not leida) then
      insert into inventario.alertas_stock(producto_id,tipo,mensaje,leida,fecha_creacion)
      values(target,'bajo_stock',left(p.nombre||' por debajo del stock mínimo',255),false,now() at time zone 'UTC');
    end if;
  elsif p_action='category_save' then
    target:=nullif(p_data->>'id','')::integer; label:=trim(p_data->>'nombre');
    if coalesce(label,'')='' or length(label)>100 then raise exception 'Nombre de categoría no válido.' using errcode='22023'; end if;
    if target is null then
      insert into inventario.categorias(nombre,color,descripcion,activa,fecha_creacion) values(label,'#0d9b8b',left(p_data->>'descripcion',5000),true,now() at time zone 'UTC') returning id into new_id;
    else
      update inventario.categorias set nombre=label,descripcion=left(p_data->>'descripcion',5000) where id=target returning id into new_id;
      if not found then raise exception 'Categoría no encontrada.' using errcode='22023'; end if;
    end if;
  elsif p_action='seller_save' then
    target:=nullif(p_data->>'id','')::integer; label:=trim(p_data->>'nombre');
    n:=stock_studio_private.number_value(p_data,'comision_porcentaje');
    if coalesce(label,'')='' or length(label)>100 or n>100 then raise exception 'Revisa el nombre y la comisión.' using errcode='22023'; end if;
    if target is null then
      insert into inventario.vendedores(nombre,email,telefono,comision_porcentaje,activo,fecha_creacion)
      values(label,nullif(left(trim(p_data->>'email'),100),''),left(p_data->>'telefono',20),n,true,now() at time zone 'UTC') returning id into new_id;
    else
      update inventario.vendedores set nombre=label,email=nullif(left(trim(p_data->>'email'),100),''),telefono=left(p_data->>'telefono',20),comision_porcentaje=n where id=target returning id into new_id;
      if not found then raise exception 'Vendedor no encontrado.' using errcode='22023'; end if;
    end if;
  elsif p_action='user_access' then
    target:=(p_data->>'id')::integer;
    if target=a.id then raise exception 'No puedes modificar tu propio acceso.' using errcode='22023'; end if;
    if coalesce(p_data->>'rol','') not in ('admin','gerente','vendedor')
      or coalesce(p_data->>'write','') not in ('true','false') or coalesce(p_data->>'activo','') not in ('true','false') then
      raise exception 'Revisa el rol, estado y permisos.' using errcode='22023'; end if;
    update inventario.usuarios set has_permisos=(p_data->>'write')::boolean,activo=(p_data->>'activo')::boolean,rol=p_data->>'rol',fecha_actualizacion=now() at time zone 'UTC'
    where id=target returning id into new_id;
    if not found then raise exception 'Usuario no encontrado.' using errcode='22023'; end if;
  elsif p_action='lot_create' then
    target:=(p_data->>'producto_id')::integer; n:=stock_studio_private.number_value(p_data,'cantidad',false);
    if n<>floor(n) or jsonb_typeof(p_data->'ingredientes')<>'array' or jsonb_array_length(p_data->'ingredientes')=0 then raise exception 'Revisa las cantidades e ingredientes.' using errcode='22023'; end if;
    quantity:=n;
    -- A deterministic order avoids deadlocks for concurrent multi-product preparations.
    perform id from inventario.productos where id=target or id in (select (x->>'producto_id')::integer from jsonb_array_elements(p_data->'ingredientes') x) order by id for update;
    select * into p from inventario.productos where id=target and activo;
    if not found then raise exception 'Producto final no encontrado.' using errcode='22023'; end if;
    for row in select jsonb_build_object('producto_id',(x->>'producto_id')::integer,'cantidad',sum((x->>'cantidad')::numeric))
      from jsonb_array_elements(p_data->'ingredientes') x group by (x->>'producto_id')::integer loop
      n:=stock_studio_private.number_value(row,'cantidad',false);
      select * into ingredient from inventario.productos where id=(row->>'producto_id')::integer and activo;
      if not found or ingredient.id=target or n<>floor(n) or ingredient.cantidad_stock<n then raise exception 'Ingrediente no válido o stock insuficiente.' using errcode='22023'; end if;
      total:=total+n*ingredient.precio;
    end loop;
    insert into inventario.lotes(nombre,descripcion,cantidad_preparada,cantidad_vendida,costo_total,usuario_id,fecha_preparacion)
      values(p.nombre,left(p_data->>'descripcion',5000),quantity,0,total,a.id,now() at time zone 'UTC') returning id into new_id;
    for row in select jsonb_build_object('producto_id',(x->>'producto_id')::integer,'cantidad',sum((x->>'cantidad')::numeric))
      from jsonb_array_elements(p_data->'ingredientes') x group by (x->>'producto_id')::integer loop
      n:=(row->>'cantidad')::numeric;
      select * into ingredient from inventario.productos where id=(row->>'producto_id')::integer;
      insert into inventario.ingredientes_lote(lote_id,producto_id,cantidad_usada,costo_unitario) values(new_id,ingredient.id,n,ingredient.precio);
      update inventario.productos set cantidad_stock=cantidad_stock-n,fecha_actualizacion=now() at time zone 'UTC' where id=ingredient.id;
      insert into inventario.movimientos_stock(producto_id,usuario_id,tipo,cantidad,motivo,observaciones,fecha)
        values(ingredient.id,a.id,'salida',n,'Preparación de lote','Lote: '||p.nombre,now() at time zone 'UTC');
    end loop;
    update inventario.productos set cantidad_stock=cantidad_stock+quantity,fecha_actualizacion=now() at time zone 'UTC' where id=target;
    insert into inventario.movimientos_stock(producto_id,usuario_id,tipo,cantidad,motivo,observaciones,fecha)
      values(target,a.id,'entrada',quantity,'Preparación de lote','Lote: '||p.nombre,now() at time zone 'UTC');
  elsif p_action='bar_close' then
    target:=(p_data->>'responsable_id')::integer; price:=stock_studio_private.number_value(p_data,'monto_entregado');
    if not exists(select 1 from inventario.usuarios where id=target and activo) or jsonb_typeof(p_data->'detalles')<>'array'
       or coalesce(jsonb_array_length(p_data->'detalles'),0)=0 then raise exception 'Revisa el responsable y el conteo.' using errcode='22023'; end if;
    for row in select * from jsonb_array_elements(p_data->'detalles') loop
      n:=stock_studio_private.number_value(row,'stock_inicial'); minimum:=stock_studio_private.number_value(row,'stock_final');
      unit_price:=stock_studio_private.number_value(row,'precio');
      if n<>floor(n) or minimum<>floor(minimum) or minimum>n or coalesce(trim(row->>'producto'),'')='' then raise exception 'Conteo de barra no válido.' using errcode='22023'; end if;
      total:=total+(n-minimum)*unit_price;
    end loop;
    insert into inventario.controles_barra(fecha_operacion,hora_cierre,usuario_id,responsable_id,observaciones,total_esperado,monto_entregado,diferencia_caja,fecha_creacion)
      values((p_data->>'fecha')::date,left(p_data->>'hora',20),a.id,target,left(p_data->>'observaciones',5000),total,price,price-total,now() at time zone 'UTC') returning id into new_id;
    for row in select * from jsonb_array_elements(p_data->'detalles') loop
      start_stock:=(row->>'stock_inicial')::integer; end_stock:=(row->>'stock_final')::integer; unit_price:=(row->>'precio')::numeric;
      insert into inventario.detalle_controles_barra(control_id,producto,stock_inicial,stock_final,vendidos,precio_unitario,total_esperado)
        values(new_id,left(row->>'producto',150),start_stock,end_stock,start_stock-end_stock,unit_price,(start_stock-end_stock)*unit_price);
    end loop;
  else
    raise exception 'Operación no disponible.' using errcode='22023';
  end if;
  response_data:=jsonb_build_object('ok',true,'id',new_id);
  update stock_studio_private.requests set result=response_data where user_id=a.id and request_id=p_request_id;
  return response_data;
exception when unique_violation then
  raise exception 'Ya existe un registro con ese SKU, nombre o correo.' using errcode='22023';
end $$;
revoke all on function public.stock_studio_write(text,jsonb,uuid) from public, anon;
grant execute on function public.stock_studio_write(text,jsonb,uuid) to authenticated;

notify pgrst, 'reload schema';
