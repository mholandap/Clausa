// Renderiza uma camada (behind/front) dos textos do v3 como PNG transparentes a 30 fps
const { chromium } = require('playwright');
const fs = require('fs');
const [,, layer, mode, out] = process.argv;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file:///home/user/Clausa/marketing/tarde-founder-v3.html?layer=' + layer, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  fs.mkdirSync(out, { recursive: true });
  const ts = mode === 'preview' ? process.argv.slice(5).map(Number) : null;
  const N = ts ? ts.length : Math.ceil((await p.evaluate(() => DUR)) * 30);
  for (let i = 0; i < N; i++) {
    const t = ts ? ts[i] : i / 30;
    await p.evaluate(t => render(t), t);
    await p.screenshot({ path: ts ? `${out}/${layer}_${t}.png` : `${out}/o${String(i).padStart(4, '0')}.png`, omitBackground: true });
  }
  console.log(layer, 'quadros:', N);
  await b.close();
})();
