// Renderiza o estúdio quadro a quadro (30 fps) a partir de uma linha do tempo JSON.
// Uso: node render.js timeline.json pasta_saida [preview t1 t2 ...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [,, tlPath, out, modo, ...tempos] = process.argv;
(async () => {
  const TL = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.addInitScript(tl => { window.TL = tl; }, TL);
  await p.goto('file://' + path.join(__dirname, 'estudio.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  fs.mkdirSync(out, { recursive: true });
  const ts = modo === 'preview' ? tempos.map(Number) : null;
  const N = ts ? ts.length : Math.ceil(TL.dur * 30);
  for (let i = 0; i < N; i++) {
    const t = ts ? ts[i] : i / 30;
    await p.evaluate(t => render(t), t);
    await p.screenshot({ path: ts ? `${out}/p_${t}.png` : `${out}/f${String(i).padStart(5, '0')}.jpg`, type: ts ? 'png' : 'jpeg', ...(ts ? {} : { quality: 92 }) });
    if (!ts && i % 150 === 0) console.log(`quadro ${i}/${N}`);
  }
  await b.close();
})();
