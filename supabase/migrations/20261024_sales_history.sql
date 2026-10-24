-- Historical reconstruction and reversible administration. No existing sales are changed.
create table if not exists stock_studio_private.sale_state(
  sale_id integer primary key references inventario.ventas(id),
  voided boolean not null default false,
  source text not null default 'registrada',
  reference text,
  updated_at timestamptz not null default now()
);
create table if not exists stock_studio_private.audit_log(
  id bigint generated always as identity primary key,
  sale_id integer not null,
  actor_id integer not null,
  action text not null,
  reason text not null,
  before_value jsonb,
  after_value jsonb,
  affects_stock boolean not null default false,
  request_id uuid not null,
  created_at timestamptz not null default now(),
  unique(actor_id,request_id)
);
revoke all on stock_studio_private.sale_state,stock_studio_private.audit_log from public,anon,authenticated;

create or replace function public.stock_studio_sales_report(
 p_from date,p_to date,p_page integer default 1,p_status text default 'active',p_search text default '',p_seller integer default null,p_limit integer default 25)
returns jsonb language plpgsql security definer set search_path='' stable as $$
declare a inventario.usuarios; result jsonb;
begin
 a:=stock_studio_private.actor();
 if p_from is null or p_to is null or p_to<p_from or p_to-p_from>3660 or p_page<1 or p_page>100000 or p_limit<1 or p_limit>10000
   or p_status not in ('active','all','voided') then raise exception 'Revisa las fechas y filtros.' using errcode='22023'; end if;
 with base as (
  select v.id,v.producto_id,p.nombre as producto,p.sku,c.nombre as categoria,v.cantidad,v.precio_unitario,v.total,v.vendedor_id,
   coalesce(s.nombre,'Sin asignar') as vendedor,v.motivo,v.observaciones,
   to_char(v.fecha,'YYYY-MM-DD"T"HH24:MI:SS')||'Z' as fecha,
   (v.fecha at time zone 'UTC' at time zone 'America/Lima') as local_time,
   coalesce(m.voided,false) as voided,coalesce(m.source,'registrada') as source,m.reference
  from inventario.ventas v join inventario.productos p on p.id=v.producto_id
  left join inventario.categorias c on c.id=p.categoria_id left join inventario.vendedores s on s.id=v.vendedor_id
  left join stock_studio_private.sale_state m on m.sale_id=v.id
  where v.fecha>= (p_from::timestamp at time zone 'America/Lima' at time zone 'UTC')
   and v.fecha< ((p_to+1)::timestamp at time zone 'America/Lima' at time zone 'UTC')
   and (p_seller is null or v.vendedor_id=p_seller)
   and (coalesce(p_search,'')='' or p.nombre ilike '%'||p_search||'%' or p.sku ilike '%'||p_search||'%' or v.id::text=p_search)
 ), visible as (select * from base where p_status='all' or (p_status='active' and not voided) or (p_status='voided' and voided)),
 valid as (select * from base where not voided)
 select jsonb_build_object(
  'summary',jsonb_build_object('total',coalesce((select sum(total) from valid),0),'units',coalesce((select sum(cantidad) from valid),0),
    'records',(select count(*) from valid),'voided',(select count(*) from base where voided),'reconstructed',(select count(*) from valid where source='reconstruida')),
  'count',(select count(*) from visible),'page',p_page,'page_size',p_limit,
  'rows',coalesce((select jsonb_agg(to_jsonb(r)-'local_time' order by r.fecha desc,r.id desc)
   from (select * from visible order by fecha desc,id desc limit p_limit offset (p_page-1)*p_limit) r),'[]'::jsonb),
  'daily',coalesce((select jsonb_agg(to_jsonb(d) order by d.day) from (
   select local_time::date::text as day,sum(total) as total,count(*) as records from valid group by local_time::date) d),'[]'::jsonb),
  'products',coalesce((select jsonb_agg(to_jsonb(p) order by p.total desc) from (
   select producto_id,producto,categoria,sum(cantidad) as units,sum(total) as total from valid group by producto_id,producto,categoria order by sum(total) desc limit 10) p),'[]'::jsonb),
  'hours',coalesce((select jsonb_agg(to_jsonb(h) order by h.hour) from (
   select extract(hour from local_time)::integer as hour,sum(total) as total from valid group by 1) h),'[]'::jsonb),
  'coverage',coalesce((select jsonb_agg(to_jsonb(d) order by d.day) from (
   select g.day::date::text as day,coalesce(v.records,0) as records,coalesce(v.total,0) as total,
    coalesce(v.reconstructed,0) as reconstructed from generate_series(p_from,p_to,interval '1 day') g(day)
   left join (select local_time::date as day,count(*) as records,sum(total) as total,count(*) filter(where source='reconstruida') as reconstructed
    from valid group by 1) v on v.day=g.day::date) d),'[]'::jsonb),
  'catalog',coalesce((select jsonb_agg(jsonb_build_object('id',id,'nombre',nombre,'precio',precio,'activo',activo) order by nombre) from inventario.productos),'[]'::jsonb),
  'range',jsonb_build_object('first',(select (min(fecha) at time zone 'UTC' at time zone 'America/Lima')::date from inventario.ventas),'last',(select (max(fecha) at time zone 'UTC' at time zone 'America/Lima')::date from inventario.ventas)),
  'can_admin',coalesce(a.rol='admin' and a.has_permisos,false)
 ) into result;
 return result;
end $$;
revoke all on function public.stock_studio_sales_report(date,date,integer,text,text,integer,integer) from public,anon;
grant execute on function public.stock_studio_sales_report(date,date,integer,text,text,integer,integer) to authenticated;

create or replace function public.stock_studio_sales_admin(p_action text,p_data jsonb,p_request_id uuid)
returns jsonb language plpgsql security definer set search_path='' as $$
declare a inventario.usuarios; old inventario.ventas; before_data jsonb; after_data jsonb;
 response_data jsonb; prior stock_studio_private.requests; target integer; product integer; qty numeric; price numeric;
 seller integer; stamp timestamp; reason text; reference text; affects boolean; is_void boolean; delta integer; item record;
begin
 a:=stock_studio_private.actor();
 if coalesce(a.rol,'')<>'admin' or not coalesce(a.has_permisos,false) then raise exception 'Esta acción requiere una cuenta Administrador.' using errcode='42501'; end if;
 if p_request_id is null or p_data is null or p_action not in ('create','edit','void','restore') then raise exception 'Solicitud no válida.' using errcode='22023'; end if;
 reason:=trim(p_data->>'reason'); reference:=left(trim(p_data->>'reference'),500);
 if coalesce(reason,'')='' or length(reason)>1000 then raise exception 'Indica el motivo de la corrección.' using errcode='22023'; end if;
 if p_action='create' and coalesce(reference,'')='' then raise exception 'Indica la referencia de la fuente de esta venta antigua.' using errcode='22023'; end if;
 affects:=coalesce((p_data->>'affects_stock')::boolean,false);
 insert into stock_studio_private.requests(user_id,request_id,action,payload) values(a.id,p_request_id,'sales_admin:'||p_action,p_data) on conflict do nothing;
 if not found then
  select * into prior from stock_studio_private.requests where user_id=a.id and request_id=p_request_id;
  if prior.action<>'sales_admin:'||p_action or prior.payload<>p_data then raise exception 'Solicitud reutilizada con otros datos.' using errcode='22023'; end if;
  return prior.result;
 end if;
 target:=nullif(p_data->>'id','')::integer;
 if p_action<>'create' then
  select * into old from inventario.ventas where id=target for update;
  if not found then raise exception 'Venta no encontrada.' using errcode='22023'; end if;
  select coalesce((select voided from stock_studio_private.sale_state where sale_id=target),false) into is_void;
  before_data:=to_jsonb(old)||jsonb_build_object('voided',is_void)||coalesce((select jsonb_build_object('reference',m.reference,'source',m.source) from stock_studio_private.sale_state m where m.sale_id=target),'{}'::jsonb);
  if p_action in ('edit','void') and is_void then raise exception 'La venta está anulada; restaura primero el registro.' using errcode='22023'; end if;
  if p_action='restore' and not is_void then raise exception 'La venta ya está vigente.' using errcode='22023'; end if;
 end if;
 if p_action in ('create','edit') then
  product:=(p_data->>'producto_id')::integer;
  qty:=stock_studio_private.number_value(p_data,'cantidad',false);price:=stock_studio_private.number_value(p_data,'precio');
  if qty<>floor(qty) or qty>2147483647 then raise exception 'La cantidad debe ser un entero positivo.' using errcode='22023'; end if;
  stamp:=(p_data->>'fecha')::timestamp at time zone 'America/Lima' at time zone 'UTC';
  if stamp is null or stamp>(now() at time zone 'UTC')+interval '5 minutes' then raise exception 'La fecha no puede estar en el futuro.' using errcode='22023'; end if;
  if not exists(select 1 from inventario.productos where id=product) then raise exception 'Producto no encontrado.' using errcode='22023'; end if;
  seller:=nullif(p_data->>'vendedor_id','')::integer;
  if seller is not null and not exists(select 1 from inventario.vendedores where id=seller) then raise exception 'Vendedor no encontrado.' using errcode='22023'; end if;
  if p_action='edit' and old.lote_id is not null and old.producto_id<>product then raise exception 'Conserva el producto de una venta vinculada a un lote.' using errcode='22023'; end if;
 end if;
 if affects then
  -- Lock all involved products in a stable order, then apply only the net difference.
  perform id from inventario.productos where id in (old.producto_id,product) order by id for update;
  for item in select p.id,p.cantidad_stock from inventario.productos p where p.id in (old.producto_id,product) order by p.id loop
   delta:=0;
   if p_action in ('edit','void') and item.id=old.producto_id then delta:=delta+old.cantidad; end if;
   if p_action in ('create','edit') and item.id=product then delta:=delta-qty; end if;
   if p_action='restore' and item.id=old.producto_id then delta:=delta-old.cantidad; end if;
   if item.cantidad_stock+delta<0 then raise exception 'Stock insuficiente para aplicar esta corrección al inventario actual.' using errcode='22023'; end if;
   if delta<>0 then
    update inventario.productos set cantidad_stock=cantidad_stock+delta,fecha_actualizacion=now() at time zone 'UTC' where id=item.id;
    insert into inventario.movimientos_stock(producto_id,usuario_id,tipo,cantidad,motivo,observaciones,fecha)
     values(item.id,a.id,'correccion',delta,'Corrección administrativa de venta',left(reason,5000),now() at time zone 'UTC');
   end if;
  end loop;
 end if;
 if p_action='create' then
  insert into inventario.ventas(producto_id,usuario_id,vendedor_id,cantidad,precio_unitario,total,motivo,observaciones,fecha)
   values(product,a.id,seller,qty,price,qty*price,'Reconstrucción histórica',left(p_data->>'observaciones',5000),stamp) returning id into target;
  insert into stock_studio_private.sale_state(sale_id,source,reference) values(target,'reconstruida',reference);
 elsif p_action='edit' then
  update inventario.ventas set producto_id=product,vendedor_id=seller,cantidad=qty,precio_unitario=price,total=qty*price,
   observaciones=left(p_data->>'observaciones',5000),fecha=stamp where id=target;
  insert into stock_studio_private.sale_state(sale_id,reference) values(target,reference)
   on conflict(sale_id) do update set reference=excluded.reference,updated_at=now();
 else
  insert into stock_studio_private.sale_state(sale_id,voided) values(target,p_action='void')
   on conflict(sale_id) do update set voided=excluded.voided,updated_at=now();
 end if;
 select to_jsonb(v)||jsonb_build_object('voided',coalesce(m.voided,false),'reference',m.reference,'source',m.source) into after_data from inventario.ventas v
  left join stock_studio_private.sale_state m on m.sale_id=v.id where v.id=target;
 insert into stock_studio_private.audit_log(sale_id,actor_id,action,reason,before_value,after_value,affects_stock,request_id)
  values(target,a.id,p_action,reason,before_data,after_data,affects,p_request_id);
 response_data:=jsonb_build_object('ok',true,'id',target);
 update stock_studio_private.requests set result=response_data where user_id=a.id and request_id=p_request_id;
 return response_data;
end $$;
revoke all on function public.stock_studio_sales_admin(text,jsonb,uuid) from public,anon;
grant execute on function public.stock_studio_sales_admin(text,jsonb,uuid) to authenticated;

create or replace function public.stock_studio_sales_audit(p_sale integer)
returns jsonb language plpgsql security definer set search_path='' stable as $$
declare a inventario.usuarios; result jsonb;
begin
 a:=stock_studio_private.actor();
 if coalesce(a.rol,'')<>'admin' or not coalesce(a.has_permisos,false) then raise exception 'Solo Administrador.' using errcode='42501'; end if;
 select coalesce(jsonb_agg(jsonb_build_object('id',l.id,'action',l.action,'reason',l.reason,'actor',u.nombre_completo,
 'before',l.before_value,'after',l.after_value,'affects_stock',l.affects_stock,'fecha',l.created_at) order by l.id desc),'[]'::jsonb)
 into result from stock_studio_private.audit_log l join inventario.usuarios u on u.id=l.actor_id where l.sale_id=p_sale;
 return result;
end $$;
revoke all on function public.stock_studio_sales_audit(integer) from public,anon;
grant execute on function public.stock_studio_sales_audit(integer) to authenticated;

-- Retain the first implementation as an internal helper; filter reversibly voided
-- records from the existing dashboard as well as the new full-history report.
do $$ begin
 if to_regprocedure('stock_studio_private.data_v1()') is null then
  alter function public.stock_studio_data() set schema stock_studio_private;
  alter function stock_studio_private.stock_studio_data() rename to data_v1;
 end if;
end $$;
revoke all on function stock_studio_private.data_v1() from public,anon,authenticated;
create or replace function public.stock_studio_data()
returns jsonb language plpgsql security definer set search_path='' stable as $$
declare result jsonb; daily jsonb; sales jsonb;
begin
 result:=stock_studio_private.data_v1();
 select coalesce(jsonb_agg(s),'[]'::jsonb) into sales from jsonb_array_elements(result->'sales') s
  where not exists(select 1 from stock_studio_private.sale_state m where m.sale_id=(s->>'id')::integer and m.voided);
 select coalesce(jsonb_agg(jsonb_build_object('day',g.day::date::text,'total',coalesce(v.total,0)) order by g.day),'[]'::jsonb)
 into daily from generate_series((now() at time zone 'America/Lima')::date-6,(now() at time zone 'America/Lima')::date,interval '1 day') g(day)
 left join (select (v.fecha at time zone 'UTC' at time zone 'America/Lima')::date as day,sum(v.total) as total from inventario.ventas v
  where not exists(select 1 from stock_studio_private.sale_state m where m.sale_id=v.id and m.voided)
  and v.fecha>=((now() at time zone 'America/Lima')::date-6)::timestamp at time zone 'America/Lima' at time zone 'UTC' group by 1) v on v.day=g.day::date;
 return result||jsonb_build_object('sales',sales,'daily_sales',daily);
end $$;
revoke all on function public.stock_studio_data() from public,anon;
grant execute on function public.stock_studio_data() to authenticated;
notify pgrst,'reload schema';
