/**
 * Patchright Stealth Browser Grid Launcher
 */

const { chromium } = require('patchright');
const { spawn } = require('child_process');

async function launchBrowser() {
  console.log('🚀 Starting Patchright stealth browser grid...');

  // Start socat to forward 0.0.0.0:9222 to 127.0.0.1:9224
  // This bypasses Chrome's strict IP checking by making the connection
  // look like it's coming from localhost.
  const socat = spawn('socat', ['tcp-listen:9222,bind=0.0.0.0,fork,reuseaddr', 'tcp:127.0.0.1:9224']);
  socat.stderr.on('data', (data) => console.error(`socat err: ${data}`));

  const browser = await chromium.launch({
    headless: false,
    args: [
      '--remote-debugging-port=9224',
      '--remote-debugging-address=127.0.0.1',
      '--remote-allow-origins=*',
      '--disable-blink-features=AutomationControlled',
      '--disable-infobars',
      '--disable-extensions',
      '--disable-gpu',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-background-networking',
      '--disable-default-apps',
      '--disable-sync',
      '--disable-translate',
      '--window-size=1920,1080',
      '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
  });

  console.log('✅ Browser launched successfully on port 9224');
  
  const http = require('http');
  const server = http.createServer(async (req, res) => {
    if (req.url === '/json/version') {
      try {
        const fetch = require('node-fetch');
        const resp = await fetch('http://127.0.0.1:9224/json/version');
        const text = await resp.text();
        
        // Rewrite the websocket URL to point to the external 9222 port instead of internal 9224
        const data = JSON.parse(text);
        if (data.webSocketDebuggerUrl) {
           data.webSocketDebuggerUrl = data.webSocketDebuggerUrl.replace(':9224', ':9222');
        }
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(data));
      } catch (err) {
        res.writeHead(500);
        res.end(err.toString());
      }
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  
  server.listen(9223, '0.0.0.0', () => {
    console.log('📡 Proxy endpoint available at: http://0.0.0.0:9223/json/version');
  });

  browser.on('disconnected', () => {
    console.log('⚠️ Browser disconnected, restarting...');
    server.close();
    socat.kill();
    launchBrowser();
  });

  process.on('SIGTERM', async () => {
    console.log('🛑 Received SIGTERM, closing browser...');
    await browser.close();
    server.close();
    socat.kill();
    process.exit(0);
  });
}

launchBrowser().catch(console.error);
