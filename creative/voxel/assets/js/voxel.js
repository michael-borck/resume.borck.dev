/* MineBorck — isometric voxel dig/build (Canvas 2D, no dependencies). */
(() => {
  "use strict";

  const canvas = document.getElementById("world");
  const ctx = canvas.getContext("2d");
  const oreCountEl = document.getElementById("oreCount");
  const logEl = document.getElementById("log");
  const welcome = document.getElementById("welcome");
  const wonEl = document.getElementById("won");
  const wonText = document.getElementById("wonText");

  let data = null;
  let pal = null;
  let blocks = [];                 // {x,y,z,type,fact?}
  let blockMap = new Map();        // "x,y,z" -> block
  let drawn = [];                  // [{b, top, left, right}]
  let hover = null;                // {b, face}
  let mode = "dig";
  let found = 0;
  let totalOre = 0;
  let won = false;

  // iso layout (CSS px)
  const L = { W2: 24, H2: 12, BH: 24, ox: 0, oy: 0 };
  const DPR = Math.min(window.devicePixelRatio || 1, 2);

  const key = (x, y, z) => `${x},${y},${z}`;

  // ---- data ----
  async function load() {
    const res = await fetch("data/voxel.json", { cache: "no-store" });
    data = await res.json();
    pal = data.palette;
    totalOre = data.totalFacts;
    blocks = data.blocks.slice();
    rebuild();
  }
  function rebuild() {
    blockMap.clear();
    for (const b of blocks) blockMap.set(key(b.x, b.y, b.z), b);
  }

  // ---- layout ----
  function computeLayout() {
    const cw = window.innerWidth, ch = window.innerHeight;
    const N = data.n;
    let W2 = Math.min(28, (cw - 70) / (2 * N));
    W2 = Math.max(12, W2);
    L.W2 = W2; L.H2 = W2 * 0.5; L.BH = 2 * L.H2;
    const maxZ = 7;
    const contentH = (2 * N - 2) * L.H2 + L.BH + maxZ * L.BH + L.H2;
    L.ox = cw / 2;
    L.oy = (ch - contentH) / 2 + maxZ * L.BH + L.H2;
  }

  function screenOf(x, y, z) {
    const cx = L.ox + (x - y) * L.W2;
    const topY = L.oy + (x + y) * L.H2 - z * L.BH;
    return { cx, topY };
  }

  // ---- render ----
  function render() {
    const w = window.innerWidth, h = window.innerHeight;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, w, h);
    // sky gradient
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, "#1b2a33"); g.addColorStop(0.6, "#111a22"); g.addColorStop(1, "#0a1016");
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

    const sorted = blocks.slice().sort((a, b) => {
      const da = a.x + a.y, db = b.x + b.y;
      if (da !== db) return da - db;
      if (a.z !== b.z) return a.z - b.z;
      return a.x - b.x;
    });

    drawn = [];
    for (const b of sorted) drawBlock(b);

    // hover outline
    if (hover && !won) {
      const d = drawn.find((d) => d.b === hover.b);
      if (d) {
        ctx.save();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        strokePoly(d.top);
        ctx.strokeStyle = "rgba(255,255,255,0.5)";
        strokePoly(d.left);
        ctx.strokeStyle = "rgba(255,255,255,0.35)";
        strokePoly(d.right);
        ctx.restore();
      }
    }
  }

  function strokePoly(pts) {
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.stroke();
  }

  function poly(pts, fill) {
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
  }

  function drawBlock(b) {
    const { cx, topY } = screenOf(b.x, b.y, b.z);
    const W2 = L.W2, H2 = L.H2, BH = L.BH;
    const T = [cx, topY - H2];
    const R = [cx + W2, topY];
    const Bm = [cx, topY + H2];
    const Lp = [cx - W2, topY];
    const top = [T, R, Bm, Lp];
    const left = [Lp, Bm, [Bm[0], Bm[1] + BH], [Lp[0], Lp[1] + BH]];
    const right = [Bm, R, [R[0], R[1] + BH], [Bm[0], Bm[1] + BH]];
    const c = pal[b.type] || pal.dirt;
    // subtle ore shimmer
    if (b.type === "ore") {
      poly(left, c.left); poly(right, c.right); poly(top, c.top);
      ctx.save(); ctx.globalAlpha = 0.9;
      ctx.fillStyle = "#fff6d0";
      ctx.beginPath(); ctx.arc(cx, topY, Math.max(2, W2 * 0.14), 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    } else {
      poly(left, c.left);
      poly(right, c.right);
      poly(top, c.top);
    }
    drawn.push({ b, top, left, right });
  }

  // ---- hit testing ----
  function pointInPoly(px, py, pts) {
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const xi = pts[i][0], yi = pts[i][1], xj = pts[j][0], yj = pts[j][1];
      if (((yi > py) !== (yj > py)) && (px < ((xj - xi) * (py - yi)) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }

  function hitTest(px, py) {
    for (let i = drawn.length - 1; i >= 0; i--) {
      const d = drawn[i];
      if (pointInPoly(px, py, d.top)) return { b: d.b, face: "top" };
      if (pointInPoly(px, py, d.left)) return { b: d.b, face: "left" };
      if (pointInPoly(px, py, d.right)) return { b: d.b, face: "right" };
    }
    return null;
  }

  // ---- actions ----
  function dig(b) {
    // excavate this block and everything above it in the column
    const colBlocks = blocks.filter((x) => x.x === b.x && x.y === b.y && x.z >= b.z)
      .sort((p, q) => q.z - p.z);
    if (!colBlocks.length) return;
    for (const cb of colBlocks) {
      blockMap.delete(key(cb.x, cb.y, cb.z));
      if (cb.type === "ore" && cb.fact) reveal(cb.fact);
    }
    const removed = new Set(colBlocks.map((c) => key(c.x, c.y, c.z)));
    blocks = blocks.filter((x) => !removed.has(key(x.x, x.y, x.z)));
    render();
  }

  function place(b) {
    const z = b.z + 1;
    if (z > 8) return;
    if (blockMap.has(key(b.x, b.y, z))) return;
    if (b.x < 0 || b.y < 0 || b.x >= data.n || b.y >= data.n) return;
    const nb = { x: b.x, y: b.y, z, type: "placed" };
    blocks.push(nb); blockMap.set(key(nb.x, nb.y, nb.z), nb);
    render();
  }

  function reveal(fact) {
    found++;
    oreCountEl.textContent = `${found}/${totalOre}`;
    const entry = document.createElement("div");
    entry.className = "entry";
    const body = (fact.body || []).filter(Boolean).slice(0, 2).join(" · ");
    entry.innerHTML = `<b>ORE: ${esc(fact.title)}</b>${body ? `<small>${esc(body)}</small>` : ""}`;
    logEl.prepend(entry);
    while (logEl.children.length > 5) logEl.removeChild(logEl.lastChild);
    if (found >= totalOre) win();
  }

  function win() {
    won = true;
    const c = data.contact || {};
    wonText.innerHTML = `You dug out every golden ore on the island — ${totalOre} facts about a working life.<br><br>${esc(c.name)} · ${esc(c.location)}<br>${esc(c.email)}`;
    wonEl.classList.remove("hidden");
  }

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }

  // ---- input ----
  function localXY(e) {
    const r = canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  function setupInput() {
    canvas.addEventListener("mousemove", (e) => {
      if (won) return;
      const p = localXY(e);
      const nh = hitTest(p.x, p.y);
      const changed = (nh && !hover) || (!nh && hover) || (nh && hover && nh.b !== hover.b);
      hover = nh;
      if (changed) render();
    });
    canvas.addEventListener("mouseleave", () => { if (hover) { hover = null; render(); } });
    canvas.addEventListener("click", (e) => {
      if (won) return;
      const p = localXY(e);
      const hit = hitTest(p.x, p.y);
      if (!hit) return;
      if (mode === "dig") dig(hit.b); else place(hit.b);
    });
    canvas.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      if (won) return;
      const p = localXY(e);
      const hit = hitTest(p.x, p.y);
      if (hit) place(hit.b);
    });
    document.querySelectorAll(".tool").forEach((btn) => {
      btn.addEventListener("click", () => {
        mode = btn.dataset.mode;
        document.querySelectorAll(".tool").forEach((b) => b.classList.toggle("active", b === btn));
      });
    });
    window.addEventListener("resize", () => { computeLayout(); render(); });
    document.getElementById("startBtn").addEventListener("click", () => welcome.classList.add("hidden"));
    document.getElementById("againBtn").addEventListener("click", () => location.reload());
  }

  // ---- boot ----
  async function boot() {
    try { await load(); } catch (e) { console.error(e); document.querySelector(".hint").textContent = "Failed to load voxel.json"; return; }
    computeLayout();
    const w = window.innerWidth, h = window.innerHeight;
    canvas.width = w * DPR; canvas.height = h * DPR;
    ctx.imageSmoothingEnabled = false;
    oreCountEl.textContent = `0/${totalOre}`;
    setupInput();
    render();

    // test hooks
    window.__VOXEL_DEBUG__ = () => ({
      blocks: blocks.length, found, total: totalOre, won, mode,
      hover: hover ? { x: hover.b.x, y: hover.b.y, z: hover.b.z, type: hover.b.type, face: hover.face } : null,
    });
    window.__VOXEL_TEST__ = {
      oreList: () => blocks.filter((b) => b.type === "ore").map((b) => ({ x: b.x, y: b.y, z: b.z, title: b.fact && b.fact.title })),
      digXY: (x, y, z) => { const b = blockMap.get(key(x, y, z)); if (b) { dig(b); return true; } return false; },
      digAllOre: () => { const ores = blocks.filter((b) => b.type === "ore"); for (const o of ores) { const cur = blockMap.get(key(o.x, o.y, o.z)); if (cur) dig(cur); } return found; },
      setMode: (m) => { mode = m; },
      hoverAt: (px, py) => { hover = hitTest(px, py); render(); return hover; },
    };
  }

  boot();
})();