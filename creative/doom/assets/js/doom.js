/* Resume Doom — a Wolfenstein/Doom-style raycaster (Canvas 2D, no dependencies).
   Renders a textured first-person view of the CV level.json, with billboard
   sprites (barrels, chests, demons) you shoot to reveal resume facts. */
(() => {
  "use strict";

  const canvas = document.getElementById("view");
  const ctx = canvas.getContext("2d");
  const minimap = document.getElementById("minimap");
  const mctx = minimap.getContext("2d");

  const el = {
    factCount: document.getElementById("factCount"),
    hp: document.getElementById("hp"),
    log: document.getElementById("log"),
    toast: document.getElementById("toast"),
    welcome: document.getElementById("welcome"),
    paused: document.getElementById("paused"),
    won: document.getElementById("won"),
    wonStats: document.getElementById("wonStats"),
    wonContact: document.getElementById("wonContact"),
    crosshair: document.getElementById("crosshair"),
    helpBtn: document.getElementById("helpBtn"),
    hint: document.getElementById("hint"),
  };

  // ---- Config ----
  const MOVE_SPEED = 3.0;         // cells/sec
  const TURN_SPEED = 2.6;         // rad/sec (keyboard)
  const MOUSE_SENS = 0.0022;
  const FOV_PLANE = 0.78;         // camera plane length -> ~76 deg fov
  const MAX_DEPTH = 24;
  const FIRE_COOLDOWN = 0.16;     // s
  const PLAYER_RADIUS = 0.22;

  // ---- State ----
  let level = null;
  let map = [];                   // 2D array of chars
  let MW = 0, MH = 0;
  const player = { x: 2, y: 2, a: 0, pitch: 0 };
  let entities = [];
  let facts = 0;
  let totalFacts = 0;
  let won = false;
  let running = false;
  let paused = false;
  let lastT = 0;
  let fireTimer = 0;
  let bob = 0;
  let shakeT = 0;

  const keys = Object.create(null);
  const RW = { w: 400, h: 260 };  // internal render resolution
  const zbuffer = new Float32Array(RW.w);

  // ---- Textures & sprites ----
  let wallTex = null;
  let sprites = {};

  function makeWallTexture() {
    const t = document.createElement("canvas");
    t.width = 64; t.height = 64;
    const c = t.getContext("2d");
    c.fillStyle = "#37282b"; c.fillRect(0, 0, 64, 64);
    // brick rows
    for (let row = 0; row < 8; row++) {
      const y = row * 8;
      const off = (row % 2) * 16;
      c.fillStyle = row % 2 ? "#402f32" : "#3a2a2d";
      c.fillRect(0, y, 64, 8);
      c.strokeStyle = "#241a1c"; c.lineWidth = 1;
      for (let bx = -16; bx < 64; bx += 32) {
        c.strokeRect(bx + off, y, 32, 8);
      }
    }
    // grime
    for (let i = 0; i < 120; i++) {
      c.fillStyle = `rgba(0,0,0,${Math.random() * 0.35})`;
      c.fillRect((Math.random() * 64) | 0, (Math.random() * 64) | 0, 2, 2);
    }
    return t;
  }

  function spriteCanvas(w, h, draw) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const g = c.getContext("2d");
    g.imageSmoothingEnabled = false;
    draw(g, w, h);
    return c;
  }

  function makeSprites() {
    // Barrel (skills)
    sprites.barrel = spriteCanvas(20, 26, (g, w, h) => {
      g.fillStyle = "#7a4a1f"; g.fillRect(4, 2, 12, 22);
      g.fillStyle = "#b06a2a"; g.fillRect(6, 3, 3, 20);
      g.fillStyle = "#4a2c12"; g.fillRect(4, 5, 12, 2); g.fillRect(4, 19, 12, 2);
      g.fillStyle = "#c9a24a"; g.fillRect(4, 11, 12, 2);
      g.fillStyle = "#2a1a0c"; g.fillRect(4, 23, 12, 2);
    });
    // Chest (education/projects/achievements)
    sprites.chest = spriteCanvas(22, 18, (g, w, h) => {
      g.fillStyle = "#5b3a1a"; g.fillRect(2, 6, 18, 11);
      g.fillStyle = "#7a4e22"; g.fillRect(2, 2, 18, 6);
      g.fillStyle = "#3a2410"; g.fillRect(2, 6, 18, 1);
      g.fillStyle = "#ffcf6b"; g.fillRect(9, 7, 4, 5);       // lock
      g.fillStyle = "#c9a24a"; g.fillRect(2, 2, 18, 1);
    });
    // Demon (a job)
    sprites.demon = spriteCanvas(22, 26, (g, w, h) => {
      g.fillStyle = "#8f1d14"; g.fillRect(5, 6, 12, 16);      // body
      g.fillStyle = "#b62a1e"; g.fillRect(6, 3, 10, 6);       // head
      g.fillStyle = "#3a0d09"; g.fillRect(3, 2, 3, 5); g.fillRect(16, 2, 3, 5); // horns
      g.fillStyle = "#ffd23b"; g.fillRect(8, 5, 2, 2); g.fillRect(13, 5, 2, 2); // eyes
      g.fillStyle = "#3a0d09"; g.fillRect(8, 10, 7, 2);       // mouth
      g.fillStyle = "#6d150e"; g.fillRect(2, 10, 3, 8); g.fillRect(17, 10, 3, 8); // arms
    });
  }

  // ---- Load level ----
  async function loadLevel() {
    const res = await fetch("data/level.json");
    if (!res.ok) throw new Error("no level.json");
    level = await res.json();
    MW = level.width; MH = level.height;
    map = level.grid.map((row) => row.split(""));
    player.x = level.spawn.x; player.y = level.spawn.y; player.a = level.spawn.angle;
    entities = level.entities.map((e, i) => ({ ...e, id: i, dead: false }));
    totalFacts = entities.length;
    updateHud();
  }

  // ---- Resize ----
  function resize() {
    const w = window.innerWidth, h = window.innerHeight;
    canvas.width = w; canvas.height = h;
    ctx.imageSmoothingEnabled = false;
    // internal resolution: keep ~400px wide, aspect-correct
    RW.w = Math.min(480, Math.max(280, Math.floor(w / 3.2)));
    RW.h = Math.max(140, Math.round(RW.w * (h / w)));
    if (zbuffer.length !== RW.w) { /* realloc on next render */ }
  }

  // ---- Map helpers ----
  function cellAt(x, y) {
    const cx = x | 0, cy = y | 0;
    if (cx < 0 || cy < 0 || cx >= MW || cy >= MH) return "#";
    return map[cy][cx];
  }
  function blocked(x, y) { return cellAt(x, y) === "#"; }

  function tryMove(nx, ny) {
    const r = PLAYER_RADIUS;
    if (!blocked(nx + r, player.y) && !blocked(nx - r, player.y) && !blocked(nx, player.y + r) && !blocked(nx, player.y - r)) {
      player.x = nx;
    }
    if (!blocked(player.x, ny + r) && !blocked(player.x, ny - r) && !blocked(player.x + r, ny) && !blocked(player.x - r, ny)) {
      player.y = ny;
    }
  }

  // ---- Render ----
  function render() {
    const w = canvas.width, h = canvas.height;
    const rw = RW.w, rh = RW.h;
    // offscreen at low res
    if (!render._c) {
      render._c = document.createElement("canvas");
      render._ctx = render._c.getContext("2d");
    }
    const oc = render._c, og = render._ctx;
    if (oc.width !== rw || oc.height !== rh) { oc.width = rw; oc.height = rh; }
    const z = new Float32Array(rw);
    const zb = z;

    // ceiling + floor
    const grad = og.createLinearGradient(0, 0, 0, rh);
    grad.addColorStop(0, "#0c0a12");
    grad.addColorStop(0.5, "#15101a");
    grad.addColorStop(0.5, "#241a16");
    grad.addColorStop(1, "#0e0a08");
    og.fillStyle = grad; og.fillRect(0, 0, rw, rh);

    const dirX = Math.cos(player.a), dirY = Math.sin(player.a);
    const planeX = -dirY * FOV_PLANE, planeY = dirX * FOV_PLANE;

    for (let x = 0; x < rw; x++) {
      const camX = 2 * x / rw - 1;
      const rdx = dirX + planeX * camX;
      const rdy = dirY + planeY * camX;
      let mapX = player.x | 0, mapY = player.y | 0;
      const ddx = Math.abs(1 / (rdx || 1e-9));
      const ddy = Math.abs(1 / (rdy || 1e-9));
      let stepX, stepY, sideX, sideY;
      if (rdx < 0) { stepX = -1; sideX = (player.x - mapX) * ddx; }
      else { stepX = 1; sideX = (mapX + 1 - player.x) * ddx; }
      if (rdy < 0) { stepY = -1; sideY = (player.y - mapY) * ddy; }
      else { stepY = 1; sideY = (mapY + 1 - player.y) * ddy; }
      let hit = 0, side = 0, guard = 0;
      while (!hit && guard++ < 128) {
        if (sideX < sideY) { sideX += ddx; mapX += stepX; side = 0; }
        else { sideY += ddy; mapY += stepY; side = 1; }
        if (mapX < 0 || mapY < 0 || mapX >= MW || mapY >= MH) { hit = 1; side = 1; break; }
        if (map[mapY][mapX] === "#") hit = 1;
      }
      let perp = side === 0 ? (sideX - ddx) : (sideY - ddy);
      if (perp < 0.05) perp = 0.05;
      perp = Math.min(perp, MAX_DEPTH);
      zb[x] = perp;

      const lineH = Math.floor(rh / perp);
      let drawStart = (-lineH / 2 + rh / 2) | 0;
      let drawEnd = (lineH / 2 + rh / 2) | 0;

      // texture x
      let wallX = side === 0 ? player.y + perp * rdy : player.x + perp * rdx;
      wallX -= Math.floor(wallX);
      let texX = (wallX * wallTex.width) | 0;
      if ((side === 0 && rdx > 0) || (side === 1 && rdy < 0)) texX = wallTex.width - texX - 1;

      // draw the texture column
      og.drawImage(wallTex, texX, 0, 1, wallTex.height, x, drawStart, 1, drawEnd - drawStart);
      // shading: side + distance fog
      let shade = Math.min(0.82, perp / MAX_DEPTH * 0.9 + (side === 1 ? 0.16 : 0));
      og.fillStyle = `rgba(6,4,6,${shade})`;
      og.fillRect(x, drawStart, 1, drawEnd - drawStart);
    }

    // ---- sprites ----
    const order = entities
      .filter((e) => !e.dead)
      .map((e) => ({ e, d: (player.x - e.x) ** 2 + (player.y - e.y) ** 2 }))
      .sort((a, b) => b.d - a.d);

    const invDet = 1 / (planeX * dirY - dirX * planeY);
    for (const { e } of order) {
      const spx = e.x - player.x, spy = e.y - player.y;
      const tX = invDet * (dirY * spx - dirX * spy);
      const tY = invDet * (-planeY * spx + planeX * spy);
      if (tY <= 0.12) continue;
      const screenX = ((rw / 2) * (1 + tX / tY)) | 0;
      const spH = Math.abs((rh / tY)) | 0;
      const spW = spH;
      let startY = (-spH / 2 + rh / 2) | 0;
      let startX = (screenX - spW / 2) | 0;
      const img = sprites[e.type] || sprites.chest;
      // vertical bob for demons
      if (e.type === "demon") startY += Math.sin(bob * 4 + e.id) * (spH * 0.02);
      const iw = img.width, ih = img.height;
      for (let stripe = 0; stripe < spW; stripe++) {
        const sx = startX + stripe;
        if (sx < 0 || sx >= rw) continue;
        if (tY >= zb[sx]) continue; // behind wall
        const texXf = ((stripe / spW) * iw) | 0;
        og.drawImage(img, texXf, 0, 1, ih, sx, startY, 1, spH);
        // simple distance shade
        if (tY > 6) { og.fillStyle = `rgba(6,4,6,${Math.min(0.6, (tY - 6) / 20)})`; og.fillRect(sx, startY, 1, spH); }
      }
    }

    // blit with shake
    let ox = 0, oy = 0;
    if (shakeT > 0) { ox = (Math.random() - 0.5) * 6 * (shakeT / 0.12); oy = (Math.random() - 0.5) * 6 * (shakeT / 0.12); }
    ctx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, w, h);
    ctx.drawImage(oc, ox, oy, w, h);

    // muzzle flash
    if (fireTimer > FIRE_COOLDOWN - 0.05) {
      ctx.fillStyle = "rgba(255,180,60,0.10)";
      ctx.fillRect(0, 0, w, h);
    }
  }

  // ---- Minimap ----
  function drawMinimap() {
    const size = minimap.width;
    const scale = size / Math.max(MW, MH);
    mctx.clearRect(0, 0, size, size);
    mctx.fillStyle = "rgba(6,4,5,0.6)"; mctx.fillRect(0, 0, size, size);
    // walls
    mctx.fillStyle = "#4a3336";
    for (let y = 0; y < MH; y++) for (let x = 0; x < MW; x++) {
      if (map[y][x] === "#") mctx.fillRect(x * scale, y * scale, Math.ceil(scale), Math.ceil(scale));
    }
    // entities
    for (const e of entities) {
      if (e.dead) continue;
      mctx.fillStyle = e.type === "demon" ? "#ff4b3e" : e.type === "barrel" ? "#ffcf6b" : "#7ddc7d";
      mctx.fillRect(e.x * scale - 1, e.y * scale - 1, 2.5, 2.5);
    }
    // player
    mctx.fillStyle = "#6ee0d8";
    mctx.beginPath();
    mctx.arc(player.x * scale, player.y * scale, 2.6, 0, Math.PI * 2);
    mctx.fill();
    mctx.strokeStyle = "#6ee0d8"; mctx.lineWidth = 1.4;
    mctx.beginPath();
    mctx.moveTo(player.x * scale, player.y * scale);
    mctx.lineTo((player.x + Math.cos(player.a) * 2) * scale, (player.y + Math.sin(player.a) * 2) * scale);
    mctx.stroke();
  }

  // ---- Shooting ----
  function fire() {
    if (!running || paused || won) return { err: "notrunning", running, paused, won };
    if (fireTimer > 0) return { err: "cooldown" };
    fireTimer = FIRE_COOLDOWN;
    el.crosshair.classList.add("fire");
    setTimeout(() => el.crosshair.classList.remove("fire"), 90);

    // nearest entity near screen center in front
    const dirX = Math.cos(player.a), dirY = Math.sin(player.a);
    const planeX = -dirY * FOV_PLANE, planeY = dirX * FOV_PLANE;
    const invDet = 1 / (planeX * dirY - dirX * planeY);
    let best = null, bestDepth = Infinity;
    const near = [];
    for (const e of entities) {
      if (e.dead) continue;
      const spx = e.x - player.x, spy = e.y - player.y;
      const d = Math.hypot(spx, spy);
      if (d > 22) continue;
      const tX = invDet * (dirY * spx - dirX * spy);
      const tY = invDet * (-planeY * spx + planeX * spy);
      const screenX = tY > 0.001 ? (1 + tX / tY) / 2 : -1;
      near.push({ title: e.title, d: +d.toFixed(2), tY: +tY.toFixed(2), sx: +screenX.toFixed(2) });
      if (tY <= 0.2 || tY > 20) continue;
      if (screenX < 0.40 || screenX > 0.60) continue;
      const hitWall = rayWallDepth(player.x, player.y, dirX, dirY);
      if (tY >= hitWall) continue;
      if (tY < bestDepth) { bestDepth = tY; best = e; }
    }

    if (best) {
      best.dead = true;
      if (best.type === "barrel") { boom(best, "BLASTED"); }
      else if (best.type === "demon") { boom(best, "VANQUISHED"); }
      else { reveal(best, "OPENED"); }
      facts++;
      updateHud();
      if (facts >= totalFacts) winGame();
      return { hit: best.title, type: best.type, facts };
    }
    toast("KICK!", 500);
    return { err: "no-target", near: near.slice(0, 4), insideWall: blocked(player.x, player.y), a: +player.a.toFixed(2) };
  }

  function rayWallDepth(px, py, dx, dy) {
    // step in small increments until a wall or MAX_DEPTH
    let t = 0, step = 0.05;
    while (t < MAX_DEPTH) {
      t += step;
      if (blocked(px + dx * t, py + dy * t)) return t;
    }
    return MAX_DEPTH;
  }

  function boom(e, verb) {
    shakeT = 0.12;
    reveal(e, verb);
  }

  function reveal(e, verb) {
    facts = Math.max(facts, 0);
    const entry = document.createElement("div");
    entry.className = "entry";
    const body = (e.body || []).filter(Boolean).slice(0, 3).join(" · ");
    entry.innerHTML = `<b>${verb}: ${esc(e.title)}</b>${body ? `<small>${esc(body)}</small>` : ""}`;
    el.log.prepend(entry);
    while (el.log.children.length > 6) el.log.removeChild(el.log.lastChild);
    toast(`${verb}: ${e.title}`, 1200);
  }

  function toast(msg, ms) {
    el.toast.textContent = msg;
    el.toast.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.toast.classList.remove("show"), ms || 1000);
  }

  function updateHud() {
    el.factCount.textContent = `${facts}/${totalFacts}`;
  }

  function winGame() {
    won = true;
    running = false;
    try { document.exitPointerLock && document.exitPointerLock(); } catch (e) {}
    el.wonStats.textContent = `You collected all ${totalFacts} facts across the facility.`;
    const c = level.contact || {};
    el.wonContact.innerHTML = `${esc(c.name || "")} · ${esc(c.location || "")}<br>${esc(c.email || "")}`;
    el.won.classList.remove("hidden");
  }

  // ---- Loop ----
  function update(dt) {
    if (!running || paused) return;
    bob += dt * (keys.w || keys.s ? 6 : 2);
    if (fireTimer > 0) fireTimer -= dt;
    if (shakeT > 0) shakeT -= dt;

    let mvX = 0, mvY = 0;
    const dirX = Math.cos(player.a), dirY = Math.sin(player.a);
    if (keys.w || keys.arrowup) { mvX += dirX; mvY += dirY; }
    if (keys.s || keys.arrowdown) { mvX -= dirX; mvY -= dirY; }
    if (keys.d) { mvX += -dirY; mvY += dirX; }       // strafe right
    if (keys.a) { mvX += dirY; mvY += -dirX; }       // strafe left
    if (keys.arrowleft) player.a -= TURN_SPEED * dt;
    if (keys.arrowright) player.a += TURN_SPEED * dt;
    if (mvX || mvY) {
      const len = Math.hypot(mvX, mvY) || 1;
      tryMove(player.x + (mvX / len) * MOVE_SPEED * dt, player.y + (mvY / len) * MOVE_SPEED * dt);
    }
  }

  function loop(t) {
    if (!lastT) lastT = t;
    let dt = (t - lastT) / 1000; lastT = t;
    if (dt > 0.1) dt = 0.1;
    update(dt);
    render();
    drawMinimap();
    requestAnimationFrame(loop);
  }

  // ---- Input ----
  function setupInput() {
    window.addEventListener("keydown", (e) => {
      const k = e.key.toLowerCase();
      keys[k] = true;
      if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(k)) e.preventDefault();
      if (k === " ") fire();
      if (k === "escape") { if (running) pause(); }
      if (k === "m") minimap.classList.toggle("hidden");
    });
    window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });

    canvas.addEventListener("click", () => {
      if (!running) return;
      if (document.pointerLockElement !== canvas) { lockPointer(); return; }
      fire();
    });
    document.addEventListener("mousemove", (e) => {
      if (document.pointerLockElement === canvas) player.a += e.movementX * MOUSE_SENS;
    });

    el.helpBtn.addEventListener("click", pause);
    document.getElementById("resumeBtn").addEventListener("click", resume);
    el.paused.addEventListener("click", (e) => { if (e.target === el.paused) resume(); });
    document.getElementById("againBtn").addEventListener("click", () => location.reload());
  }

  function start() {
    el.welcome.classList.add("hidden");
    running = true; paused = false;
    lastT = 0;
    lockPointer();
  }
  function pause() {
    paused = true;
    try { document.exitPointerLock && document.exitPointerLock(); } catch (e) {}
    el.paused.classList.remove("hidden");
  }
  function resume() {
    paused = false;
    el.paused.classList.add("hidden");
    lockPointer();
  }

  // ---- Utils ----
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  function lockPointer() {
    try {
      const p = canvas.requestPointerLock && canvas.requestPointerLock();
      if (p && p.catch) p.catch(() => {});
    } catch (e) {}
  }

  // ---- Boot ----
  async function boot() {
    wallTex = makeWallTexture();
    makeSprites();
    resize();
    window.addEventListener("resize", resize);
    setupInput();
    try {
      await loadLevel();
    } catch (err) {
      console.error(err);
      el.hint.textContent = "Failed to load level.json";
      return;
    }
    document.getElementById("startBtn").addEventListener("click", start);

    // Debug/test hook
    window.__DOOM_DEBUG__ = () => ({
      pos: { x: +player.x.toFixed(2), y: +player.y.toFixed(2), a: +player.a.toFixed(2) },
      facts, total: totalFacts, alive: entities.filter((e) => !e.dead).length, won, running, paused,
    });
    window.__DOOM_TEST__ = {
      start: () => start(),
      teleport: (x, y, a) => { player.x = x; player.y = y; if (a != null) player.a = a; },
      faceNearest: () => {
        const e = entities.filter((x) => !x.dead).sort((p, q) => ((p.x-player.x)**2+(p.y-player.y)**2) - ((q.x-player.x)**2+(q.y-player.y)**2))[0];
        if (!e) return null;
        player.a = Math.atan2(e.y - player.y, e.x - player.x);
        return { title: e.title, type: e.type, d: +Math.hypot(e.x-player.x, e.y-player.y).toFixed(2) };
      },
      fire: () => fire(),
      collectAll: () => { let n = 0; for (const e of entities) if (!e.dead) { e.dead = true; facts++; n++; } updateHud(); if (facts >= totalFacts) winGame(); return n; },
      list: () => entities.map((e) => ({ id: e.id, type: e.type, title: e.title, x: e.x, y: e.y, dead: e.dead })),
    };

    requestAnimationFrame(loop);
  }

  boot();
})();