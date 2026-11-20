// Headless Chromium for the renderers: Playwright's own browser, else the installed Google Chrome.
// File access between file:// URLs lets a canvas read back the images it draws.
const { chromium } = require('playwright');
const ARGS = { args: ['--allow-file-access-from-files', '--font-render-hinting=none'] };
async function launch() {
  try { return await chromium.launch(ARGS); }
  catch (e) {
    try { return await chromium.launch({ ...ARGS, channel: 'chrome' }); }
    catch { throw new Error('No browser for rendering. Run `studio setup` (it installs Playwright\'s Chromium), or install Google Chrome.\n' + e.message); }
  }
}
module.exports = { launch };
