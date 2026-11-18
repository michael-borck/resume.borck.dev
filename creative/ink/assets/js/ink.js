/* The Valley — Ink player. Uses the vendored inkjs runtime (ESM). */
import { Story } from "../../vendor/ink.mjs";

const proseEl = document.getElementById("prose");
const choicesEl = document.getElementById("choices");
const artEl = document.getElementById("art");
const artImg = document.getElementById("artImg");
const progressEl = document.getElementById("progress");
const restartBtn = document.getElementById("restart");

let story = null;
let lastImage = null;

function paragraphs(text) {
  const clean = text.replace(/^\n+/, "").replace(/\n+$/, "");
  if (!clean) return "";
  return clean
    .split(/\n{2,}/)
    .map((p, i) => `<p>${i === 0 ? dropCap(p) : esc(p).replace(/\n/g, "<br>")}</p>`)
    .join("");
}
function dropCap(p) {
  const safe = esc(p).replace(/\n/g, "<br>");
  // only add a drop cap on a normal first paragraph
  if (/^[A-Za-z]/.test(p) && p.length > 24) {
    return `<span class="drop">${safe.charAt(0)}</span>${safe.slice(1)}`;
  }
  return safe;
}
function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function applyTags(tags) {
  let image = null;
  for (const t of tags || []) {
    const m = /^image:\s*(.+)$/.exec(t.trim());
    if (m) image = m[1].trim();
  }
  if (image) {
    if (image !== lastImage) { artImg.src = image; lastImage = image; }
    artEl.classList.remove("empty");
  }
}

function updateProgress() {
  try {
    const v = Number(story.variablesState["visited_count"] || 0);
    progressEl.textContent = `${v} / 8 places`;
  } catch (e) { /* variable may not exist yet */ }
}

function render() {
  // gather all continuous text
  let text = "";
  let more = true;
  let guard = 0;
  while (more && guard++ < 500) {
    if (story.canContinue) {
      const line = story.Continue();
      text += line;
      if (story.currentTags) applyTags(story.currentTags);
    }
    more = story.canContinue;
  }

  if (text.trim()) {
    // append rather than replace so a scene builds up
    const p = document.createElement("div");
    p.innerHTML = paragraphs(text);
    proseEl.appendChild(p);
    proseEl.scrollTop = proseEl.scrollHeight;
  }

  choicesEl.innerHTML = "";
  if (story.currentChoices && story.currentChoices.length) {
    story.currentChoices.forEach((choice, i) => {
      const b = document.createElement("button");
      b.className = "choice";
      b.innerHTML = `<span class="arrow">›</span>${esc(choice.text)}`;
      b.addEventListener("click", () => choose(i));
      choicesEl.appendChild(b);
    });
  } else if (!story.canContinue) {
    const b = document.createElement("button");
    b.className = "choice";
    b.innerHTML = `<span class="arrow">↻</span>The end. Begin again.`;
    b.addEventListener("click", () => location.reload());
    choicesEl.appendChild(b);
    choicesEl.classList.add("end");
  }
  updateProgress();
}

function choose(i) {
  choicesEl.innerHTML = "";
  try {
    story.ChooseChoiceIndex(i);
  } catch (e) {
    console.error(e);
  }
  render();
}

async function boot() {
  try {
    const res = await fetch("data/story.json", { cache: "no-store" });
    if (!res.ok) throw new Error("missing story.json");
    const json = await res.text();
    story = new Story(json);
  } catch (err) {
    proseEl.innerHTML = `<p>The story failed to load. Run <code>make ink</code> to build story.json.</p>`;
    console.error(err);
    return;
  }

  restartBtn.addEventListener("click", () => location.reload());
  render();

  // test hooks
  window.__INK_DEBUG__ = () => ({
    visited: (() => { try { return Number(story.variablesState["visited_count"] || 0); } catch (e) { return -1; } })(),
    choices: (story.currentChoices || []).map((c) => c.text),
    canContinue: story.canContinue,
    done: !story.canContinue && (!story.currentChoices || story.currentChoices.length === 0),
    image: lastImage,
  });
  window.__INK_TEST__ = {
    choose: (i) => choose(i),
    chooseLabel: (sub) => {
      const idx = (story.currentChoices || []).findIndex((c) => c.text.toLowerCase().includes(sub.toLowerCase()));
      if (idx >= 0) { choose(idx); return true; }
      return false;
    },
    // exhaust the story by always choosing the first (or matching) option
    autoplay: (maxSteps = 60) => {
      let n = 0;
      while (n++ < maxSteps) {
        if (story.canContinue) { render(); continue; }
        if (!story.currentChoices || !story.currentChoices.length) break;
        // prefer unvisited places, else first
        let idx = (story.currentChoices || []).findIndex((c) => /—/.test(c.text));
        if (idx < 0) idx = 0;
        choose(idx);
      }
      return window.__INK_DEBUG__();
    },
  };
}

boot();