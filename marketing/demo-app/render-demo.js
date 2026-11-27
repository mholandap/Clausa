// Renderiza o vídeo de demonstração quadro a quadro, com o app de verdade num "celular".
// Precisa do site servido em http://localhost:8766 (python3 -m http.server 8766 na raiz do repositório).
// Uso: node render-demo.js pasta fps [preview t1 t2 ...]
const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
const [,,out,fps,modo,...ts]=process.argv;
// "Supabase" de mentira: um usuário logado num escritório fictício (nada real aparece no vídeo)
const MOCK=`window.supabase={createClient:()=>{
 const dados={membros:[{escritorio_id:'e1',user_id:'u1',email:'voce@escritoriomodelo.adv.br',papel:'admin'},{escritorio_id:'e1',user_id:'u2',email:'ana@escritoriomodelo.adv.br',papel:'membro'},{escritorio_id:'e1',user_id:'u3',email:'bruno@escritoriomodelo.adv.br',papel:'membro'},{escritorio_id:'e1',user_id:'u4',email:'carla@escritoriomodelo.adv.br',papel:'membro'}],
  escritorios:{id:'e1',nome:'Escritório Modelo',convite:'5f2c9a71b04e4d8f9c3a6e21d7b8f0aa'},escritorio_regras:null,contracts:[]};
 const q=t=>{let one=false;const b={select(){return b},order(){return b},eq(){return b},maybeSingle(){one=true;return b},single(){one=true;return b},upsert(){return b},delete(){return b},
  then(ok,er){const d=dados[t];return Promise.resolve({data:one?(Array.isArray(d)?d[0]:d):(Array.isArray(d)?d:[]),error:null}).then(ok,er)}};return b};
 return {auth:{getSession:async()=>({data:{session:{user:{id:'u1',email:'voce@escritoriomodelo.adv.br',user_metadata:{nome:'Você'}},access_token:'t'}}}),signOut:async()=>({})},from:q,rpc:async()=>({data:null})}}};`;
(async()=>{
  const b=await chromium.launch();const c=await b.newContext({viewport:{width:1080,height:1920},deviceScaleFactor:1,reducedMotion:'reduce'});
  await c.route('**/supabase.js',r=>r.fulfill({contentType:'text/javascript',body:MOCK}));
  await c.addInitScript(()=>{try{if(!sessionStorage.getItem('ok')){localStorage.clear();sessionStorage.setItem('ok','1')}}catch(e){}});
  const p=await c.newPage();
  await p.goto('http://localhost:8766/marketing/demo-app/demo.html',{waitUntil:'networkidle'});
  await p.evaluate(async t=>{window.CONTRATO=t;await document.fonts.ready;await window.pronto},fs.readFileSync(path.join(__dirname,'contrato-demo.txt'),'utf8'));
  fs.mkdirSync(out,{recursive:true});
  const dur=await p.evaluate(()=>window.DUR),F=+fps;
  const lista=modo==='preview'?ts.map(Number):Array.from({length:Math.round(dur*F)},(_,i)=>i/F);
  const t0=Date.now();
  for(let i=0;i<lista.length;i++){const t=lista[i];await p.evaluate(t=>render(t),t);
    await p.screenshot({path:modo==='preview'?`${out}/p_${String(t).replace('.','_')}.jpg`:`${out}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});
    if(modo!=='preview'&&i%240===0)console.log(`quadro ${i}/${lista.length} ${(i/((Date.now()-t0)/1000)).toFixed(1)} q/s`)}
  await b.close()})();
