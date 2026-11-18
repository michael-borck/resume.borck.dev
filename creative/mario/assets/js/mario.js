/* Michael Borck's World — a Super-Mario-World-style overworld.
   Fixed level nodes joined by paths; walk between adjacent nodes with the arrow
   keys, press Enter to enter a level, clear them all, reach the castle.
   Canvas 2D, no dependencies. */
(() => {
  "use strict";

  const canvas = document.getElementById("map");
  const ctx = canvas.getContext("2d");
  const el = {
    progress: document.getElementById("progress"),
    hint: document.getElementById("hint"),
    toast: document.getElementById("toast"),
    panel: document.getElementById("panel"),
    panelEyebrow: document.getElementById("panelEyebrow"),
    panelTitle: document.getElementById("panelTitle"),
    panelBody: document.getElementById("panelBody"),
    welcome: document.getElementById("welcome"),
    won: document.getElementById("won"),
    wonBody: document.getElementById("wonBody"),
  };

  const ICON_R = 26;         // node icon radius (screen px, scaled)
  const MOVE_DUR = 0.42;     // seconds to tween between nodes
  const DPR = Math.min(window.devicePixelRatio || 1, 2);

  let world = null;
  let byId = {};
  let nodes = [];
  let startId = "base", castleId = "castle";
  let levelCount = 0;
  let current = "base";
  const cleared = new Set();
  let moving = null;         // {from, to, t}
  let started = false, won = false, panelOpen = false;
  let bg = null, avatar = null;
  const icons = {};
  const view = { scale: 1, ox: 0, oy: 0, bw: 1216, bh: 832 };
  let bob = 0, lastT = 0;

  // ---- assets ----
  function loadImage(src) {
    return new Promise((resolve) => {
      const im = new Image();
      im.onload = () => resolve(im);
      im.onerror = () => resolve(null);
      im.src = src;
    });
  }
  async function loadAssets() {
    bg = await loadImage(world.background);
    avatar = await loadImage(world.avatar);
    const uniq = [...new Set(nodes.map((n) => n.icon))];
    await Promise.all(uniq.map(async (name) => {
      icons[name] = await loadImage(`../world/assets/img/${name}.png`);
    }));
    if (bg) { view.bw = bg.naturalWidth; view.bh = bg.naturalHeight; }
  }

  // ---- layout ----
  function resize() {
    const w = window.innerWidth, h = window.innerHeight;
    canvas.width = Math.floor(w * DPR);
    canvas.height = Math.floor(h * DPR);
    canvas.style.width = w + "px"; canvas.style.height = h + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.imageSmoothingEnabled = false;
    const pad = 40;
    const scale = Math.min((w - pad) / view.bw, (h - pad) / view.bh);
    view.scale = scale;
    view.ox = (w - view.bw * scale) / 2;
    view.oy = (h - view.bh * scale) / 2 + 6;
  }
  function nodeScreen(n) {
    return { x: view.ox + (n.x / 100) * view.bw * view.scale, y: view.oy + (n.y / 100) * view.bh * view.scale };
  }
  function playerScreen() {
    if (moving) {
      const a = nodeScreen(byId[moving.from]), b = nodeScreen(byId[moving.to]);
      const t = ease(moving.t / MOVE_DUR);
      return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
    }
    return nodeScreen(byId[current]);
  }
  const ease = (t) => t * t * (3 - 2 * t);

  // ---- render ----
  function render() {
    const w = window.innerWidth, h = window.innerHeight;
    const g = ctx.createLinearGradient(0, 0, 0, h);
    g.addColorStop(0, "#182a3f"); g.addColorStop(1, "#0b1220");
    ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);

    if (bg) {
      ctx.drawImage(bg, view.ox, view.oy, view.bw * view.scale, view.bh * view.scale);
      // gentle night tint
      ctx.fillStyle = "rgba(10,18,30,0.18)";
      ctx.fillRect(view.ox, view.oy, view.bw * view.scale, view.bh * view.scale);
    }

    drawPaths();
    for (const n of nodes) drawNode(n);
    drawPlayer();
  }

  function drawPaths() {
    ctx.save();
    ctx.setLineDash([6, 7]);
    ctx.lineDashOffset = -(bob * 20) % 13;
    for (const [a, b] of world.edges) {
      const pa = nodeScreen(byId[a]), pb = nodeScreen(byId[b]);
      const onPath = current === a || current === b;
      ctx.strokeStyle = onPath ? "rgba(255,207,107,0.95)" : "rgba(220,225,235,0.5)";
      ctx.lineWidth = onPath ? 3 : 2;
      ctx.beginPath(); ctx.moveTo(pa.x, pa.y); ctx.lineTo(pb.x, pb.y); ctx.stroke();
    }
    ctx.restore();
  }

  function drawNode(n) {
    const p = nodeScreen(n);
    const isCur = n.id === current;
    const isCleared = cleared.has(n.id);
    const locked = n.castle && cleared.size < levelCount;

    // glow for current / reachable
    if (isCur) {
      ctx.save();
      ctx.globalAlpha = 0.35 + 0.2 * Math.sin(bob * 3);
      ctx.fillStyle = n.castle ? "#ff7a6b" : "#ffcf6b";
      ctx.beginPath(); ctx.arc(p.x, p.y, ICON_R * 0.85, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    }

    ctx.save();
    if (locked) ctx.globalAlpha = 0.55;
    else if (isCleared && !n.castle) ctx.globalAlpha = 0.92;

    // icon or fallback
    const icon = icons[n.icon];
    const size = n.castle ? ICON_R * 2.2 : ICON_R * 1.7;
    if (icon) ctx.drawImage(icon, p.x - size / 2, p.y - size / 2, size, size);
    else { ctx.fillStyle = "#8a93a0"; ctx.fillRect(p.x - size / 3, p.y - size / 3, size / 1.5, size / 1.5); }

    // cleared badge
    if (isCleared && !n.castle) {
      ctx.fillStyle = "#6bd06b";
      ctx.beginPath(); ctx.arc(p.x + ICON_R * 0.8, p.y - ICON_R * 0.8, 8, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#0a1206"; ctx.font = "700 11px 'JetBrains Mono', monospace"; ctx.textAlign = "center";
      ctx.fillText("✓", p.x + ICON_R * 0.8, p.y - ICON_R * 0.8 + 4);
    }
    ctx.restore();

    // label pill
    ctx.save();
    ctx.font = "700 11px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    let label = n.name;
    if (locked) label += " 🔒";
    const tw = ctx.measureText(label).width;
    const ly = p.y + (n.castle ? ICON_R * 1.4 : ICON_R * 1.05);
    ctx.fillStyle = "rgba(10,15,22,0.85)";
    roundRect(p.x - tw / 2 - 7, ly - 1, tw + 14, 18, 4); ctx.fill();
    ctx.fillStyle = isCur ? "#ffe6a8" : (n.castle ? "#ff9d8f" : (isCleared ? "#bfe9c0" : "#cfd8df"));
    ctx.fillText(label, p.x, ly + 12);
    ctx.restore();
  }

  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function drawPlayer() {
    const p = playerScreen();
    const hover = Math.sin(bob * 5) * 2.5;
    const s = ICON_R * 1.7;
    ctx.save();
    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.beginPath(); ctx.ellipse(p.x, p.y + s / 2 - 2, s * 0.34, s * 0.14, 0, 0, Math.PI * 2); ctx.fill();
    if (avatar) ctx.drawImage(avatar, p.x - s / 2, p.y - s / 2 - s * 0.55 + hover, s, s);
    else { ctx.fillStyle = "#7ddc7d"; ctx.fillRect(p.x - s / 3, p.y - s / 2 - s * 0.55 + hover, s / 1.5, s); }
    ctx.restore();
  }

  // ---- state / ui ----
  function updateProgress() {
    el.progress.textContent = `LEVELS ${cleared.size}/${levelCount}`;
  }
  function setHint(text) { el.hint.textContent = text; }
  function toast(msg, ms) {
    el.toast.textContent = msg;
    el.toast.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.toast.classList.remove("show"), ms || 1100);
  }

  function arrivalHint() {
    const n = byId[current];
    if (won) return;
    if (n.castle) {
      if (cleared.size >= levelCount) setHint("Enter: enter the castle 🏰");
      else setHint(`The castle is sealed — ${levelCount - cleared.size} level(s) left`);
    } else if (!cleared.has(n.id)) {
      setHint(`Enter: enter ${n.name}`);
    } else {
      setHint("Arrows / WASD walk the paths · Enter enters a level · click a node");
    }
  }

  // ---- movement ----
  function moveDir(dx, dy) {
    if (!started || panelOpen || won || moving) return false;
    const cur = byId[current];
    let best = null, bestScore = 0.3;
    for (const id of cur.links) {
      const n = byId[id];
      const vx = n.x - cur.x, vy = n.y - cur.y;
      const len = Math.hypot(vx, vy) || 1;
      const score = (vx / len) * dx + (vy / len) * dy;
      if (score > bestScore) { bestScore = score; best = n; }
    }
    if (!best) { toast("No path that way"); return false; }
    moving = { from: current, to: best.id, t: 0 };
    return true;
  }

  function update(dt) {
    bob += dt;
    if (moving) {
      moving.t += dt;
      if (moving.t >= MOVE_DUR) {
        current = moving.to;
        moving = null;
        arrivalHint();
        const n = byId[current];
        toast(n.name, 900);
      }
    }
  }

  // ---- entering levels ----
  function openCurrent() {
    if (!started || moving || won) return;
    const n = byId[current];
    if (n.castle) return enterCastle(n);
    openLevel(n);
  }

  function openLevel(n) {
    cleared.add(n.id);
    updateProgress();
    el.panelEyebrow.textContent = "LEVEL · " + n.name;
    el.panelTitle.textContent = n.name;
    el.panelBody.innerHTML = (n.body.length ? n.body : ["(no details)"]).map((b) => `<p>${esc(b)}</p>`).join("");
    panelOpen = true;
    el.panel.classList.remove("hidden");
    arrivalHint();
  }

  function enterCastle(n) {
    if (cleared.size >= levelCount) { win(); return; }
    el.panelEyebrow.textContent = "CASTLE · sealed";
    el.panelTitle.textContent = "Castle Borck";
    el.panelBody.innerHTML = `<p>The gate is barred. <b>${levelCount - cleared.size}</b> level(s) remain before the castle will open.</p>`;
    panelOpen = true;
    el.panel.classList.remove("hidden");
  }

  function closePanel() {
    panelOpen = false;
    el.panel.classList.add("hidden");
    arrivalHint();
  }

  function win() {
    won = true;
    const c = byId[castleId];
    el.wonBody.innerHTML = (c.body || []).map((b) => `<p>${esc(b)}</p>`).join("") +
      `<p>All ${levelCount} levels cleared. Thanks for playing.</p>`;
    el.won.classList.remove("hidden");
  }

  // ---- input ----
  function setupInput() {
    window.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (!started) { start(); return; }
        if (panelOpen) { closePanel(); return; }
        openCurrent(); return;
      }
      if (e.key === "Escape" && panelOpen) { closePanel(); return; }
      if (panelOpen || !started) return;
      const k = e.key.toLowerCase();
      let dx = 0, dy = 0;
      if (k === "arrowup" || k === "w") dy = -1;
      else if (k === "arrowdown" || k === "s") dy = 1;
      else if (k === "arrowleft" || k === "a") dx = -1;
      else if (k === "arrowright" || k === "d") dx = 1;
      else return;
      e.preventDefault();
      moveDir(dx, dy);
    });

    canvas.addEventListener("click", (e) => {
      if (!started || panelOpen || won || moving) return;
      const rect = canvas.getBoundingClientRect();
      const px = e.clientX - rect.left, py = e.clientY - rect.top;
      let hit = null, bestD = 30;
      for (const n of nodes) {
        const p = nodeScreen(n);
        const d = Math.hypot(px - p.x, py - p.y);
        if (d < bestD) { bestD = d; hit = n; }
      }
      if (!hit) return;
      if (hit.id === current) { openCurrent(); return; }
      if (byId[current].links.includes(hit.id)) { moving = { from: current, to: hit.id, t: 0 }; }
      else toast("Follow the path — that level is not adjacent");
    });

    document.getElementById("helpBtn").addEventListener("click", () => {
      el.panelEyebrow.textContent = "HOW TO PLAY";
      el.panelTitle.textContent = "Walk, enter, clear";
      el.panelBody.innerHTML =
        "<p>Use the <b>arrow keys</b> or <b>WASD</b> to walk between levels along the paths.</p>" +
        "<p>When you stand on a level, press <b>Enter</b> to enter it (or click it). Levels you enter are marked ✓.</p>" +
        "<p>Clear all levels, then enter the <b>castle</b>.</p>";
      panelOpen = true; el.panel.classList.remove("hidden");
    });

    document.getElementById("panelClose").addEventListener("click", closePanel);
    document.getElementById("panel").addEventListener("click", (e) => { if (e.target.id === "panel") closePanel(); });
    document.getElementById("startBtn").addEventListener("click", start);
    document.getElementById("againBtn").addEventListener("click", () => location.reload());
    window.addEventListener("resize", () => { resize(); render(); });
  }

  function start() {
    started = true;
    el.welcome.classList.add("hidden");
    arrivalHint();
  }

  // ---- utils ----
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }

  // ---- loop ----
  function loop(t) {
    if (!lastT) lastT = t;
    let dt = (t - lastT) / 1000; lastT = t;
    if (dt > 0.1) dt = 0.1;
    update(dt);
    render();
    requestAnimationFrame(loop);
  }

  // ---- boot ----
  async function boot() {
    try {
      const res = await fetch("data/world.json", { cache: "no-store" });
      world = await res.json();
    } catch (e) {
      document.getElementById("hint").textContent = "Failed to load world.json — run 'make mario'.";
      return;
    }
    nodes = world.nodes;
    nodes.forEach((n) => { byId[n.id] = n; });
    startId = world.start;
    castleId = world.castle;
    current = startId;
    levelCount = nodes.filter((n) => !n.castle).length;

    await loadAssets();
    resize();
    setupInput();
    updateProgress();
    requestAnimationFrame(loop);

    window.__MARIO_DEBUG__ = () => ({ current, cleared: [...cleared], levels: levelCount, won, moving: !!moving, panelOpen, started });
    window.__MARIO_TEST__ = {
      start,
      move: (dir) => moveDir(...({ up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[dir] || [0, 0])),
      links: () => byId[current].links,
      goto: (id) => { if (byId[id]) { current = id; moving = null; arrivalHint(); } },
      open: () => openCurrent(),
      close: () => closePanel(),
      clearAll: () => { for (const n of nodes) if (!n.castle) cleared.add(n.id); updateProgress(); return cleared.size; },
      finish: () => { if (cleared.size >= levelCount) win(); return won; },
      neighbors: () => byId[current].links.map((id) => ({ id, name: byId[id].name })),
    };
  }

  boot();
})();