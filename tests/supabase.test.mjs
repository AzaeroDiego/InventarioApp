// Runs exclusively in an in-memory PostgreSQL WASM instance. No network or real credentials.
import { PGlite } from '@electric-sql/pglite';
import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
const db=new PGlite();
let checks=0;
const check=(condition)=>{assert.ok(condition);checks++};
const one=async(sql,params=[])=> (await db.query(sql,params)).rows[0];
const write=async(action,data,key=randomUUID())=>(await one('select public.stock_studio_write($1,$2::jsonb,$3::uuid) as result',[action,JSON.stringify(data),key])).result;
const read=async()=>(await one('select public.stock_studio_data() as result')).result;
async function fails(fn,pattern){await assert.rejects(fn,pattern);checks++}
try{
  await db.exec(await readFile(new URL('./postgres_fixture.sql',import.meta.url),'utf8'));
  await db.exec(await readFile(new URL('../supabase/migrations/20261024_stock_studio.sql',import.meta.url),'utf8'));
  await fails(read,/acceso activo/);
  await db.exec(`insert into inventario.usuarios(id,nombre_completo,email,password_hash,has_permisos,rol,activo) values
    (1,'Owner','owner@example.invalid','disabled',true,'admin',true),
    (2,'Reader','reader@example.invalid','disabled',false,'vendedor',true);
    insert into auth.users values('00000000-0000-0000-0000-000000000001','owner@example.invalid',now()),
    ('00000000-0000-0000-0000-000000000002','reader@example.invalid',now()),
    ('00000000-0000-0000-0000-000000000003','stranger@example.invalid',now());`);
  await db.query("select set_config('request.jwt.claim.sub',$1,false)",['00000000-0000-0000-0000-000000000001']);
  const category=(await write('category_save',{nombre:'Test'})).id;
  const body={nombre:'Product',sku:'TEST',categoria_id:category,precio:'10',minimo:'2',se_vende:true};
  const key=randomUUID(),created=await write('product_save',body,key),product=created.id;
  check((await write('product_save',body,key)).id===product);
  check((await one('select count(*)::int as n from inventario.productos')).n===1);
  await fails(()=>write('product_save',{...body,sku:'OTHER'},key),/otros datos/);
  await fails(()=>write('product_save',body),/Ya existe/);
  await write('movement',{producto_id:product,tipo:'entrada',cantidad:'5'});
  await write('movement',{producto_id:product,tipo:'venta',cantidad:'2',precio:'12'});
  check((await one('select cantidad_stock from inventario.productos where id=$1',[product])).cantidad_stock===3);
  check(Number((await one('select total from inventario.ventas')).total)===24);
  await fails(()=>write('movement',{producto_id:product,tipo:'venta',cantidad:'4',precio:'12'}),/Stock insuficiente/);
  for(const cantidad of ['-1','1.5','NaN','Infinity','0'])await fails(()=>write('movement',{producto_id:product,tipo:'entrada',cantidad}),/Revisa|entero/);
  await write('movement',{producto_id:product,tipo:'ajuste',cantidad:'0',motivo:'Physical count'});
  check((await one('select cantidad_stock from inventario.productos where id=$1',[product])).cantidad_stock===0);
  await write('product_save',{...body,id:product,precio:'15',nombre:'Updated'});
  check(Number((await one('select precio from inventario.productos where id=$1',[product])).precio)===15);
  const ingredient=(await write('product_save',{...body,nombre:'Ingredient',sku:'ING',se_vende:false})).id;
  await write('movement',{producto_id:ingredient,tipo:'entrada',cantidad:'20'});
  await fails(()=>write('lot_create',{producto_id:product,cantidad:'2',ingredientes:[{producto_id:ingredient,cantidad:'21'}]}),/stock insuficiente/);
  await write('lot_create',{producto_id:product,cantidad:'4',ingredientes:[{producto_id:ingredient,cantidad:'3'},{producto_id:ingredient,cantidad:'2'}]});
  check((await one('select cantidad_stock from inventario.productos where id=$1',[ingredient])).cantidad_stock===15);
  check((await one('select cantidad_stock from inventario.productos where id=$1',[product])).cantidad_stock===4);
  const stockBefore=JSON.stringify((await db.query('select id,cantidad_stock from inventario.productos order by id')).rows);
  await write('bar_close',{responsable_id:1,fecha:'2026-10-24',hora:'23:00',monto_entregado:'50',detalles:[{producto:'Test drink',stock_inicial:'10',stock_final:'6',precio:'12'}]});
  check(Number((await one('select diferencia_caja from inventario.controles_barra')).diferencia_caja)===2);
  check(JSON.stringify((await db.query('select id,cantidad_stock from inventario.productos order by id')).rows)===stockBefore);
  await fails(()=>write('bar_close',{responsable_id:1,fecha:'2026-10-24',monto_entregado:'0',detalles:[{producto:'Test',stock_inicial:'1',stock_final:'2',precio:'1'}]}),/Conteo/);
  await write('seller_save',{nombre:'Seller',comision_porcentaje:'10'});
  const data=await read();
  check(data.products.length===2&&data.categories.length===1&&data.sellers.length===1&&data.lots.length===1&&data.bar_controls.length===1);
  check(!JSON.stringify(data).includes('password_hash'));
  await fails(()=>write('user_access',{id:1,write:false,activo:false,rol:'vendedor'}),/propio acceso/);
  await db.query("select set_config('request.jwt.claim.sub',$1,false)",['00000000-0000-0000-0000-000000000002']);
  check((await read()).user.write===false);
  await fails(()=>write('movement',{producto_id:product,tipo:'entrada',cantidad:'1'}),/solo lectura/);
  await db.query("select set_config('request.jwt.claim.sub',$1,false)",['00000000-0000-0000-0000-000000000003']);
  await fails(read,/acceso activo/);
  check((await one("select has_function_privilege('anon','public.stock_studio_data()','EXECUTE') as allowed")).allowed===false);
  check((await one("select has_function_privilege('anon','public.stock_studio_write(text,jsonb,uuid)','EXECUTE') as allowed")).allowed===false);
  console.log(`PASS: ${checks} isolated PostgreSQL checks; no production connection.`);
}catch(error){console.error('FAIL:',error.message,error.where||'');process.exitCode=1}finally{await db.close()}
