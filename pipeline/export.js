// Exporta cada .slide do carousel.html em PNG 1080x1350.
// Uso: node pipeline/export.js [carousel.html] [out_dir]
// Requer: npm i playwright  &&  npx playwright install chromium
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ROOT = path.dirname(__dirname);
const HTML = process.argv[2] || path.join(ROOT, 'carousel.html');
const OUT = process.argv[3] || path.join(ROOT, 'slides');

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  // --no-sandbox + --disable-* = necessário pra chromium subir em cloud/container Linux (root, sem shm)
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--force-color-profile=srgb', '--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1400 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(HTML), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.querySelector('.stage') && document.querySelector('.stage').classList.remove('preview'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1500);
  const ok = await page.evaluate(() => document.fonts.check('900 48px "Barlow Condensed"'));
  if (!ok) await page.waitForTimeout(3000);

  const slides = page.locator('.slide');
  const n = await slides.count();
  for (let i = 0; i < n; i++) {
    const s = slides.nth(i);
    await s.scrollIntoViewIfNeeded();
    await page.waitForTimeout(250);
    const tmp = path.join(OUT, `_s_${i + 1}.png`);
    await s.screenshot({ path: tmp });
    console.log('shot', i + 1);
  }
  await browser.close();

  // normaliza pra 1080x1350 com sharp se disponível, senão deixa 2x
  try {
    const sharp = require('sharp');
    for (let i = 1; i <= n; i++) {
      const src = path.join(OUT, `_s_${i}.png`);
      const dst = path.join(OUT, `slide_${String(i).padStart(2, '0')}.png`);
      await sharp(src).resize(1080, 1350).png().toFile(dst);
      fs.unlinkSync(src);
    }
    console.log('resized to 1080x1350');
  } catch (e) {
    for (let i = 1; i <= n; i++) {
      fs.renameSync(path.join(OUT, `_s_${i}.png`), path.join(OUT, `slide_${String(i).padStart(2, '0')}.png`));
    }
    console.log('kept 2x (sharp ausente)');
  }
  console.log('DONE', OUT);
})();
