// Compile creative/ink/story.ink -> creative/ink/data/story.json using inkjs.
// inkjs ships a JS compiler, so no inklecate binary is required.
//   node scripts/compile_ink.mjs
import { Compiler } from "inkjs/full";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const srcPath = path.join(root, "creative/ink/story.ink");
const outPath = path.join(root, "creative/ink/data/story.json");

const source = fs.readFileSync(srcPath, "utf8");
const compiler = new Compiler(source);

let story;
try {
  story = compiler.Compile();
} catch (err) {
  console.error("✗ Ink compile failed:");
  console.error(err && err.message ? err.message : err);
  const issues = compiler.errors || [];
  for (const e of issues) console.error("  ", e.message || e);
  process.exit(1);
}

const json = story.ToJson();
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, json);
const kb = (Buffer.byteLength(json) / 1024).toFixed(1);
console.log(`✓ Compiled ${path.relative(root, srcPath)} -> ${path.relative(root, outPath)} (${kb} KB)`);