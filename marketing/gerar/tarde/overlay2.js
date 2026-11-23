// Renderiza os textos animados como sequência de PNG transparentes (30 fps)
const { chromium } = require('playwright');
const fs = require('fs');
const [,, mode, out] = process.argv;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file:///home/user/Clausa/marketing/tarde-founder-v2.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  fs.mkdirSync(out, { recursive: true });
  if (mode === 'preview') {
    for (const t of process.argv.slice(4).map(Number)) { await p.evaluate(t => render(t), t); await p.screenshot({ path: `${out}/o_${t}.png`, omitBackground: true }); }
  } else {
    const D = await p.evaluate(() => DUR), N = Math.ceil(D * 30);
    for (let i = 0; i < N; i++) {
      await p.evaluate(t => render(t), i / 30);
      await p.screenshot({ path: `${out}/o${String(i).padStart(4, '0')}.png`, omitBackground: true });
    }
    console.log('quadros:', N);
  }
  await b.close();
})();
