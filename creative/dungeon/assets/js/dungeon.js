/* The Delve — a text dungeon crawler over the CV. No dependencies. */
(() => {
  "use strict";

  const out = document.getElementById("out");
  const form = document.getElementById("form");
  const input = document.getElementById("cmd");
  const foundEl = document.getElementById("found");
  const wonOverlay = document.getElementById("won");
  const wonText = document.getElementById("wonText");

  let data = null;
  let roomId = null;
  const visited = new Set();
  const taken = new Set();       // item ids taken
  const inventory = [];          // {title, body}
  let won = false;
  let turns = 0;

  // ---- output ----
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }
  function emit(html) {
    const div = document.createElement("div");
    div.innerHTML = html;
    out.appendChild(div);
    out.scrollTop = out.scrollHeight;
  }
  function line(text, cls) { emit(cls ? `<span class="${cls}">${text}</span>` : text); }

  // ---- helpers ----
  const DIRS = {
    n: "n", s: "s", e: "e", w: "w",
    north: "n", south: "s", east: "e", west: "w",
    up: "n", down: "s", right: "e", left: "w",
  };
  const DIRNAME = { n: "north", s: "south", e: "east", w: "west" };

  function room() { return data.rooms[roomId]; }
  function remainingItems() { return room().items.filter((it) => !taken.has(it.id)); }

  function describeRoom() {
    const r = room();
    visited.add(roomId);
    line(`— ${esc(r.name)} —`, "room");
    line(esc(r.desc));
    const rem = remainingItems();
    if (rem.length) {
      line("", "");
      line("You see:", "dim");
      rem.forEach((it, i) => line(`  ${i + 1}. ${esc(it.title)}`, "hi"));
    } else {
      line("");
      line("Nothing left to take here.", "dim");
    }
    const exits = Object.keys(r.exits);
    line("");
    line(`Exits: ${exits.map((d) => DIRNAME[d]).join(", ")}`, "dim");
  }

  function updateHud() {
    foundEl.textContent = `loot ${taken.size}/${data.total}`;
  }

  function findItem(arg, pool) {
    if (!arg) return null;
    const q = arg.toLowerCase();
    // by number
    const n = parseInt(arg, 10);
    if (!isNaN(n) && n >= 1 && n <= pool.length) return pool[n - 1];
    // exact then substring title match
    return (
      pool.find((it) => it.title.toLowerCase() === q) ||
      pool.find((it) => it.title.toLowerCase().includes(q)) ||
      null
    );
  }

  function take(it) {
    taken.add(it.id);
    inventory.push(it);
    updateHud();
    line(`You take: ${esc(it.title)}`, "take");
    for (const b of it.body) if (b) line(`    ${esc(b)}`, "dim");
    if (taken.size >= data.total) win();
  }

  function win() {
    won = true;
    const c = data.contact || {};
    wonText.innerHTML = `You have gathered every relic of a working life — ${data.total} facts across ${Object.keys(data.rooms).length} chambers.<br><br>${esc(c.name)} · ${esc(c.location)}<br>${esc(c.email)}`;
    wonOverlay.classList.remove("hidden");
  }

  // ---- map ----
  function drawMap() {
    const rooms = Object.values(data.rooms);
    const xs = rooms.map((r) => r.x), ys = rooms.map((r) => r.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const grid = [];
    for (let y = minY; y <= maxY; y++) {
      const row = [];
      for (let x = minX; x <= maxX; x++) {
        const r = rooms.find((rr) => rr.x === x && rr.y === y);
        if (!r) { row.push("   "); continue; }
        if (r.id === roomId) row.push("[@]");
        else if (visited.has(r.id)) row.push("[·]");
        else row.push("[?]");
      }
      grid.push(row.join(" "));
    }
    line("Map  [@]you [·]visited [?]unknown", "dim");
    for (const g of grid) line("  " + g, "hdr");
  }

  // ---- command interpreter ----
  function exec(raw) {
    const text = String(raw || "").trim();
    if (!text) return { ok: false };
    line(`<span class="dim">&gt; ${esc(text)}</span>`);
    const parts = text.toLowerCase().split(/\s+/);
    const verb = parts[0];
    const arg = parts.slice(1).join(" ");
    turns++;

    // movement shortcuts
    if (DIRS[verb] && Object.keys(room().exits).length) {
      return go(DIRS[verb]);
    }

    switch (verb) {
      case "help": case "?": case "commands":
        line("Commands:", "hdr");
        line("  look / l            describe the room again");
        line("  go <dir> or n/s/e/w move (north, south, east, west)");
        line("  take <item>         pick up an item (or 'take all')");
        line("  examine <item>      read an item without taking (x)");
        line("  inventory / i       what you carry");
        line("  map / m             show the map");
        line("  stats               progress");
        line("  clear               clear the screen");
        return { ok: true };

      case "look": case "l": case "room":
        describeRoom(); return { ok: true };

      case "go": case "move": case "walk":
        if (!arg) { line("Go where? (n, s, e, w)", "err"); return { ok: false }; }
        return go(DIRS[arg]);
      case "n": case "s": case "e": case "w":
      case "north": case "south": case "east": case "west":
        return go(DIRS[verb]);

      case "take": case "get": case "grab": case "pickup":
        if (!arg) { line("Take what? Try 'take all'.", "err"); return { ok: false }; }
        if (arg === "all" || arg === "everything") {
          const rem = remainingItems();
          if (!rem.length) { line("Nothing to take here.", "err"); return { ok: false }; }
          for (const it of rem.slice()) take(it);
          return { ok: true };
        }
        const it = findItem(arg, remainingItems());
        if (!it) { line(`No '${esc(arg)}' here.`, "err"); return { ok: false }; }
        take(it); return { ok: true };

      case "examine": case "x": case "read": case "inspect":
        const pool = [...remainingItems(), ...inventory];
        const ex = findItem(arg, pool);
        if (!ex) { line(`No '${esc(arg)}' to examine.`, "err"); return { ok: false }; }
        line(esc(ex.title), "take");
        for (const b of ex.body) if (b) line(`    ${esc(b)}`, "dim");
        return { ok: true };

      case "inventory": case "i": case "inv":
        if (!inventory.length) { line("You carry nothing yet.", "dim"); return { ok: true }; }
        line("You carry:", "hdr");
        inventory.forEach((it) => line(`  - ${esc(it.title)}`, "dim"));
        return { ok: true };

      case "map": case "m":
        drawMap(); return { ok: true };

      case "stats":
        line(`${taken.size}/${data.total} facts gathered · room: ${esc(room().name)} · turns: ${turns}`, "hdr");
        return { ok: true };

      case "clear": case "cls":
        out.innerHTML = ""; return { ok: true };

      default:
        line(`I don't know '${esc(verb)}'. Type 'help'.`, "err");
        return { ok: false };
    }

    function go(dir) {
      const r = room();
      const dest = r.exits[dir];
      if (!dest) { line(`You can't go ${DIRNAME[dir] || dir} from here.`, "err"); return { ok: false }; }
      roomId = dest;
      line("");
      describeRoom();
      return { ok: true };
    }
  }

  // ---- UI ----
  function submit(text) {
    exec(text);
    updateHud();
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const v = input.value;
    input.value = "";
    submit(v);
  });

  document.getElementById("helpBtn").addEventListener("click", () => exec("help"));
  document.getElementById("mapBtn").addEventListener("click", () => exec("map"));
  document.getElementById("againBtn").addEventListener("click", () => location.reload());

  // ---- boot ----
  async function boot() {
    try {
      const res = await fetch("data/dungeon.json");
      data = await res.json();
    } catch (e) {
      line("Failed to load dungeon.json", "err");
      return;
    }
    roomId = data.start;
    updateHud();
    line(data.title, "room");
    line("A text dungeon of a working life. Type 'help' for commands.", "dim");
    line("");
    describeRoom();
    input.focus();

    window.__DUNGEON_DEBUG__ = () => ({ room: roomId, visited: [...visited], taken: [...taken], found: taken.size, total: data.total, won, turns });
    window.__DUNGEON_TEST__ = { cmd: (s) => { const r = exec(s); updateHud(); return r; }, go: (s) => exec("go " + s), take: (s) => exec("take " + s) };
  }

  boot();
})();