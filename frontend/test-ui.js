import puppeteer from 'puppeteer';

async function testUI() {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
    args: ['--start-maximized']
  });

  try {
    const page = await browser.newPage();
    
    // Listen for console messages
    page.on('console', (message) => {
      console.log(`📢 Console (${message.type()}):`, message.text());
    });
    
    // Listen for page errors
    page.on('pageerror', (error) => {
      console.log('❌ Page error:', error.message);
    });
    
    console.log('🌐 Navigating to frontend...');
    await page.goto('http://localhost:5175', { waitUntil: 'networkidle2' });
    
    console.log('📷 Taking screenshot...');
    await page.screenshot({ 
      path: 'ui-test.png', 
      fullPage: true 
    });
    
    console.log('🔍 Checking page content...');
    
    // Get page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for React errors
    const errors = await page.evaluate(() => {
      return window.console?.errors || [];
    });
    
    // Get all text content
    const bodyText = await page.evaluate(() => document.body.textContent);
    console.log('Page contains text:', bodyText.substring(0, 200) + '...');
    
    // Check if components are rendered
    const hasCards = await page.$('.rounded-lg');
    const hasButtons = await page.$('button');
    const hasInputs = await page.$('input');
    
    console.log('✅ Cards found:', !!hasCards);
    console.log('✅ Buttons found:', !!hasButtons);
    console.log('✅ Inputs found:', !!hasInputs);
    
    // Check for any error messages
    const errorElements = await page.$$('.text-red-600');
    console.log('❌ Error elements:', errorElements.length);
    
    // Look for specific text
    const hasTitle = await page.$eval('body', el => 
      el.textContent.includes('CHC Location Geocoder')
    ).catch(() => false);
    
    console.log('🏷️  Title found:', hasTitle);
    
    // Check console errors
    page.on('console', (message) => {
      if (message.type() === 'error') {
        console.log('❌ Console error:', message.text());
      }
    });
    
    // Wait for any dynamic content
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    console.log('📷 Taking final screenshot...');
    await page.screenshot({ 
      path: 'ui-final.png', 
      fullPage: true 
    });
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

testUI();