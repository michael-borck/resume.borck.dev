/* The Delve — a roguelike text dungeon over the CV.
   Procedural dungeon each run, turn-based tile movement, HP/combat, loot,
   permadeath, and three depths to descend. No dependencies. */
(() => {
  "use strict";

  const out = document.getElementById("out");
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
  const DNAME = { "0,-1": "north", "0,1": "south", "1,0": "east", "-1,0": "west" };

  // ---- state ----
  let data = null;
  let seed = 1;
  let rng = Math.random;
  let depth = 1, maxDepth = 3;
  let grid, rooms, pos, stairsPos, archivePos;
  let enemies = [], items = [], seen;
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

  // ---- output ----
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
  function emit(html, cls) {
    const d = document.createElement("div");
    d.innerHTML = cls ? `<span class="${cls}">${html}</span>` : html;
    out.appendChild(d);
    // keep terminal bounded
    while (out.children.length > 400) out.removeChild(out.firstChild);
    out.scrollTop = out.scrollHeight;
  }
  function hr() { emit('<span class="dim">────────────────────────────────────────</span>'); }

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

    // enemies scale with depth
    const nEnemies = 2 + d * 2;
    for (let i = 0; i < nEnemies; i++) {
      const c = take(); if (!c) break;
      const name = pick(data.monsters);
      const hp = 3 + d * 2 + ri(3);
      enemies.push({ x: c.x, y: c.y, name, hp, maxhp: hp, atk: 1 + Math.floor(d / 2), glyph: name[0].toUpperCase() });
    }
    // items
    for (let i = 0; i < 3; i++) { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "relic", glyph: "*", relic: nextRelic() }); }
    for (let i = 0; i < 2; i++) { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "potion", glyph: "!" }); }
    { const c = take(); if (c) items.push({ x: c.x, y: c.y, type: "weapon", glyph: ")" }); }

    seen = new Set();
    reveal();
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

  // ---- helpers ----
  const inb = (x, y) => x >= 0 && y >= 0 && x < W && y < H;
  const passable = (x, y) => inb(x, y) && grid[y][x] !== "#";
  const enemyAt = (x, y) => enemies.find((e) => e.x === x && e.y === y);
  const itemAt = (x, y) => items.find((i) => i.x === x && i.y === y);
  const cheb = (a, b) => Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y));

  function reveal() {
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
      const x = pos.x + dx, y = pos.y + dy;
      if (inb(x, y)) seen.add(x + "," + y);
    }
  }

  // ---- hud ----
  function updateHud() {
    hudEl.textContent = `HP ${Math.max(0, state.hp)}/${state.maxhp} · ATK ${state.atk} · depth ${depth}/${maxDepth} · relics ${state.relics.length}`;
  }

  // ---- actions ----
  function move(dx, dy) {
    if (state.over) return { ok: false };
    const nx = pos.x + dx, ny = pos.y + dy;
    if (!inb(nx, ny) || grid[ny][nx] === "#") { emit("A damp stone wall blocks the way.", "err"); return { ok: false }; }
    const e = enemyAt(nx, ny);
    if (e) { attack(e); endTurn(); return { ok: true }; }
    pos = { x: nx, y: ny };
    reveal();
    autoPick();
    if (grid[ny][nx] === "A") { win(); return { ok: true }; }
    if (grid[ny][nx] === ">") emit("A stairway spirals down into the dark. (descend)", "take");
    endTurn();
    return { ok: true };
  }

  function attack(e) {
    const dmg = state.atk;
    e.hp -= dmg;
    emit(`You strike the ${esc(e.name)} for ${dmg}.`, "hi");
    if (e.hp <= 0) {
      enemies = enemies.filter((x) => x !== e);
      emit(`The ${esc(e.name)} falls.`, "hi");
    }
  }

  function autoPick() {
    const it = itemAt(pos.x, pos.y);
    if (!it) return;
    items = items.filter((x) => x !== it);
    if (it.type === "potion") { state.potions++; emit("You pocket a flask of healing. (use potion)", "take"); }
    else if (it.type === "weapon") { state.atk += data.weaponBonus; emit(`You find a keener edge. ATK +${data.weaponBonus} → ${state.atk}.`, "take"); }
    else if (it.type === "relic") {
      state.relics.push(it.relic);
      emit(`✦ RELIC: ${esc(it.relic.title)}`, "take");
      for (const b of (it.relic.body || []).slice(0, 2)) if (b) emit(`    ${esc(b)}`, "dim");
    }
  }

  function potion() {
    if (state.over) return;
    if (!state.potions) { emit("You have no potions.", "err"); return; }
    state.potions--;
    state.hp = Math.min(state.maxhp, state.hp + data.potionHeal);
    emit(`You drink a potion. (+${data.potionHeal} HP → ${state.hp}/${state.maxhp})`, "hi");
    endTurn();
  }

  function endTurn() {
    if (state.over) return;
    turn++;
    enemiesAct();
    if (state.hp <= 0) { die(); return; }
    updateHud();
    // ambient warning
    const adj = enemies.filter((e) => cheb(e, pos) === 1);
    if (adj.length) emit(`⚠ ${adj.map((e) => e.name).join(", ")} ${adj.length > 1 ? "are" : "is"} right next to you.`, "err");
  }

  function enemiesAct() {
    for (const e of enemies.slice()) {
      const d = cheb(e, pos);
      if (d === 1) {
        state.hp -= e.atk;
        emit(`The ${esc(e.name)} hits you for ${e.atk}. (HP ${Math.max(0, state.hp)})`, "err");
        if (state.hp <= 0) return;
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
      const nx = e.x + mx, ny = e.y + my;
      if (!passable(nx, ny)) continue;
      if (nx === pos.x && ny === pos.y) continue;
      if (enemyAt(nx, ny)) continue;
      e.x = nx; e.y = ny; return;
    }
  }

  function die() {
    state.hp = 0; state.dead = true; state.over = true;
    updateHud();
    overlayTitle.textContent = "YOU DIED";
    overlayText.innerHTML = `The dark takes you on depth ${depth} after ${state.relics.length} relic${state.relics.length === 1 ? "" : "s"}.<br>Every delver dies; only the seed remembers. Run again.`;
    overlay.classList.remove("hidden");
  }

  function win() {
    state.won = true; state.over = true;
    const c = data.contact || {};
    overlayTitle.textContent = "THE ARCHIVE IS YOURS";
    overlayText.innerHTML = `You reach the Archive with ${state.relics.length} relic${state.relics.length === 1 ? "" : "s"} of a working life.<br><br>${esc(c.name)} · ${esc(c.location)}<br>${esc(c.email)}`;
    overlay.classList.remove("hidden");
  }

  function descend() {
    if (state.over) return;
    if (!stairsPos || pos.x !== stairsPos.x || pos.y !== stairsPos.y) { emit("There are no stairs here.", "err"); return; }
    depth++;
    if (depth > maxDepth) { win(); return; }
    emit(`You descend to depth ${depth}…`, "hdr");
    genDepth(depth);
    emitIntro();
    updateHud();
  }

  // ---- info ----
  function look() {
    const dirs = [];
    for (const [k, [dx, dy]] of Object.entries({ n: [0, -1], s: [0, 1], e: [1, 0], w: [-1, 0] })) {
      if (passable(pos.x + dx, pos.y + dy)) dirs.push(k);
    }
    emit(`You are on depth ${depth}. Open directions: ${dirs.join(" ") || "none"}.`, "dim");
    const here = itemAt(pos.x, pos.y);
    if (here) emit(`Underfoot: ${here.type}.`, "dim");
    const adj = enemies.filter((e) => cheb(e, pos) <= 1);
    if (adj.length) emit("Beside you: " + adj.map((e) => `${e.name} (${e.hp}hp)`).join(", "), "err");
    const near = enemies.filter((e) => cheb(e, pos) > 1 && cheb(e, pos) <= 3);
    if (near.length) emit("Nearby: " + near.map((e) => e.name).join(", "), "dim");
    if (stairsPos && pos.x === stairsPos.x && pos.y === stairsPos.y) emit("A stairway down. (descend)", "take");
    if (grid[pos.y][pos.x] === "A") emit("The Archive glows here.", "take");
  }

  function drawMap() {
    const lines = [];
    for (let y = 0; y < H; y++) {
      let row = "";
      for (let x = 0; x < W; x++) {
        if (x === pos.x && y === pos.y) { row += "@"; continue; }
        if (!seen.has(x + "," + y)) { row += " "; continue; }
        const e = enemyAt(x, y);
        if (e && cheb(e, pos) <= 3) { row += e.glyph; continue; }
        row += grid[y][x];
      }
      lines.push(row);
    }
    emit("Map — @ you, > stairs, A archive, letters = foes, blank = unseen", "dim");
    for (const ln of lines) emit(esc(ln), "hdr");
  }

  // ---- intro ----
  function emitIntro() {
    hr();
    emit(`DEPTH ${depth} OF ${maxDepth} · seed ${seed}`, "room");
    emit("Move with n/s/e/w (or h/j/k/l). Walk into a foe to strike it. Type 'help'.", "dim");
    const here = items.filter((i) => Math.abs(i.x - pos.x) <= 3 && Math.abs(i.y - pos.y) <= 3);
    const foes = enemies.filter((e) => cheb(e, pos) <= 3);
    if (foes.length) emit("Something stirs nearby: " + foes.map((e) => e.name).join(", "), "err");
    if (here.length) emit("You sense " + here.length + " thing(s) of interest close by.", "dim");
    emit("", "dim");
  }

  // ---- command interpreter ----
  function exec(raw) {
    const text = String(raw || "").trim();
    if (!text) return { ok: false };
    emit(`<span class="dim">&gt; ${esc(text)}</span>`);
    const [verb, ...rest] = text.toLowerCase().split(/\s+/);
    const arg = rest.join(" ");

    if (DIRS[verb]) { const r = move(...DIRS[verb]); return r; }

    switch (verb) {
      case "help": case "?":
        emitHelp(); return { ok: true };
      case "look": case "l":
        look(); return { ok: true };
      case "map": case "m":
        drawMap(); return { ok: true };
      case "wait": case ".": case "rest":
        emit("You wait a beat…", "dim"); endTurn(); return { ok: true };
      case "attack": case "a": case "hit":
        const dir = DIRS[arg];
        if (!dir) { emit("Attack which way? (attack n)", "err"); return { ok: false }; }
        const e = enemyAt(pos.x + dir[0], pos.y + dir[1]);
        if (!e) { emit("There is nothing to strike there.", "err"); return { ok: false }; }
        attack(e); endTurn(); return { ok: true };
      case "potion": case "use": case "drink": case "p":
        potion(); return { ok: true };
      case "inventory": case "i": case "inv":
        emit(`Potions: ${state.potions} · ATK: ${state.atk} · Relics: ${state.relics.length}`, "hdr");
        for (const r of state.relics) emit(`  ✦ ${esc(r.title)}`, "dim");
        return { ok: true };
      case "descend": case "d": case "down":
        descend(); return { ok: true };
      case "stats":
        updateHud(); emit(hudEl.textContent, "hdr"); return { ok: true };
      case "seed":
        emit(`seed ${seed}`, "hdr"); return { ok: true };
      case "clear": case "cls":
        out.innerHTML = ""; return { ok: true };
      default:
        emit(`I don't know '${esc(verb)}'. Type 'help'.`, "err");
        return { ok: false };
    }
  }

  function emitHelp() {
    emit("Commands", "hdr");
    emit("  n s e w / h j k l      move one tile (walk into a foe to attack)");
    emit("  attack <dir>           strike without moving");
    emit("  wait / .               hold position (foes take a turn)");
    emit("  potion / p             drink a potion to heal");
    emit("  look / l               survey your surroundings");
    emit("  map / m                show the explored map");
    emit("  descend / d            take the stairs down");
    emit("  inventory / i          potions, attack, relics");
    emit("  stats · seed · clear");
    emit("Goal: descend three depths, reach the Archive, and gather relics.", "dim");
  }

  // ---- ui ----
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = input.value; input.value = "";
    exec(v);
    updateHud();
  });
  document.getElementById("helpBtn").addEventListener("click", () => { emitHelp(); });
  document.getElementById("mapBtn").addEventListener("click", () => { drawMap(); });
  document.getElementById("restartBtn").addEventListener("click", () => newRun());
  document.getElementById("againBtn").addEventListener("click", () => newRun());

  // ---- run lifecycle ----
  function newRun(forceSeed) {
    seed = forceSeed != null ? forceSeed : (Math.floor(Math.random() * 0xffffffff) >>> 0);
    rng = mulberry32(seed);
    depth = 1; turn = 0; relicIndex = 0;
    state.maxhp = data.player.hp; state.hp = data.player.hp; state.atk = data.player.atk;
    state.potions = 0; state.relics = []; state.won = false; state.dead = false; state.over = false;
    overlay.classList.add("hidden");
    out.innerHTML = "";
    emit(data.title + " — " + data.subtitle, "room");
    emit("A roguelike of a working life. Three depths, a handful of relics, and the things that stand in the way.", "dim");
    genDepth(1);
    emitIntro();
    updateHud();
    input.focus();
  }

  // ---- boot ----
  async function boot() {
    try {
      const res = await fetch("data/dungeon.json", { cache: "no-store" });
      data = await res.json();
    } catch (e) {
      emit("Failed to load dungeon.json — run 'make dungeon'.", "err");
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
      toStairs: () => { if (stairsPos) { pos = { ...stairsPos }; reveal(); return true; } return false; },
      toArchive: () => { if (archivePos) { pos = { ...archivePos }; reveal(); if (grid[pos.y][pos.x] === "A") win(); return true; } return false; },
      teleport: (x, y) => { if (passable(x, y)) { pos = { x, y }; reveal(); return true; } return false; },
      nearestEnemy: () => {
        if (!enemies.length) return null;
        const e = enemies.slice().sort((a, b) => cheb(a, pos) - cheb(b, pos))[0];
        return { x: e.x, y: e.y, name: e.name, hp: e.hp };
      },
      setAtk: (n) => { state.atk = n; updateHud(); },
      setHp: (n) => { state.hp = n; updateHud(); },
      killEnemies: () => { const n = enemies.length; enemies = []; return n; },
      heal: () => { state.hp = state.maxhp; },
      // connectivity of the current depth (all floor cells reachable from pos)
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
    };
  }

  boot();
})();