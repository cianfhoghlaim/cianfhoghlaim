/**
 * Patchright Stealth Browser Grid Launcher
 *
 * Launches a Chromium browser with stealth patches and exposes
 * Chrome DevTools Protocol (CDP) on port 9222 for remote control.
 *
 * Features:
 * - Binary-patched navigator.webdriver = false
 * - Stripped Runtime.enable CDP command
 * - Isolated execution contexts
 * - Human-like fingerprints
 */

const { chromium } = require('patchright');

async function launchBrowser() {
  console.log('🚀 Starting Patchright stealth browser grid...');

  const browser = await chromium.launch({
    headless: false, // Use headed mode for better anti-detection
    args: [
      // CDP debugging
      '--remote-debugging-port=9222',
      '--remote-debugging-address=0.0.0.0',

      // Stealth flags
      '--disable-blink-features=AutomationControlled',
      '--disable-infobars',
      '--disable-extensions',

      // Performance
      '--disable-gpu',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',

      // Memory optimization
      '--disable-background-networking',
      '--disable-default-apps',
      '--disable-sync',
      '--disable-translate',

      // Window size
      '--window-size=1920,1080',

      // User agent (randomized at runtime)
      '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
  });

  console.log('✅ Browser launched successfully');
  console.log('📡 CDP endpoint available at: ws://0.0.0.0:9222');

  // Keep browser alive
  browser.on('disconnected', () => {
    console.log('⚠️ Browser disconnected, restarting...');
    launchBrowser();
  });

  // Graceful shutdown
  process.on('SIGTERM', async () => {
    console.log('🛑 Received SIGTERM, closing browser...');
    await browser.close();
    process.exit(0);
  });

  process.on('SIGINT', async () => {
    console.log('🛑 Received SIGINT, closing browser...');
    await browser.close();
    process.exit(0);
  });
}

launchBrowser().catch(console.error);
