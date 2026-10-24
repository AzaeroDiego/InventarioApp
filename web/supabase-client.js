'use strict';
// Only the public project key is used here. Database credentials never reach the browser.
window.StockSupabase = (() => {
  const config=window.STOCK_CONFIG||{};
  const base=config.SUPABASE_URL?.replace(/\/$/,'');
  let session;
  try {session=JSON.parse(sessionStorage.getItem('stock-supabase-session')||'null')} catch {session=null}
  let refreshing;
  function save(data){session={access_token:data.access_token,refresh_token:data.refresh_token,expires_at:data.expires_at||Math.floor(Date.now()/1000)+data.expires_in};sessionStorage.setItem('stock-supabase-session',JSON.stringify(session));sessionStorage.setItem('stock-token',session.access_token);return session}
  function clear(){session=null;sessionStorage.removeItem('stock-supabase-session');sessionStorage.removeItem('stock-token')}
  async function request(path,body,authenticated=false,method='POST'){
    if(!base||!config.SUPABASE_PUBLISHABLE_KEY)throw Error('Falta configurar el proyecto de Supabase.');
    let response;
    try {response=await fetch(base+path,{method,headers:{apikey:config.SUPABASE_PUBLISHABLE_KEY,'Content-Type':'application/json',...(authenticated&&session?{Authorization:`Bearer ${session.access_token}`}:{})},...(body?{body:JSON.stringify(body)}:{}),credentials:'omit',signal:AbortSignal.timeout(18000)})}
    catch {const error=Error('No se pudo confirmar la respuesta. Revisa la conexión; puedes repetir los mismos datos sin duplicar la operación.');error.uncertain=true;throw error}
    const data=await response.json().catch(()=>({}));
    if(!response.ok){const message=data.message||data.msg||data.error_description||data.error||'';
      if(response.status===401&&authenticated){clear();throw Error('Tu sesión terminó. Vuelve a iniciar sesión.')}
      if(message.includes('Invalid login credentials'))throw Error('Correo o contraseña incorrectos. Para el primer acceso puedes usar un enlace por correo.');
      if(message.includes('Email not confirmed'))throw Error('Confirma primero tu correo desde el mensaje de Supabase.');
      if(message.includes('stock_studio_')&&(data.code==='PGRST202'||response.status===404))throw Error('La conexión está lista, pero falta instalar las funciones de Stock Studio en Supabase.');
      throw Error(message||'No se pudo completar la operación.');
    }
    return data;
  }
  async function ensureSession(){
    if(!session)throw Error('Inicia sesión para acceder al inventario.');
    if(session.expires_at<=Math.floor(Date.now()/1000)+60){
      refreshing ||= request('/auth/v1/token?grant_type=refresh_token',{refresh_token:session.refresh_token}).then(save).catch(e=>{clear();throw e}).finally(()=>{refreshing=null});
      await refreshing;
    }
  }
  async function write(action,data,rpc='stock_studio_write'){
    await ensureSession();
    let pending;try{pending=JSON.parse(sessionStorage.getItem('stock-pending-write')||'null')}catch{}
    const fingerprint=JSON.stringify({rpc,action,data});
    if(!pending||pending.fingerprint!==fingerprint){pending={fingerprint,key:crypto.randomUUID()};sessionStorage.setItem('stock-pending-write',JSON.stringify(pending))}
    try{const result=await request('/rest/v1/rpc/'+rpc,{p_action:action,p_data:data,p_request_id:pending.key},true);sessionStorage.removeItem('stock-pending-write');return result}
    catch(error){if(!error.uncertain)sessionStorage.removeItem('stock-pending-write');throw error}
  }
  return {
    enabled:config.PROVIDER==='supabase',
    hasSession:()=>Boolean(session),
    clear,
    async login(email,password){return save(await request('/auth/v1/token?grant_type=password',{email,password}))},
    async sendLink(email){return request('/auth/v1/otp?redirect_to='+encodeURIComponent(location.origin+location.pathname),{email,create_user:true})},
    async verify(email,code){return save(await request('/auth/v1/verify',{email,token:code,type:'email'}))},
    async acceptLink(){const values=new URLSearchParams(location.hash.slice(1));if(values.has('access_token')&&values.has('refresh_token')){save({access_token:values.get('access_token'),refresh_token:values.get('refresh_token'),expires_in:Number(values.get('expires_in')||3600)});history.replaceState(null,'',location.pathname+location.search);return true}return false},
    async logout(){try{if(session)await request('/auth/v1/logout',{},true)}finally{clear()}},
    async api(path,body){
      if(path==='login'){const s=await this.login(body.email,body.password);return {token:s.access_token}}
      await ensureSession();
      if(path==='data')return request('/rest/v1/rpc/stock_studio_data',{},true);
      if(path==='sales-report')return request('/rest/v1/rpc/stock_studio_sales_report',body,true);
      if(path==='sales-audit')return request('/rest/v1/rpc/stock_studio_sales_audit',{p_sale:body.id},true);
      if(path.startsWith('sales-admin/'))return write(path.slice(12),body,'stock_studio_sales_admin');
      if(path==='products')return write('product_save',body);
      if(path==='movements')return write('movement',body);
      if(path.startsWith('action/'))return write(path.slice(7),body);
      throw Error('Esta operación no está disponible en la conexión directa.');
    }
  };
})();
