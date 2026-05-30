import puppeteer from 'puppeteer';
import { spawn } from 'child_process';

const capture = async () => {
  // Start server
  const server = spawn('npm', ['run', 'preview'], { stdio: 'ignore' });
  
  // Wait for server to start
  await new Promise(r => setTimeout(r, 3000));
  
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  try {
    await page.setViewport({ width: 1280, height: 800 });
    
    // Capture Home
    await page.goto('http://localhost:4173');
    await page.waitForNetworkIdle();
    await page.screenshot({ path: '../../PROJECT_GROWTH_AUDIT_HOME.png' });
    
    // Capture Dives
    await page.goto('http://localhost:4173/dives');
    await page.waitForNetworkIdle();
    await page.screenshot({ path: '../../PROJECT_GROWTH_AUDIT_DIVES.png' });
    
    console.log("Screenshots captured successfully.");
  } catch(e) {
    console.error("Screenshot error:", e);
  } finally {
    await browser.close();
    server.kill();
  }
};

capture();
