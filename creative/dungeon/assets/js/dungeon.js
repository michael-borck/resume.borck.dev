/* The Delve — a roguelike text dungeon over the CV.
   Procedural dungeon each run, turn-based tile movement, HP/combat, loot,
   permadeath, three depths. Renders a persistent ASCII map that redraws every
   turn, with a bounded message log beside it. No dependencies. */
(() => {
  "use strict";

  const mapEl = document.getElementById("map");
  const logEl = document.getElementById("log");
  const form = document.getElementById("form");
  const input = document.getElementById("cmd");
  const hudEl = document.getElementById("hud");
  const overlay = document.getElementById("won");
  const overlayTitle = document.getElementById("overlayTitle");
  const overlayText = document.getElementById("wonText");

  const W = 40, H = 22;
  const DIRS = {
    n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0],
    north: [0, -1], south: [0, 1], east: [1, 0], west: [-1, 0],
    up: [0, -1], down: [0, 1], right: [1, 0], left: [-1, 0],
  };

  // ---- state ----
  let data = null;
  let seed = 1;
  let rng = Math.random;
  let depth = 1, maxDepth = 3;
  let grid, rooms, pos, stairsPos, archivePos;
  let enemies = [], items = [], seen, visible;
  let relicIndex = 0;
  let turn = 0;
  const state = { maxhp: 24, hp: 24, atk: 3, potions: 0, relics: [], won: false, dead: false, over: false };

  // ---- rng ----
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const ri = (n) => Math.floor(rng() * n);
  const pick = (a) => a[ri(a.length)];

  // ---- output (bounded message log) ----
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
  function log(html, cls) {
    const d = document.createElement("div");
    d.innerHTML = cls ? `<span class="${cls}">${html}</span>` : html;
    logEl.appendChild(d);
    while (logEl.children.length > 300) logEl.removeChild(logEl.firstChild);
    logEl.scrollTop = logEl.scrollHeight;
  }
  function hr() { log('<span class="dim">────────────────────────────────────────</span>'); }

  // ---- generation ----
  function genDepth(d) {
    grid = Array.from({ length: H }, () => Array(W).fill("#"));
    rooms = [];
    let tries = 400;
    while (rooms.length < 9 && tries-- > 0) {
      const w = 3 + ri(4), h = 3 + ri(3);
      const x = 1 + ri(W - w - 2), y = 1 + ri(H - h - 2);
      if (rooms.every((o) => x + w + 1 < o.x || o.x + o.w + 1 < x || y + h + 1 < o.y || o.y + o.h + 1 < y)) {
        rooms.push({ x, y, w, h });
        for (let yy = y; yy < y + h; yy++) for (let xx = x; xx < x + w; xx++) grid[yy][xx] = ".";
      }
    }
    if (rooms.length < 2) { // fallback
      rooms = [{ x: 1, y: 1, w: 6, h: 4 }, { x: W - 8, y: H - 6, w: 6, h: 4 }];
      for (const r of rooms) for (let yy = r.y; yy < r.y + r.h; yy++) for (let xx = r.x; xx < r.x + r.w; xx++) grid[yy][xx] = ".";
    }
    const centers = rooms.map((r) => ({ x: Math.floor(r.x + r.w / 2), y: Math.floor(r.y + r.h / 2) }));
    for (let i = 1; i < centers.length; i++) corridor(centers[i - 1], centers[i]);
    for (let k = 0; k < 2 && rooms.length > 3; k++) {
      const a = ri(centers.length), b = ri(centers.length);
      if (a !== b) corridor(centers[a], centers[b]);
    }

    pos = { ...centers[0] };
    // farthest room centre from start -> stairs/archive
    let far = centers[1] || centers[0], best = -1;
    for (const c of centers) {
      const dd = (c.x - pos.x) ** 2 + (c.y - pos.y) ** 2;
      if (dd > best) { best = dd; far = c; }
    }
    stairsPos = null; archivePos = null;
    if (d < maxDepth) { grid[far.y][far.x] = ">"; stairsPos = { ...far }; }
    else { grid[far.y][far.x] = "A"; archivePos = { ...far }; }

    // floor cells for placement (not too near the start, not the special tile)
    const cells = [];
    for (const r of rooms) for (let yy = r.y; yy < r.y + r.h; yy++) for (let xx = r.x; xx < r.x + r.w; xx++) {
      if (grid[yy][xx] !== ".") continue;
      if (Math.abs(xx - pos.x) <= 2 && Math.abs(yy - pos.y) <= 2) continue;
      cells.push({ x: xx, y: yy });
    }
    shuffle(cells);

    enemies = [];
    items = [];
    const occupied = new Set();
    const take = () => {
      for (let i = 0; i < cells.length; i++) {
        const c = cells[i];
        const k = c.x + "," + c.y;
        if (occupied.has(k)) continue;
        occupied.add(k);
        return c;
      }
      return null;
    };

    const nEnemies = 2 + d * 2;
    for (let i = 0; i < nEnemies; i++) {
      const c = take(); if (!c) break;
      const name = pick(data.monsters);
      const hp = 3 + d * 2 + ri(3);
      enemies.push({ x: c.x, y: c.y, name, hp, maxhp: hp, atk: 1 + Math.floor(d / 2) });
    }
    for (let i = 0; i < 3; i++) { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "relic", relic: nextRelic() }); }
    for (let i = 0; i < 2; i++) { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "potion" }); }
    { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "weapon" }); }

    seen = new Set();
    computeFOV();
  }

  function nextRelic() {
    const pool = data.relics;
    if (!pool.length) return { title: "A blank plaque", body: [] };
    const r = pool[relicIndex % pool.length];
    relicIndex++;
    return r;
  }

  function corridor(a, b) {
    if (rng() < 0.5) { hcarve(a.x, b.x, a.y); vcarve(a.y, b.y, b.x); }
    else { vcarve(a.y, b.y, a.x); hcarve(a.x, b.x, b.y); }
  }
  function hcarve(x1, x2, y) { for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) if (grid[y][x] === "#") grid[y][x] = "."; }
  function vcarve(y1, y2, x) { for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) if (grid[y][x] === "#") grid[y][x] = "."; }

  function shuffle(a) { for (let i = a.length - 1; i > 0; i--) { const j = ri(i + 1); [a[i], a[j]] = [a[j], a[i]]; } }

  // ---- field of view (radius + simple raycast for walls) ----
  function computeFOV() {
    visible = new Set();
    const R = 5;
    for (let dy = -R; dy <= R; dy++) for (let dx = -R; dx <= R; dx++) {
      if (dx * dx + dy * dy > R * R + 1) continue;
      const x = pos.x + dx, y = pos.y + dy;
      if (!inb(x, y)) continue;
      if (los(pos.x, pos.y, x, y)) { visible.add(x + "," + y); seen.add(x + "," + y); }
    }
    visible.add(pos.x + "," + pos.y);
    seen.add(pos.x + "," + pos.y);
  }

  // Bresenham line-of-sight: walls block sight beyond them.
  function los(x0, y0, x1, y1) {
    let dx = Math.abs(x1 - x0), dy = Math.abs(y1 - y0);
    let sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
    let err = dx - dy, x = x0, y = y0;
    while (!(x === x1 && y === y1)) {
      const e2 = 2 * err;
      if (e2 > -dy) { err -= dy; x += sx; }
      if (e2 < dx) { err += dx; y += sy; }
      if (x === x1 && y === y1) break;
      if (!inb(x, y)) return false;
      if (grid[y][x] === "#") return false; // wall blocks sight past it
    }
    return true;
  }

  // ---- helpers ----
  const inb = (x, y) => x >= 0 && y >= 0 && x < W && y < H;
  const passable = (x, y) => inb(x, y) && grid[y][x] !== "#";
  const enemyAt = (x, y) => enemies.find((e) => e.x === x && e.y === y);
  const itemAt = (x, y) => items.find((i) => i.x === x && i.y === y);
  const cheb = (a, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));

  // ---- map rendering ----
  function render() {
    const rows = [];
    for (let y = 0; y < H; y++) {
      let row = "";
      for (let x = 0; x < W; x++) {
        const k = x + "," + y;
        if (x === pos.x && y === pos.y) { row += '<span class="you">@</span>'; continue; }
        if (!seen.has(k)) { row += " "; continue; }
        const vis = visible.has(k);
        const e = vis ? enemyAt(x, y) : null;
        if (e) { row += `<span class="foe">${e.name[0].toUpperCase()}</span>`; continue; }
        if (vis) {
          const it = itemAt(x, y);
          if (it) {
            const g = it.type === "relic" ? "*" : it.type === "potion" ? "!" : ")";
            row += `<span class="item">${g}</span>`;
            continue;
          }
        }
        const cell = grid[y][x];
        if (cell === "#") { row += '<span class="w">#</span>'; continue; }
        if (cell === ">") { row += '<span class="stairs">&gt;</span>'; continue; }
        if (cell === "A") { row += '<span class="archive">A</span>'; continue; }
        row += `<span class="${vis ? "f" : "seen"}">${cell === "." ? "·" : cell}</span>`;
      }
      rows.push(row);
    }
    mapEl.innerHTML = rows.join("\n");
  }

  // ---- hud ----
  function updateHud() {
    hudEl.textContent = `HP ${Math.max(0, state.hp)}/${state.maxhp} · ATK ${state.atk} · depth ${depth}/${maxDepth} · relics ${state.relics.length}`;
  }

  // ---- actions ----
  function move(dx, dy) {
    if (state.over) return { ok: false };
    const nx = pos.x + dx, ny = pos.y + dy;
    if (!inb(nx, ny) || grid[ny][nx] === "#") { return { ok: false }; }
    const e = enemyAt(nx, ny);
    if (e) { attack(e); endTurn(); return { ok: true }; }
    pos = { x: nx, y: ny };
    computeFOV();
    autoPick();
    render();
    if (grid[ny][nx] === "A") { win(); return { ok: true }; }
    if (grid[ny][nx] === ">" ) log("A stairway spirals down into the dark. <b>(descend)</b>", "take");
    endTurn();
    return { ok: true };
  }

  function attack(e) {
    const dmg = state.atk;
    e.hp -= dmg;
    log(`You strike the ${esc(e.name)} for ${dmg}.`, "hi");
    if (e.hp <= 0) {
      enemies = enemies.filter((x) => x !== e);
      log(`The ${esc(e.name)} falls.`, "hi");
    }
    computeFOV();
    render();
  }

  function autoPick() {
    const it = itemAt(pos.x, pos.y);
    if (!it) return;
    items = items.filter((x) => x !== it);
    if (it.type === "potion") { state.potions++; log("You pocket a flask of healing. <b>(use potion)</b>", "take"); }
    else if (it.type === "weapon") { state.atk += data.weaponBonus; log(`You find a keener edge. ATK +${data.weaponBonus} → ${state.atk}.`, "take"); }
    else if (it.type === "relic") {
      state.relics.push(it.relic);
      log(`✦ RELIC: ${esc(it.relic.title)}`, "take");
      for (const b of (it.relic.body || []).slice(0, 2)) if (b) log(`&nbsp;&nbsp;&nbsp;&nbsp;${esc(b)}`, "dim");
    }
  }

  function potion() {
    if (state.over) return;
    if (!state.potions) { log("You have no potions.", "err"); return; }
    state.potions--;
    state.hp = Math.min(state.maxhp, state.hp + data.potionHeal);
    log(`You drink a potion. (+${data.potionHeal} HP → ${state.hp}/${state.maxhp})`, "hi");
    endTurn();
  }

  function endTurn() {
    if (state.over) return;
    turn++;
    enemiesAct();
    if (state.hp <= 0) { die(); return; }
    computeFOV();
    render();
    updateHud();
    const adj = enemies.filter((e) => cheb(e, pos) === 1);
    if (adj.length) log(`⚠ ${adj.map((e) => e.name).join(", ")} ${adj.length > 1 ? "are" : "is"} right next to you.`, "err");
  }

  function enemiesAct() {
    for (const e of enemies.slice()) {
      if (state.hp <= 0) return;
      const d = cheb(e, pos);
      if (d === 1) {
        state.hp -= e.atk;
        log(`The ${esc(e.name)} hits you for ${e.atk}. (HP ${Math.max(0, state.hp)})`, "err");
      } else if (d <= 6) {
        stepToward(e);
      }
    }
  }

  function stepToward(e) {
    const dx = Math.sign(pos.x - e.x), dy = Math.sign(pos.y - e.y);
    const opts = Math.abs(pos.x - e.x) > Math.abs(pos.y - e.y)
      ? [[dx, 0], [0, dy]] : [[0, dy], [dx, 0]];
    for (const [mx, my] of opts) {
      if (mx === 0 && my === 0) continue;
      const nx = e.x + mx, ny = e.y + my;
      if (!passable(nx, ny)) continue;
      if (nx === pos.x && ny === pos.y) continue;
      if (enemyAt(nx, ny)) continue;
      e.x = nx; e.y = ny; return;
    }
  }

  function die() {
    state.hp = 0; state.dead = true; state.over = true;
    render(); updateHud();
    overlayTitle.textContent = "YOU DIED";
    overlayText.innerHTML = `The dark takes you on depth ${depth} after ${state.relics.length} relic${state.relics.length === 1 ? "" : "s"}.<br>Every delver dies; only the seed remembers. Run again.`;
    overlay.classList.remove("hidden");
  }

  function win() {
    state.won = true; state.over = true;
    const c = data.contact || {};
    render(); updateHud();
    overlayTitle.textContent = "THE ARCHIVE IS YOURS";
    overlayText.innerHTML = `You reach the Archive with ${state.relics.length} relic${state.relics.length === 1 ? "" : "s"} of a working life.<br><br>${esc(c.name)} · ${esc(c.location)}<br>${esc(c.email)}`;
    overlay.classList.remove("hidden");
  }

  function descend() {
    if (state.over) return;
    if (!stairsPos || pos.x !== stairsPos.x || pos.y !== stairsPos.y) { log("There are no stairs here.", "err"); return; }
    depth++;
    if (depth > maxDepth) { win(); return; }
    log(`You descend to depth ${depth}…`, "hdr");
    genDepth(depth);
    emitIntro();
    render(); updateHud();
  }

  // ---- info ----
  function look() {
    const dirs = [];
    for (const [k, [dx, dy]] of Object.entries({ n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] })) {
      if (passable(pos.x + dx, pos.y + dy)) dirs.push(k);
    }
    log(`You are on depth ${depth}. Open directions: ${dirs.join(" ") || "none"}.`, "dim");
    const here = itemAt(pos.x, pos.y);
    if (here) log(`Underfoot: ${here.type}.`, "dim");
    const adj = enemies.filter((e) => cheb(e, pos) <= 1);
    if (adj.length) log("Beside you: " + adj.map((e) => `${e.name} (${e.hp}hp)`).join(", "), "err");
    const near = enemies.filter((e) => cheb(e, pos) > 1 && cheb(e, pos) <= 3);
    if (near.length) log("Nearby: " + near.map((e) => e.name).join(", "), "dim");
    if (stairsPos && pos.x === stairsPos.x && pos.y === stairsPos.y) log("A stairway down. (descend)", "take");
    if (grid[pos.y][pos.x] === "A") log("The Archive glows here.", "take");
  }

  // ---- intro ----
  function emitIntro() {
    hr();
    log(`DEPTH ${depth} OF ${maxDepth} · seed ${seed}`, "room");
    log("Arrows / WASD / HJKL to move. Walk into a foe to strike it.", "dim");
    const foes = enemies.filter((e) => cheb(e, pos) <= 4);
    if (foes.length) log("Something stirs nearby: " + foes.map((e) => e.name).join(", "), "err");
    log("Legend: @ you · · floor · # wall · letters foes · * relic · ! potion · ) blade · > stairs · A archive", "dim");
  }

  // ---- command interpreter ----
  function exec(raw) {
    const text = String(raw || "").trim();
    if (!text) return { ok: false };
    log(`<span class="dim">&gt; ${esc(text)}</span>`);
    const [verb, ...rest] = text.toLowerCase().split(/\s+/);
    const arg = rest.join(" ");

    if (DIRS[verb]) { const r = move(...DIRS[verb]); updateHud(); return r; }

    switch (verb) {
      case "help": case "?":
        emitHelp(); return { ok: true };
      case "look": case "l":
        look(); return { ok: true };
      case "map": case "m":
        log("The map is always visible on the left.", "dim"); render(); return { ok: true };
      case "wait": case ".": case "rest":
        log("You wait a beat…", "dim"); endTurn(); return { ok: true };
      case "attack": case "a": case "hit":
        const dir = DIRS[arg];
        if (!dir) { log("Attack which way? (attack n)", "err"); return { ok: false }; }
        const e = enemyAt(pos.x + dir[0], pos.y + dir[1]);
        if (!e) { log("There is nothing to strike there.", "err"); return { ok: false }; }
        attack(e); endTurn(); return { ok: true };
      case "potion": case "use": case "drink": case "p":
        potion(); updateHud(); return { ok: true };
      case "inventory": case "i": case "inv":
        log(`Potions: ${state.potions} · ATK: ${state.atk} · Relics: ${state.relics.length}`, "hdr");
        for (const r of state.relics) log(`&nbsp;&nbsp;✦ ${esc(r.title)}`, "dim");
        return { ok: true };
      case "descend": case "d": case "down":
        descend(); return { ok: true };
      case "stats":
        updateHud(); log(hudEl.textContent, "hdr"); return { ok: true };
      case "seed":
        log(`seed ${seed}`, "hdr"); return { ok: true };
      case "clear": case "cls":
        logEl.innerHTML = ""; return { ok: true };
      default:
        log(`I don't know '${esc(verb)}'. Type 'help'.`, "err");
        return { ok: false };
    }
  }

  function emitHelp() {
    log("Keys (no typing needed)", "hdr");
    log("  Arrows / WASD / HJKL   move one tile (walk into a foe to attack)");
    log("  &gt;                      take the stairs down");
    log("  p                      drink a potion");
    log("  i · ?                  inventory · help");
    log("  space / .              wait (foes take a turn)");
    log("  / or Enter             type a command (Esc to leave the box)");
    log("", "dim");
    log("Commands (after / or Enter)", "hdr");
    log("  attack <dir> · look · descend · inventory · stats · seed · clear");
    log("Goal: descend three depths, reach the Archive, and gather relics.", "dim");
  }

  // ---- ui ----
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = input.value; input.value = "";
    exec(v);
    updateHud();
    input.blur();
    mapEl.focus();
  });
  document.getElementById("helpBtn").addEventListener("click", () => { emitHelp(); mapEl.focus(); });
  document.getElementById("restartBtn").addEventListener("click", () => newRun());
  document.getElementById("againBtn").addEventListener("click", () => newRun());

  // Click on the map returns focus to movement mode.
  mapEl.addEventListener("mousedown", () => { if (document.activeElement === input) input.blur(); mapEl.focus(); });

  // ---- direct keyboard control (nethack-style) ----
  const KEYMOVE = {
    ArrowUp: "n", ArrowDown: "s", ArrowLeft: "w", ArrowRight: "e",
    w: "n", s: "s", a: "w", d: "e",          // WASD
    k: "n", j: "s", h: "w", l: "e",          // hjkl (nethack)
    "8": "n", "2": "s", "4": "w", "6": "e",  // numpad
  };
  const typingCommand = () => document.activeElement === input;

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (typingCommand()) { input.blur(); mapEl.focus(); e.preventDefault(); }
      return;
    }
    if (typingCommand()) return;
    if (state.over) {
      if (e.key === "Enter") { e.preventDefault(); newRun(); }
      return;
    }
    const k = e.key;
    if (KEYMOVE[k]) { e.preventDefault(); move(...DIRS[KEYMOVE[k]]); updateHud(); return; }
    if (k === "Enter" || k === "/" || k === ":") { e.preventDefault(); input.focus(); return; }
    if (k === ">") { e.preventDefault(); descend(); return; }
    if (k === " " || k === ".") { e.preventDefault(); log("You wait a beat…", "dim"); endTurn(); updateHud(); return; }
    if (k === "i") { e.preventDefault(); exec("inventory"); return; }
    if (k === "p") { e.preventDefault(); potion(); updateHud(); return; }
    if (k === "?") { e.preventDefault(); emitHelp(); return; }
  });

  // ---- run lifecycle ----
  function newRun(forceSeed) {
    seed = forceSeed != null ? forceSeed : (Math.floor(Math.random() * 0xffffffff) >>> 0);
    rng = mulberry32(seed);
    depth = 1; turn = 0; relicIndex = 0;
    state.maxhp = data.player.hp; state.hp = data.player.hp; state.atk = data.player.atk;
    state.potions = 0; state.relics = []; state.won = false; state.dead = false; state.over = false;
    overlay.classList.add("hidden");
    logEl.innerHTML = "";
    log(data.title + " — " + data.subtitle, "room");
    log("A roguelike of a working life. Three depths, a handful of relics, and the things that stand in the way.", "dim");
    genDepth(1);
    emitIntro();
    render();
    updateHud();
    mapEl.focus();
  }

  // ---- boot ----
  async function boot() {
    try {
      const res = await fetch("data/dungeon.json", { cache: "no-store" });
      data = await res.json();
    } catch (e) {
      log("Failed to load dungeon.json — run 'make dungeon'.", "err");
      return;
    }
    maxDepth = data.depths || 3;
    const qs = new URLSearchParams(location.search);
    newRun(qs.has("seed") ? Number(qs.get("seed")) >>> 0 : undefined);

    // test hooks
    window.__DUNGEON_DEBUG__ = () => ({
      depth, hp: state.hp, maxhp: state.maxhp, atk: state.atk, potions: state.potions,
      relics: state.relics.length, enemies: enemies.length, won: state.won, dead: state.dead,
      pos: { ...pos }, seed, stairs: stairsPos ? { ...stairsPos } : null, archive: archivePos ? { ...archivePos } : null,
    });
    window.__DUNGEON_TEST__ = {
      cmd: (s) => { const r = exec(s); updateHud(); return r; },
      state: () => window.__DUNGEON_DEBUG__(),
      toStairs: () => { if (stairsPos) { pos = { ...stairsPos }; computeFOV(); render(); return true; } return false; },
      toArchive: () => { if (archivePos) { pos = { ...archivePos }; computeFOV(); render(); if (grid[pos.y][pos.x] === "A") win(); return true; } return false; },
      teleport: (x, y) => { if (passable(x, y)) { pos = { x, y }; computeFOV(); render(); return true; } return false; },
      nearestEnemy: () => {
        if (!enemies.length) return null;
        const e = enemies.slice().sort((a, b) => cheb(a, pos) - cheb(b, pos))[0];
        return { x: e.x, y: e.y, name: e.name, hp: e.hp };
      },
      setAtk: (n) => { state.atk = n; updateHud(); },
      setHp: (n) => { state.hp = n; updateHud(); },
      killEnemies: () => { const n = enemies.length; enemies = []; return n; },
      heal: () => { state.hp = state.maxhp; },
      generation: () => {
        const seen2 = new Set([pos.x + "," + pos.y]);
        const q = [[pos.x, pos.y]];
        let floors = 0;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (grid[y][x] !== "#") floors++;
        while (q.length) {
          const [x, y] = q.pop();
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const nx = x + dx, ny = y + dy;
            if (!passable(nx, ny)) continue;
            const k = nx + "," + ny;
            if (!seen2.has(k)) { seen2.add(k); q.push([nx, ny]); }
          }
        }
        return { W, H, rooms: rooms.length, floors, reachable: seen2.size, fullyConnected: seen2.size === floors };
      },
      newRun: (s) => newRun(s),
      render,
    };
  }

  boot();
})();