import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dir = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dir, '../public-astro/thumbs');
mkdirSync(OUT, { recursive: true });

const BASE = 'https://resume.borck.dev';

const formats = [
  { id: 'pdf',      url: `${BASE}/output/cv-michael-borck.html`,  delay: 1000 },
  { id: 'html',     url: `${BASE}/output/cv-michael-borck.html`,  delay: 1000, scrollY: 0 },
  { id: 'quest',    url: `${BASE}/creative/quest/`,               delay: 2000 },
  { id: 'terminal', url: `${BASE}/creative/terminal/`,            delay: 2000 },
  { id: 'magazine', url: `${BASE}/creative/magazine/`,            delay: 2000 },
  { id: 'api-docs', url: `${BASE}/creative/api/`,                 delay: 1500 },
  { id: 'slides',   url: `${BASE}/output/cv-michael-borck-slides.html`, delay: 2000 },
  { id: 'live-api', url: 'https://api.resume.michaelborck.dev/docs',    delay: 3000 },
  { id: 'mcp',      url: 'https://www.npmjs.com/package/@michaelborck/resume-mcp-server', delay: 2000 },
  { id: 'source',   url: 'https://github.com/michael-borck/resume.borck.dev/blob/main/data/cv-data.yml', delay: 2000 },
];

const VIEWPORT = { width: 1280, height: 800 };
const CLIP = { x: 0, y: 0, width: 1280, height: 600 };

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: VIEWPORT });

for (const fmt of formats) {
  console.log(`Screenshotting ${fmt.id}…`);
  const page = await context.newPage();
  try {
    await page.goto(fmt.url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(fmt.delay);
    await page.screenshot({
      path: join(OUT, `${fmt.id}.png`),
      clip: CLIP,
    });
    console.log(`  ✓ ${fmt.id}.png`);
  } catch (err) {
    console.warn(`  ✗ ${fmt.id}: ${err.message}`);
  }
  await page.close();
}

// llms.txt — render as styled code preview
console.log('Screenshotting llms…');
const page = await context.newPage();
await page.setContent(`
  <html><body style="margin:0;background:#0d1117;font-family:monospace;font-size:13px;color:#c9d1d9;padding:24px;line-height:1.6">
  <div style="color:#58a6ff;margin-bottom:12px;font-size:15px;font-weight:bold"># llms.txt — Michael Borck</div>
  <div style="color:#8b949e">&gt; Resume structured for LLM ingestion</div>
  <br/>
  <div style="color:#3fb950">## Identity</div>
  <div>Name: Michael Borck</div>
  <div>Role: Developer · Educator · Researcher</div>
  <br/>
  <div style="color:#3fb950">## Current Roles</div>
  <div>- Lecturer, Curtin University</div>
  <div>- Lead, LocoLabo applied AI research</div>
  <br/>
  <div style="color:#8b949e;font-style:italic">… structured for AI tool ingestion</div>
  </body></html>
`);
await page.screenshot({ path: join(OUT, 'llms.png'), clip: CLIP });
console.log('  ✓ llms.png');

// "How It Works" — render the ASCII pipeline
const page2 = await context.newPage();
await page2.setContent(`
  <html><body style="margin:0;background:#0d1117;font-family:monospace;font-size:14px;color:#c9d1d9;padding:40px;line-height:1.8;display:flex;align-items:center;justify-content:center;min-height:600px">
  <pre style="color:#58a6ff;font-size:15px">cv-data.yml
 +──&gt; Quarto   ──&gt; PDF, HTML, Slides
 +──&gt; Python   ──&gt; Quest, Terminal,
 |              Magazine, API Docs
 +──&gt; FastAPI  ──&gt; Live API + Swagger
 +──&gt; MCP      ──&gt; AI integration
 +──&gt; Gen      ──&gt; llms.txt</pre>
  </body></html>
`);
await page2.screenshot({ path: join(OUT, 'pipeline.png'), clip: CLIP });
console.log('  ✓ pipeline.png');

await browser.close();
console.log('\nDone. Thumbnails saved to public-astro/thumbs/');
