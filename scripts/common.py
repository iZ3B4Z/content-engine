#!/usr/bin/env python3
"""
common.py — single source of truth for Content Engine (merged architecture).

Holds: the two vault catalogs (methodology / client), the TYPE->DESTINATION routing,
folder shapes, canonical file sets, per-type markdown templates, frontmatter ordering,
and all deterministic file mechanics (resolution, rendering, writing, index/log/manifest).

The only judgment step in the system is classification (choosing a type + slot values).
Everything in this file is pure mechanics: given a structured record, it decides the path,
the filename, the frontmatter, and the body — with no model thinking required.

Pure Python stdlib. Cross-platform.
"""

import os
import re
import json
import datetime

MARKER = os.path.join("_system", "rules.md")     # vault marker (carries vault_type)
ROOT_MARKER = ".content-engine"                   # repo-root marker
SYSTEM_FILES = {"index.md", "log.md"}             # not treated as notes

# --------------------------------------------------------------------------------------
# Catalogs (CLOSED). Only these folders may exist in each vault's content area.
# shape: "fixed-files" | "flat-notes" | "closed-subfolders"
# --------------------------------------------------------------------------------------

CATALOG = {
    "methodology": {
        "taxonomies":  {"shape": "fixed-files",
                        "files": ["funnel-stages", "hook-types",
                                  "storytelling-structures", "visual-formats"]},
        "frameworks":  {"shape": "flat-notes"},
        "principles":  {"shape": "flat-notes"},
        "learnings":   {"shape": "flat-notes"},
        "templates":   {"shape": "closed-subfolders",
                        "subfolders": ["script-templates", "hook-formulas", "visual-formats"]},
    },
    "client": {
        "identity":    {"shape": "fixed-files",
                        "files": ["client-bio", "products", "audience",
                                  "business-model", "goals", "constraints"]},
        "voice":       {"shape": "fixed-files",
                        "files": ["tone", "idioms", "vocabulary",
                                  "prohibitions", "voice-samples"]},
        "corpus":      {"shape": "flat-notes"},
        "inspiration": {"shape": "flat-notes"},
        "outputs":     {"shape": "closed-subfolders",
                        "subfolders": ["scripts", "briefs"]},
    },
}

# --------------------------------------------------------------------------------------
# Routing: TYPE -> destination. mode decides how the markdown is created.
#   new_file            -> dated file  YYYY-MM-DD-<slug>.md in folder
#   new_file_named      -> <slug>.md (no date) in folder/<subfolder from slot>
#   section_in_file     -> upsert a "## <heading>" block inside a canonical file (slot picks file)
#   append_block        -> append a dated block to a fixed file
# --------------------------------------------------------------------------------------

TYPES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "types.json")

def _load_types():
    with open(TYPES_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_routes_and_templates():
    """Build ROUTES + TEMPLATES from types.json. CATALOG stays the structural source for
    folders; allowed files/subfolders are derived from it unless overridden in types.json."""
    defs = _load_types()
    routes, templates = {}, {}
    for vault, types in defs.items():
        routes[vault] = {}
        for t, d in types.items():
            entry = {"folder": d["folder"], "mode": d["mode"]}
            if d["mode"] == "section_in_file":
                entry["file_slot"] = d["file_slot"]
                entry["allowed_files"] = d.get("allowed_files") or CATALOG[vault][d["folder"]]["files"]
            elif d["mode"] == "new_file_named":
                entry["subfolder_slot"] = d["subfolder_slot"]
                entry["allowed_subfolders"] = d.get("allowed_subfolders") or CATALOG[vault][d["folder"]]["subfolders"]
            elif d["mode"] == "append_block":
                entry["file"] = d["file"]
            routes[vault][t] = entry
            if "sections" in d:
                templates[t] = [tuple(x) for x in d["sections"]]
    return routes, templates

ROUTES, TEMPLATES = build_routes_and_templates()

def types_for(vault_type):
    return sorted(ROUTES.get(vault_type, {}).keys())

# Frontmatter key order (only keys that are present are emitted).
FRONTMATTER_ORDER = [
    "type", "title", "client", "source", "captured",
    "funnel_stage", "hook_type", "storytelling_structure", "visual_format",
    "format", "status", "tags", "source_language",
    "created", "updated", "raw_source",
]

# Controlled-vocabulary fields: values must already exist in the methodology taxonomies.
CONTROLLED_FIELDS = {
    "funnel_stage": "funnel-stages",
    "hook_type": "hook-types",
    "storytelling_structure": "storytelling-structures",
    "visual_format": "visual-formats",
    "format": "visual-formats",
}

# --------------------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------------------

def slugify(text):
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "untitled"

def today():
    return datetime.date.today().isoformat()

def find_root(start=None):
    """Walk up to the repo root (folder holding ROOT_MARKER). Returns path or None."""
    cur = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.exists(os.path.join(cur, ROOT_MARKER)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent

def find_vault(start=None):
    """Walk up to a vault root (folder holding _system/rules.md). Returns (path, vault_type) or (None, None)."""
    cur = os.path.abspath(start or os.getcwd())
    while True:
        marker = os.path.join(cur, MARKER)
        if os.path.isfile(marker):
            return cur, read_vault_type(marker)
        parent = os.path.dirname(cur)
        if parent == cur:
            return None, None
        cur = parent

def read_vault_type(marker_path):
    try:
        with open(marker_path, encoding="utf-8") as f:
            head = f.read(600)
        m = re.search(r"vault_type:\s*(\w+)", head)
        return m.group(1) if m else None
    except OSError:
        return None

# --------------------------------------------------------------------------------------
# Enforcement: only catalog folders may be created.
# --------------------------------------------------------------------------------------

def allowed_folders(vault_type):
    """Closed set of relative content folders allowed for this vault type."""
    out = set()
    cat = CATALOG[vault_type]
    for folder, spec in cat.items():
        out.add(folder)
        if spec["shape"] == "closed-subfolders":
            for sub in spec["subfolders"]:
                out.add(f"{folder}/{sub}")
    return out

def assert_allowed(vault_type, rel_folder):
    rel = rel_folder.replace(os.sep, "/").strip("/")
    if rel in allowed_folders(vault_type):
        return
    raise ValueError(
        f"Refused: '{rel}' is not in the {vault_type} catalog. "
        f"Allowed: {sorted(allowed_folders(vault_type))}. "
        f"Folders outside the catalog are never created (see _system/rules.md)."
    )

def ensure_folder(vault_root, vault_type, rel_folder):
    assert_allowed(vault_type, rel_folder)
    path = os.path.join(vault_root, rel_folder)
    os.makedirs(path, exist_ok=True)
    return path

# --------------------------------------------------------------------------------------
# Frontmatter + body rendering
# --------------------------------------------------------------------------------------

def render_frontmatter(d):
    lines = ["---"]
    for k in FRONTMATTER_ORDER:
        if k not in d or d[k] in (None, "", []):
            continue
        v = d[k]
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)

def render_body(type_, slots):
    parts = []
    for heading, slot in TEMPLATES.get(type_, []):
        val = (slots or {}).get(slot, "").strip()
        parts.append(f"## {heading}\n\n{val if val else '_TODO_'}")
    return "\n\n".join(parts)

def render_note(frontmatter, title, type_, slots):
    return f"{render_frontmatter(frontmatter)}\n\n# {title}\n\n{render_body(type_, slots)}\n"

# --------------------------------------------------------------------------------------
# Section upsert (for fixed-files: identity / voice / taxonomies)
# --------------------------------------------------------------------------------------

def upsert_section(file_path, heading, content, scaffold_frontmatter=None):
    """Create the file if missing (with optional frontmatter), then upsert a '## heading' block."""
    if not os.path.isfile(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        base = ""
        if scaffold_frontmatter:
            base += render_frontmatter(scaffold_frontmatter) + "\n\n"
        base += f"# {os.path.splitext(os.path.basename(file_path))[0]}\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(base)
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    block = f"## {heading}\n\n{content.strip()}\n"
    pat = re.compile(r"(?ms)^## " + re.escape(heading) + r"\s*\n.*?(?=^## |\Z)")
    if pat.search(text):
        text = pat.sub(block + "\n", text, count=1)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + block
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

def append_block(file_path, block, scaffold_frontmatter=None):
    if not os.path.isfile(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        base = ""
        if scaffold_frontmatter:
            base += render_frontmatter(scaffold_frontmatter) + "\n\n"
        base += f"# {os.path.splitext(os.path.basename(file_path))[0]}\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(base)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n" + block.rstrip() + "\n")

# --------------------------------------------------------------------------------------
# Index / log / manifest
# --------------------------------------------------------------------------------------

def append_log(vault_root, message):
    log = os.path.join(vault_root, "log.md")
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"- {stamp} {message}\n"
    if not os.path.isfile(log):
        with open(log, "w", encoding="utf-8") as f:
            f.write("# Log\n\n")
    with open(log, "a", encoding="utf-8") as f:
        f.write(line)

def iter_notes(vault_root, vault_type):
    for folder in sorted(allowed_folders(vault_type)):
        d = os.path.join(vault_root, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".md"):
                yield folder, os.path.join(d, name)

def rebuild_index(vault_root, vault_type):
    lines = ["# Index", ""]
    for folder in sorted(allowed_folders(vault_type)):
        d = os.path.join(vault_root, folder)
        if not os.path.isdir(d):
            continue
        notes = sorted(n for n in os.listdir(d) if n.endswith(".md"))
        if not notes:
            continue
        lines.append(f"## {folder}")
        for n in notes:
            lines.append(f"- [[{folder}/{n[:-3]}]]")
        lines.append("")
    with open(os.path.join(vault_root, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

def manifest_path(vault_root):
    return os.path.join(vault_root, ".raw", ".manifest.json")

def load_manifest(vault_root):
    p = manifest_path(vault_root)
    if os.path.isfile(p):
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}
    return {}

def save_manifest(vault_root, data):
    p = manifest_path(vault_root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)

def mark_ingested(vault_root, raw_source, produced):
    data = load_manifest(vault_root)
    data[raw_source] = {"ingested_at": datetime.datetime.now().isoformat(timespec="seconds"),
                        "produced": produced}
    save_manifest(vault_root, data)
