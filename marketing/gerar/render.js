const { chromium } = require('playwright');
const path = require('path');
const [,, mode, outDir] = process.argv;  // mode: "preview" | "full"
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, '..', 'anuncio.html') + '?frame', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const fonts = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style));
  console.log('fonts:', [...new Set(fonts)].join(', '));
  const times = mode === 'preview' ? [1.2, 2.4, 5.0, 8.0, 11.6, 14.6, 17.5] : null;
  if (times) {
    for (const t of times) { await p.evaluate(t => render(t), t); await p.screenshot({ path: `${outDir}/p_${t}.png` }); }
  } else {
    const FPS = 30, N = Math.round(18 * FPS);
    for (let i = 0; i < N; i++) {
      await p.evaluate(t => render(t), i / FPS);
      await p.screenshot({ path: `${outDir}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 });
      if (i % 90 === 0) console.log('frame', i, '/', N);
    }
  }
  await b.close();
})();
