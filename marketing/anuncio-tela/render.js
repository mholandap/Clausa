// Renderiza uma página com window.render(t) quadro a quadro.
// Uso: node render.js pagina.html pasta fps [preview t1 t2 ...]
const { chromium } = require('playwright'); const fs=require('fs'), path=require('path');
const [,, page, out, fps, modo, ...ts] = process.argv;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{width:1920,height:1080}, deviceScaleFactor:1 });
  await p.goto('file://'+path.resolve(page), { waitUntil:'networkidle' });
  await p.evaluate(async()=>{await document.fonts.load('900 100px "Inter Tight"');await document.fonts.load('700 40px Inter');await document.fonts.ready});
  fs.mkdirSync(out,{recursive:true});
  const dur=await p.evaluate(()=>window.DUR); const F=+fps;
  const lista = modo==='preview' ? ts.map(Number) : Array.from({length:Math.round(dur*F)},(_,i)=>i/F);
  const t0=Date.now();
  for (let i=0;i<lista.length;i++){ const t=lista[i]; await p.evaluate(t=>render(t),t);
    await p.screenshot({ path: modo==='preview'?`${out}/p_${String(t).replace('.','_')}.png`:`${out}/f${String(i).padStart(5,'0')}.jpg`, type: modo==='preview'?'png':'jpeg', ...(modo==='preview'?{}:{quality:93}) });
    if(modo!=='preview'&&i%120===0) console.log(`quadro ${i}/${lista.length} ${(i/((Date.now()-t0)/1000)).toFixed(1)} q/s`); }
  await b.close();
})();
