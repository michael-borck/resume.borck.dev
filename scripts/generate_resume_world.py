#!/usr/bin/env python3
"""Generate Resume World data from cv-data.yml.

Flattens the CV into a game world: a set of regions (from the `world:` block in
cv-data.yml) each containing landmark markers, one per CV entry. The canvas game
in creative/world/index.html loads this JSON and renders the overworld.

  python3 scripts/generate_resume_world.py
  -> creative/world/data/world-data.json
"""

from __future__ import annotations

import json
import os
import re
import yaml

# Which icon sprite represents each kind of marker.
ICON_BY_KIND = {
    "experience": "keep",
    "education": "tower",
    "skill": "dojo",
    "project": "chest",
    "achievement": "scroll",
    "publication": "scroll",
    "teaching": "dojo",
    "feedback": "signpost",
    "innovation": "signpost",
    "service": "ruins",
    "membership": "ruins",
    "interest": "beach",
    "certification": "scroll",
    "contact": "camp",
}


def load_cv() -> dict:
    with open("data/cv-data.yml", "r") as f:
        return yaml.safe_load(f)


def clean(text) -> str:
    """Collapse a value to a single clean line."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def split_label(text: str) -> tuple[str, str]:
    """Split 'Label - rest' / 'Label — rest' into a bold title + detail."""
    text = clean(text)
    m = re.match(r"^(.{2,60}?)\s*[—–-]\s+(.+)$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text, ""


def para(text: str) -> str:
    """Turn a string or list into a list of paragraphs."""
    if text is None:
        return []
    if isinstance(text, list):
        return [clean(t) for t in text if clean(t)]
    return [clean(text)]


def experience_markers(cv: dict) -> list[dict]:
    out = []
    for job in cv.get("experience", []):
        title = clean(job.get("title"))
        org = clean(job.get("organization"))
        period = clean(job.get("period"))
        location = clean(job.get("location"))
        resp = [clean(r) for r in job.get("responsibilities", []) if clean(r)]
        details = []
        for r in resp:
            head, tail = split_label(r)
            details.append({"label": head, "text": tail} if tail else {"label": "", "text": head})
        subtitle = " · ".join(x for x in [org, location, period] if x)
        out.append({
            "name": title or org or "Role",
            "subtitle": subtitle,
            "icon": ICON_BY_KIND["experience"],
            "kind": "experience",
            "body": ([f"{title} — {org} ({period})"] if org else []) + resp,
        })
    return out


def education_markers(cv: dict) -> list[dict]:
    out = []
    for ed in cv.get("education", []):
        degree = clean(ed.get("degree"))
        field = clean(ed.get("field"))
        inst = clean(ed.get("institution"))
        year = clean(ed.get("year"))
        thesis = clean(ed.get("thesis"))
        title = degree + (f" ({field})" if field and field.lower() not in degree.lower() else "")
        sub = " · ".join(x for x in [inst, year] if x)
        body = [f"{title} — {inst}, {year}"]
        if thesis:
            body.append(f"Thesis: {thesis}")
        out.append({
            "name": title or "Qualification",
            "subtitle": sub,
            "icon": ICON_BY_KIND["education"],
            "kind": "education",
            "body": body,
        })
    return out


def skill_markers(cv: dict) -> list[dict]:
    out = []
    skills = cv.get("skills", {})
    for group, items in skills.items():
        if isinstance(items, dict):
            for sub, vals in items.items():
                values = vals if isinstance(vals, list) else [vals]
                out.append({
                    "name": f"{group.title()} · {sub.title()}",
                    "subtitle": ", ".join(clean(v) for v in values),
                    "icon": ICON_BY_KIND["skill"],
                    "kind": "skill",
                    "body": [f"{group.title()} — {sub.title()}: " + ", ".join(clean(v) for v in values)],
                })
        else:
            values = items if isinstance(items, list) else [items]
            out.append({
                "name": group.title(),
                "subtitle": ", ".join(clean(v) for v in values),
                "icon": ICON_BY_KIND["skill"],
                "kind": "skill",
                "body": [f"{group.title()}: " + ", ".join(clean(v) for v in values)],
            })
    return out


def project_markers(cv: dict) -> list[dict]:
    out = []
    for p in cv.get("projects", []):
        name = clean(p.get("name"))
        desc = clean(p.get("description"))
        year = clean(p.get("year"))
        sub = " · ".join(x for x in [year, desc] if x)
        body = [f"{name}{(' (' + year + ')') if year else ''}"]
        if desc:
            body.append(desc)
        out.append({
            "name": name or "Project",
            "subtitle": sub,
            "icon": ICON_BY_KIND["project"],
            "kind": "project",
            "body": body,
        })
    return out


def achievement_markers(cv: dict) -> list[dict]:
    out = []
    for a in cv.get("achievements", []):
        head, tail = split_label(a)
        out.append({
            "name": head or "Achievement",
            "subtitle": tail,
            "icon": ICON_BY_KIND["achievement"],
            "kind": "achievement",
            "body": para(a),
        })
    pubs = cv.get("publications", {})
    for book in pubs.get("books", []) or []:
        out.append({
            "name": clean(book.get("title")),
            "subtitle": clean(book.get("description")),
            "icon": ICON_BY_KIND["publication"],
            "kind": "publication",
            "body": [clean(book.get("title")), clean(book.get("description")), clean(book.get("license"))],
        })
    for conf in pubs.get("conferences", []) or []:
        title = clean(conf.get("title"))
        authors = clean(conf.get("authors"))
        venue = clean(conf.get("venue"))
        year = clean(conf.get("year"))
        out.append({
            "name": title or "Paper",
            "subtitle": " · ".join(x for x in [venue, year] if x),
            "icon": ICON_BY_KIND["publication"],
            "kind": "publication",
            "body": [f"{title}", f"{authors} ({year})", f"{venue}"],
        })
    return out


def teaching_markers(cv: dict) -> list[dict]:
    out = []
    teaching = cv.get("teaching", {})
    phil = teaching.get("philosophy", {})
    core = clean(phil.get("core"))
    approach = clean(phil.get("approach"))
    if core:
        out.append({
            "name": clean(phil.get("framework")) or "Teaching Philosophy",
            "subtitle": core,
            "icon": ICON_BY_KIND["teaching"],
            "kind": "teaching",
            "body": [core, approach] if approach else [core],
        })
    for metric in teaching.get("satisfaction", []) or []:
        out.append({
            "name": clean(metric.get("metric")),
            "subtitle": clean(metric.get("details")),
            "icon": ICON_BY_KIND["teaching"],
            "kind": "teaching",
            "body": [clean(metric.get("metric")), clean(metric.get("details"))],
        })
    for inn in teaching.get("innovations", []) or []:
        out.append({
            "name": clean(inn.get("name")),
            "subtitle": clean(inn.get("description")),
            "icon": ICON_BY_KIND["innovation"],
            "kind": "innovation",
            "body": [clean(inn.get("name")), clean(inn.get("description"))],
        })
    return out


def service_markers(cv: dict) -> list[dict]:
    out = []
    service = cv.get("service", {})
    for group, items in service.items():
        for item in items or []:
            role = clean(item.get("role"))
            org = clean(item.get("organization") or item.get("project"))
            year = clean(item.get("year") or item.get("period"))
            out.append({
                "name": role or "Service",
                "subtitle": " · ".join(x for x in [org, year] if x),
                "icon": ICON_BY_KIND["service"],
                "kind": "service",
                "body": [f"{role} — {org} ({year})"],
            })
    for m in cv.get("memberships", []) or []:
        org = clean(m.get("organization"))
        status = clean(m.get("status"))
        year = clean(m.get("year"))
        out.append({
            "name": org or "Membership",
            "subtitle": " · ".join(x for x in [status, year] if x),
            "icon": ICON_BY_KIND["membership"],
            "kind": "membership",
            "body": [f"{org} — {status} ({year})"],
        })
    for c in cv.get("certifications", []) or []:
        out.append({
            "name": clean(c.get("name")),
            "subtitle": clean(c.get("year")),
            "icon": ICON_BY_KIND["certification"],
            "kind": "certification",
            "body": [clean(c.get("name")), clean(c.get("year"))],
        })
    return out


def interest_markers(cv: dict) -> list[dict]:
    out = []
    for it in cv.get("interests", []) or []:
        out.append({
            "name": clean(it),
            "subtitle": "A life beyond work",
            "icon": ICON_BY_KIND["interest"],
            "kind": "interest",
            "body": [f"Enjoys {clean(it)}"],
        })
    return out


SOURCE_BUILDERS = {
    "experience": experience_markers,
    "education": education_markers,
    "skills": skill_markers,
    "projects": project_markers,
    "achievements": achievement_markers,
    "publications": achievement_markers,
    "teaching": teaching_markers,
    "service": service_markers,
    "memberships": service_markers,
    "interests": interest_markers,
}


def build(cv: dict) -> dict:
    world_cfg = cv.get("world", {})
    personal = cv.get("personal", {})

    # Build each unique source once.
    built: dict[str, list[dict]] = {}
    for key, fn in SOURCE_BUILDERS.items():
        if key not in built:
            built[key] = fn(cv)

    regions = []
    for rcfg in world_cfg.get("regions", []):
        markers: list[dict] = []
        seen: set[str] = set()
        for source in rcfg.get("sources", []):
            for m in built.get(source, []):
                key = m["name"]
                if key in seen:
                    continue
                seen.add(key)
                markers.append(m)
                if len(markers) >= rcfg.get("spawns", 8):
                    break
            if len(markers) >= rcfg.get("spawns", 8):
                break
        regions.append({
            "id": rcfg["id"],
            "name": rcfg["name"],
            "subtitle": rcfg.get("subtitle", ""),
            "icon": rcfg.get("icon", "signpost"),
            "x": rcfg.get("map", {}).get("x", 50),
            "y": rcfg.get("map", {}).get("y", 50),
            "markers": markers,
        })

    # Contact hub at the spawn point.
    contact = {
        "id": "contact",
        "name": clean(personal.get("name")) or "Contact",
        "subtitle": "Start / get in touch",
        "icon": "camp",
        "x": world_cfg.get("spawn", {}).get("x", 50),
        "y": world_cfg.get("spawn", {}).get("y", 50),
        "kind": "contact",
        "body": [
            f"{clean(personal.get('name'))} — {clean(personal.get('location'))}",
            clean(personal.get("email")),
            clean(personal.get("phone")),
            clean(personal.get("linkedin")),
            clean(personal.get("github")),
            clean(personal.get("portfolio")),
        ],
        "links": {
            "email": clean(personal.get("email")),
            "linkedin": clean(personal.get("linkedin")),
            "github": clean(personal.get("github")),
            "portfolio": clean(personal.get("portfolio")),
        },
    }

    summary = clean(cv.get("summary", {}).get("main"))

    return {
        "title": f"{clean(personal.get('name'))}'s World",
        "subtitle": "An interactive map of a career",
        "spawn": world_cfg.get("spawn", {"x": 50, "y": 50}),
        "summary": summary,
        "contact": contact,
        "regions": regions,
    }


def main() -> None:
    cv = load_cv()
    world = build(cv)
    out_dir = "creative/world/data"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "world-data.json")
    with open(out_path, "w") as f:
        json.dump(world, f, indent=2)
    total = sum(len(r["markers"]) for r in world["regions"])
    print(f"✓ World generated: {out_path}")
    print(f"  - {len(world['regions'])} regions, {total} landmarks")


if __name__ == "__main__":
    main()