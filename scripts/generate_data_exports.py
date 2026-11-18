#!/usr/bin/env python3
"""Export cv-data.yml to many downloadable data formats.

Writes to creative/data/ (served at /creative/data/):
  cv.md          human-readable Markdown
  cv.qmd         Quarto Markdown (renders to PDF/HTML)
  cv.tex         standalone LaTeX
  cv.json        the CV as nested JSON
  cv.xml         the CV as XML
  cv.csv         tidy long CSV (path,value) — handles the hierarchy
  cv.py          the CV as a Python dict literal
  cv.mysql.sql   MySQL: CREATE DATABASE + tables + rows (importable)
  cv-dump.sql    MySQL data-only dump (INSERTs; assumes schema)
  index.html     a download page listing everything

  python3 scripts/generate_data_exports.py
"""

from __future__ import annotations

import csv
import html
import io
import json
import os
import pprint
import yaml

OUT = "creative/data"


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f) or {}


def s(v) -> str:
    return "" if v is None else str(v).strip()


def joined(v) -> str:
    if isinstance(v, (list, tuple)):
        return "\n".join(s(x) for x in v if s(x))
    return s(v)


# ---------------------------------------------------------------- Markdown
def to_markdown(cv: dict) -> str:
    p = cv.get("personal", {}) or {}
    out = [f"# {s(p.get('name'))}", ""]
    contact = " · ".join(x for x in [s(p.get("location")), s(p.get("email")), s(p.get("phone"))] if x)
    if contact:
        out.append(contact + "  ")
    links = " · ".join(x for x in [s(p.get("linkedin")), s(p.get("github")), s(p.get("portfolio")), s(p.get("education_platform"))] if x)
    if links:
        out.append(links)
    out.append("")

    def h2(t):
        out.extend([f"## {t}", ""])

    summary = s((cv.get("summary") or {}).get("main"))
    if summary:
        h2("Summary")
        out.extend([summary, ""])

    if cv.get("experience"):
        h2("Experience")
        for j in cv["experience"]:
            out.append(f"### {s(j.get('title'))}")
            meta = " · ".join(x for x in [s(j.get("organization")), s(j.get("location")), s(j.get("period"))] if x)
            if meta:
                out.append(f"*{meta}*")
            for r in j.get("responsibilities", []) or []:
                out.append(f"- {s(r)}")
            out.append("")

    if cv.get("education"):
        h2("Education")
        for e in cv["education"]:
            line = f"- **{s(e.get('degree'))}**"
            if e.get("field"):
                line += f" ({s(e.get('field'))})"
            line += f" — {s(e.get('institution'))}, {s(e.get('year'))}"
            out.append(line)
            if e.get("thesis"):
                out.append(f"  - Thesis: {s(e.get('thesis'))}")
        out.append("")

    skills = cv.get("skills") or {}
    if skills:
        h2("Skills")
        for group, val in skills.items():
            out.append(f"**{group.replace('_', ' ').title()}**")
            if isinstance(val, dict):
                for sub, vals in val.items():
                    vv = vals if isinstance(vals, list) else [vals]
                    out.append(f"- {sub.replace('_', ' ').title()}: {', '.join(s(x) for x in vv)}")
            else:
                vv = val if isinstance(val, list) else [val]
                out.append(f"- {', '.join(s(x) for x in vv)}")
        out.append("")

    if cv.get("projects"):
        h2("Projects")
        for pr in cv["projects"]:
            yr = f" ({s(pr.get('year'))})" if pr.get("year") else ""
            out.append(f"- **{s(pr.get('name'))}**{yr}: {s(pr.get('description'))}")
        out.append("")

    if cv.get("achievements"):
        h2("Achievements")
        for a in cv["achievements"]:
            out.append(f"- {s(a)}")
        out.append("")

    pubs = cv.get("publications") or {}
    if pubs:
        h2("Publications")
        for b in pubs.get("books", []) or []:
            out.append(f"- **{s(b.get('title'))}** — {s(b.get('description'))} ({s(b.get('license'))})")
        for c in pubs.get("conferences", []) or []:
            out.append(f"- {s(c.get('authors'))} ({s(c.get('year'))}). *{s(c.get('title'))}*. {s(c.get('venue'))}, {s(c.get('location'))}.")
        for t in pubs.get("thesis", []) or []:
            out.append(f"- {s(t.get('title'))} — {s(t.get('type'))}, {s(t.get('year'))}")
        out.append("")

    teaching = cv.get("teaching") or {}
    if teaching:
        h2("Teaching")
        ph = teaching.get("philosophy") or {}
        if ph.get("core"):
            out.append(f"- {s(ph.get('core'))}")
        if ph.get("framework"):
            out.append(f"- {s(ph.get('framework'))}")
        for m in teaching.get("satisfaction", []) or []:
            out.append(f"- {s(m.get('metric'))}: {s(m.get('details'))}")
        for inn in teaching.get("innovations", []) or []:
            out.append(f"- **{s(inn.get('name'))}** — {s(inn.get('description'))}")
        out.append("")

    if cv.get("service"):
        h2("Service")
        for group, items in (cv["service"] or {}).items():
            for it in items or []:
                meta = " · ".join(x for x in [s(it.get("organization") or it.get("project")), s(it.get("year") or it.get("period"))] if x)
                out.append(f"- **{s(it.get('role'))}** — {meta}")
        out.append("")

    if cv.get("certifications"):
        h2("Certifications")
        for c in cv["certifications"]:
            out.append(f"- {s(c.get('name'))} ({s(c.get('year'))})")
        out.append("")

    if cv.get("memberships"):
        h2("Memberships")
        for m in cv["memberships"]:
            out.append(f"- {s(m.get('organization'))} — {s(m.get('status'))} ({s(m.get('year'))})")
        out.append("")

    if cv.get("interests"):
        h2("Interests")
        out.append(", ".join(s(i) for i in cv["interests"]))
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def to_qmd(cv: dict) -> str:
    p = cv.get("personal", {}) or {}
    front = (
        "---\n"
        f'title: "{s(p.get("name"))}"\n'
        'subtitle: "Curriculum Vitae"\n'
        "format:\n"
        "  html:\n"
        "    toc: true\n"
        "  pdf: default\n"
        "---\n\n"
    )
    return front + to_markdown(cv)


# ---------------------------------------------------------------- LaTeX
def tex(s_val) -> str:
    conv = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(conv.get(c, c) for c in s(s_val))


def to_latex(cv: dict) -> str:
    p = cv.get("personal", {}) or {}
    L = [
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[margin=2cm]{geometry}",
        r"\usepackage{enumitem}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{lmodern}",
        r"\setlist[itemize]{leftmargin=1.2em,itemsep=1pt,topsep=2pt}",
        r"\pagestyle{empty}",
        r"\setlength{\parindent}{0pt}",
        r"\begin{document}",
        r"\begin{center}",
        r"{\LARGE \textbf{" + tex(p.get("name")) + r"}}\\[4pt]",
        " · ".join(tex(x) for x in [p.get("location"), p.get("email"), p.get("phone")] if s(x)) + r"\\",
        " · ".join(tex(x) for x in [p.get("linkedin"), p.get("github"), p.get("portfolio")] if s(x)),
        r"\end{center}",
    ]

    def section(title):
        L.append(r"\vspace{4pt}\hrule\vspace{4pt}")
        L.append(r"\subsection*{" + tex(title) + "}")

    summary = s((cv.get("summary") or {}).get("main"))
    if summary:
        section("Summary")
        L.append(tex(summary))

    if cv.get("experience"):
        section("Experience")
        for j in cv["experience"]:
            L.append(r"\textbf{" + tex(j.get("title")) + r"} \hfill " + tex(j.get("period")))
            meta = " — ".join(tex(x) for x in [j.get("organization"), j.get("location")] if s(x))
            if meta:
                L.append(r"\textit{" + meta + r"}")
            resp = [s(r) for r in j.get("responsibilities", []) or [] if s(r)]
            if resp:
                L.append(r"\begin{itemize}")
                for r in resp:
                    L.append(r"\item " + tex(r))
                L.append(r"\end{itemize}")
            L.append("")

    if cv.get("education"):
        section("Education")
        L.append(r"\begin{itemize}")
        for e in cv["education"]:
            line = r"\textbf{" + tex(e.get("degree")) + "}"
            if e.get("field"):
                line += " (" + tex(e.get("field")) + ")"
            line += " — " + tex(e.get("institution")) + ", " + tex(e.get("year"))
            if e.get("thesis"):
                line += r". \textit{" + tex(e.get("thesis")) + "}"
            L.append(r"\item " + line)
        L.append(r"\end{itemize}")

    skills = cv.get("skills") or {}
    if skills:
        section("Skills")
        for group, val in skills.items():
            parts = []
            if isinstance(val, dict):
                for sub, vals in val.items():
                    vv = vals if isinstance(vals, list) else [vals]
                    parts.append(tex(sub.replace("_", " ").title()) + ": " + ", ".join(tex(x) for x in vv))
            else:
                vv = val if isinstance(val, list) else [val]
                parts = [", ".join(tex(x) for x in vv)]
            L.append(r"\textbf{" + tex(group.replace("_", " ").title()) + "}: " + "; ".join(parts))

    if cv.get("projects"):
        section("Projects")
        L.append(r"\begin{itemize}")
        for pr in cv["projects"]:
            yr = " (" + tex(pr.get("year")) + ")" if pr.get("year") else ""
            L.append(r"\item \textbf{" + tex(pr.get("name")) + "}" + yr + ": " + tex(pr.get("description")))
        L.append(r"\end{itemize}")

    if cv.get("achievements"):
        section("Achievements")
        L.append(r"\begin{itemize}")
        for a in cv["achievements"]:
            L.append(r"\item " + tex(a))
        L.append(r"\end{itemize}")

    L.append(r"\end{document}")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- flatten (CSV)
def flatten(obj, prefix=""):
    rows = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            rows.extend(flatten(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            rows.extend(flatten(v, f"{prefix}[{i}]"))
    else:
        rows.append((prefix, obj))
    return rows


def to_csv(cv: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["path", "value"])
    for path, val in flatten(cv):
        w.writerow([path, "" if val is None else val])
    return buf.getvalue()


# ---------------------------------------------------------------- XML
def xml_tag(name: str) -> str:
    import re
    t = re.sub(r"[^A-Za-z0-9_.-]", "_", str(name))
    if not t or not (t[0].isalpha() or t[0] == "_"):
        t = "_" + t
    return t


def to_xml(obj, tag="cv", indent=0) -> str:
    pad = "  " * indent
    t = xml_tag(tag)
    if isinstance(obj, dict):
        inner = "\n".join(to_xml(v, k, indent + 1) for k, v in obj.items())
        return f"{pad}<{t}>\n{inner}\n{pad}</{t}>"
    if isinstance(obj, list):
        inner = "\n".join(to_xml(v, "item", indent + 1) for v in obj)
        return f"{pad}<{t}>\n{inner}\n{pad}</{t}>"
    return f"{pad}<{t}>{html.escape('' if obj is None else str(obj))}</{t}>"


def to_python(cv: dict) -> str:
    body = pprint.pformat(cv, sort_dicts=False, width=100)
    return (
        '"""Michael Borck CV as a Python dict. Generated from data/cv-data.yml."""\n\n'
        "CV = " + body + "\n\n"
        'if __name__ == "__main__":\n'
        "    import json, sys\n"
        "    json.dump(CV, sys.stdout, indent=2, default=str)\n"
    )


# ---------------------------------------------------------------- MySQL
def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + s(v).replace("\\", "\\\\").replace("'", "''") + "'"


def sql_rows(cv: dict):
    """Return {table: (columns, [rows])} for a relational MySQL mapping."""
    p = cv.get("personal", {}) or {}
    tables = {}

    def add(table, cols, rows):
        tables[table] = (cols, rows)

    add("personal", ["id", "name", "email", "phone", "linkedin", "github", "portfolio", "location"],
        [(1, p.get("name"), p.get("email"), p.get("phone"), p.get("linkedin"), p.get("github"), p.get("portfolio"), p.get("location"))])
    add("summary", ["id", "summary_text"], [(1, (cv.get("summary") or {}).get("main"))])

    rows = []
    for i, j in enumerate(cv.get("experience", []) or [], 1):
        rows.append((i, i, j.get("title"), j.get("organization"), j.get("location"), j.get("period"), joined(j.get("responsibilities"))))
    add("experience", ["id", "sort", "title", "organization", "location", "period", "responsibilities"], rows)

    rows = []
    for i, e in enumerate(cv.get("education", []) or [], 1):
        rows.append((i, i, e.get("degree"), e.get("field"), e.get("institution"), e.get("year"), e.get("thesis")))
    add("education", ["id", "sort", "degree", "field", "institution", "year", "thesis"], rows)

    rows = []
    n = 0
    for group, val in (cv.get("skills") or {}).items():
        if isinstance(val, dict):
            for sub, vals in val.items():
                vv = vals if isinstance(vals, list) else [vals]
                n += 1
                rows.append((n, n, group, sub, ", ".join(s(x) for x in vv)))
        else:
            vv = val if isinstance(val, list) else [val]
            n += 1
            rows.append((n, n, group, None, ", ".join(s(x) for x in vv)))
    add("skill", ["id", "sort", "category", "subcategory", "names"], rows)

    rows = []
    for i, pr in enumerate(cv.get("projects", []) or [], 1):
        rows.append((i, i, pr.get("name"), pr.get("description"), pr.get("year")))
    add("project", ["id", "sort", "name", "description", "year"], rows)

    rows = []
    for i, a in enumerate(cv.get("achievements", []) or [], 1):
        rows.append((i, i, a))
    add("achievement", ["id", "sort", "achievement_text"], rows)

    rows = []
    n = 0
    pubs = cv.get("publications") or {}
    for b in pubs.get("books", []) or []:
        n += 1; rows.append((n, n, "book", b.get("title"), None, None, None, b.get("description"), b.get("license")))
    for c in pubs.get("conferences", []) or []:
        n += 1; rows.append((n, n, "conference", c.get("title"), c.get("authors"), c.get("year"), c.get("venue"), None, None))
    for t in pubs.get("thesis", []) or []:
        n += 1; rows.append((n, n, "thesis", t.get("title"), None, t.get("year"), t.get("fields"), t.get("description"), None))
    for h in pubs.get("honours", []) or []:
        n += 1; rows.append((n, n, "honour", h.get("title"), None, h.get("year"), h.get("institution"), None, None))
    add("publication", ["id", "sort", "kind", "title", "authors", "year", "venue", "description", "license"], rows)

    rows = []
    for i, c in enumerate(cv.get("certifications", []) or [], 1):
        rows.append((i, i, c.get("name"), c.get("year")))
    add("certification", ["id", "sort", "name", "year"], rows)

    rows = []
    n = 0
    for group, items in (cv.get("service") or {}).items():
        for it in items or []:
            n += 1
            rows.append((n, n, group, it.get("role"), it.get("organization"), it.get("project"), it.get("year"), it.get("period")))
    add("service", ["id", "sort", "category", "role", "organization", "project", "year", "period"], rows)

    rows = []
    for i, m in enumerate(cv.get("memberships", []) or [], 1):
        rows.append((i, i, m.get("organization"), m.get("status"), m.get("year"), m.get("note")))
    add("membership", ["id", "sort", "organization", "status", "year", "note"], rows)

    rows = []
    for i, it in enumerate(cv.get("interests", []) or [], 1):
        rows.append((i, i, it))
    add("interest", ["id", "sort", "name"], rows)

    teaching = cv.get("teaching") or {}
    rows = []
    for i, m in enumerate(teaching.get("satisfaction", []) or [], 1):
        rows.append((i, i, m.get("metric"), m.get("details")))
    add("teaching_satisfaction", ["id", "sort", "metric", "details"], rows)

    rows = []
    for i, inn in enumerate(teaching.get("innovations", []) or [], 1):
        rows.append((i, i, inn.get("name"), inn.get("description")))
    add("teaching_innovation", ["id", "sort", "name", "description"], rows)

    return tables


SQL_TYPES = {
    "id": "INT NOT NULL",
    "sort": "INT NOT NULL",
    "summary_text": "TEXT",
}


def sql_ddl(tables) -> str:
    out = ["-- Schema for the CV database (MySQL 8+)", "SET FOREIGN_KEY_CHECKS=0;"]
    for name in tables:
        out.append(f"DROP TABLE IF EXISTS `{name}`;")
    for name, (cols, _rows) in tables.items():
        defs = []
        for c in cols:
            if c == "id":
                defs.append("`id` INT NOT NULL")
            elif c == "sort":
                defs.append("`sort` INT NOT NULL DEFAULT 0")
            else:
                defs.append(f"`{c}` " + ("TEXT" if c in ("responsibilities", "summary_text", "description", "achievement_text", "thesis") else "VARCHAR(255)"))
        defs.append("PRIMARY KEY (`id`)")
        out.append(f"CREATE TABLE `{name}` (\n  " + ",\n  ".join(defs) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
    out.append("SET FOREIGN_KEY_CHECKS=1;")
    return "\n".join(out)


def sql_inserts(tables) -> str:
    out = []
    for name, (cols, rows) in tables.items():
        if not rows:
            continue
        collist = ", ".join(f"`{c}`" for c in cols)
        out.append(f"-- {name}")
        for row in rows:
            vals = ", ".join(q(v) for v in row)
            out.append(f"INSERT INTO `{name}` ({collist}) VALUES ({vals});")
        out.append("")
    return "\n".join(out)


def to_mysql_full(tables) -> str:
    return (
        "-- Michael Borck CV — MySQL import file\n"
        "CREATE DATABASE IF NOT EXISTS `cv` CHARACTER SET utf8mb4;\n"
        "USE `cv`;\n\n"
        + sql_ddl(tables) + "\n\n"
        + sql_inserts(tables)
    )


def to_sql_dump(tables) -> str:
    return (
        "-- Michael Borck CV — data-only dump (INSERTs).\n"
        "-- Assumes the schema from cv.mysql.sql already exists.\n"
        "SET FOREIGN_KEY_CHECKS=0;\n\n"
        + sql_inserts(tables)
        + "\nSET FOREIGN_KEY_CHECKS=1;\n"
    )


# ---------------------------------------------------------------- writer
def write(path, content):
    full = os.path.join(OUT, path)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return len(content.encode("utf-8"))


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>CV data — download</title>
<meta name="description" content="Download Michael Borck's CV as Markdown, Quarto, LaTeX, JSON, XML, CSV, Python dict, or MySQL." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
<style>
  :root{{ --ink:#0a0a0b; --panel:#14161a; --line:#2a2d34; --text:#e8e6e3; --muted:#9a9aa8; --gold:#ffcf6b; --cyan:#6ee0d8; --mono:"JetBrains Mono",monospace; }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--ink);color:var(--text);font-family:var(--mono);padding:32px 20px;min-height:100%}}
  .wrap{{max-width:760px;margin:0 auto}}
  .eyebrow{{font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--cyan);margin-bottom:8px}}
  h1{{font-size:22px;margin-bottom:6px}}
  .sub{{color:var(--muted);font-size:12px;margin-bottom:22px}}
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
  @media(max-width:600px){{.grid{{grid-template-columns:1fr}}}}
  a.file{{display:flex;justify-content:space-between;gap:12px;align-items:center;text-decoration:none;color:var(--text);background:var(--panel);border:2px solid var(--line);border-radius:8px;padding:12px 14px;transition:border-color .12s,transform .08s}}
  a.file:hover{{border-color:var(--gold);transform:translateY(-1px)}}
  .fname{{font-weight:700;color:var(--gold)}}
  .fdesc{{color:var(--muted);font-size:11px;margin-top:3px}}
  .fsize{{color:#6f7278;font-size:10px;white-space:nowrap}}
  .api{{margin-top:22px;font-size:12px;color:var(--muted);line-height:1.7}}
  .api a{{color:var(--cyan);text-decoration:none}}
  .backlink{{position:fixed;top:12px;right:14px;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}}
  .backlink:hover{{color:var(--gold);border-color:var(--gold)}}
</style>
</head>
<body>
<a class="backlink" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="eyebrow">Download · one YAML, many formats</div>
  <h1>The CV as data</h1>
  <div class="sub">Generated from <code>data/cv-data.yml</code>. Grab whatever your tool needs.</div>
  <div class="grid">
{items}
  </div>
  <div class="api">
    Prefer the live JSON API? <a href="https://api.resume.borck.dev/docs">api.resume.borck.dev/docs</a>
    — endpoints: <code>/profile</code> <code>/experience</code> <code>/skills</code> <code>/education</code>
    <code>/projects</code> <code>/publications</code> <code>/achievements</code> <code>/contact</code> <code>/export</code>.
  </div>
</div>
</body>
</html>
"""

FILES = [
    ("cv.md", "Markdown", "Human-readable CV in Markdown."),
    ("cv.qmd", "Quarto", "Quarto Markdown — render to PDF/HTML with Quarto."),
    ("cv.tex", "LaTeX", "Standalone LaTeX document (compile with pdflatex)."),
    ("cv.json", "JSON", "The full CV as nested JSON."),
    ("cv.xml", "XML", "The full CV as XML."),
    ("cv.csv", "CSV", "Tidy long format: path,value — one row per leaf."),
    ("cv.py", "Python dict", "The CV as a Python dict literal (CV = {...})."),
    ("cv.mysql.sql", "MySQL (full)", "CREATE DATABASE + tables + rows; import directly."),
    ("cv-dump.sql", "SQL dump", "INSERT-only data dump (assumes schema)."),
]


def build_index(sizes) -> str:
    items = []
    for fname, label, desc in FILES:
        kb = sizes.get(fname, 0) / 1024
        items.append(
            f'    <a class="file" href="{fname}" download>\n'
            f'      <span><span class="fname">{label}</span><span class="fdesc">{desc}</span></span>\n'
            f'      <span class="fsize">{fname} · {kb:.1f} KB</span>\n'
            f'    </a>'
        )
    return INDEX_TEMPLATE.format(items="\n".join(items))


def main() -> None:
    cv = load_cv()
    os.makedirs(OUT, exist_ok=True)
    sizes = {}
    sizes["cv.md"] = write("cv.md", to_markdown(cv))
    sizes["cv.qmd"] = write("cv.qmd", to_qmd(cv))
    sizes["cv.tex"] = write("cv.tex", to_latex(cv))
    sizes["cv.json"] = write("cv.json", json.dumps(cv, indent=2, ensure_ascii=False, default=str) + "\n")
    sizes["cv.xml"] = write("cv.xml", '<?xml version="1.0" encoding="UTF-8"?>\n' + to_xml(cv, "cv") + "\n")
    sizes["cv.csv"] = write("cv.csv", to_csv(cv))
    sizes["cv.py"] = write("cv.py", to_python(cv))

    tables = sql_rows(cv)
    sizes["cv.mysql.sql"] = write("cv.mysql.sql", to_mysql_full(tables))
    sizes["cv-dump.sql"] = write("cv-dump.sql", to_sql_dump(tables))

    write("index.html", build_index(sizes))

    print(f"✓ Data exports -> {OUT}/")
    for fname, label, _ in FILES:
        print(f"  {fname:16} {label:12} {sizes[fname]/1024:6.1f} KB")


if __name__ == "__main__":
    main()