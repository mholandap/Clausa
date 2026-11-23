const { chromium } = require('playwright');
const path = require('path');
const [,, mode, outDir, fpsArg] = process.argv;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(process.env.PAGE || path.join(__dirname, '..', 'anuncio.html')) + '?frame', { waitUntil: 'networkidle' });
  await p.evaluate(async () => { await document.fonts.ready; init(); });
  const fonts = await p.evaluate(() => [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family))]);
  console.log('fonts:', fonts.join(', '));
  if (mode === 'preview') {
    for (const t of process.argv.slice(5).map(Number)) { await p.evaluate(t => render(t), t); await p.screenshot({ path: `${outDir}/p_${t}.png` }); }
  } else {
    const FPS = Number(fpsArg) || 60, D = await p.evaluate(() => DUR), N = Math.round(D * FPS);
    for (let i = Number(process.env.START||0); i < N; i++) {
      await p.evaluate(t => render(t), i / FPS);
      await p.screenshot({ path: `${outDir}/f${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 });
      if (i % 180 === 0) console.log('frame', i, '/', N);
    }
  }
  await b.close();
})();
