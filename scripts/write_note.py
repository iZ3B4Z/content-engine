#!/usr/bin/env python3
"""
write_note.py — the deterministic filer. Consumes structured record(s) from the model and
files markdown into the correct vault/folder with the right name, frontmatter, and template.
The model never decides paths, names, or formatting; this script does.

Input: JSON on stdin or a file path arg. Either a single record, a list of records, or
{"raw_source": "...", "records": [...]}.

Record schema:
  vault: "client" | "methodology"
  client: "<slug>"            (required iff vault == client)
  type: "<closed type>"
  title: "<human title>"
  tags: [..]                  (optional; topic/sector)
  source_language: "es"       (optional)
  raw_source: "<path>"        (optional; or global)
  slots: { ... }              (template slots; plus mode-specific keys)
  # passthrough frontmatter for some types: source, captured, funnel_stage, hook_type,
  # storytelling_structure, visual_format, format
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c

PASSTHROUGH = ["source", "captured", "funnel_stage", "hook_type",
               "storytelling_structure", "visual_format", "format", "status"]

def resolve_vault_root(rec, root):
    vault = rec["vault"]
    if vault == "methodology":
        return os.path.join(root, "methodology"), "methodology"
    if vault == "client":
        slug = rec.get("client")
        if not slug:
            raise ValueError("client record missing 'client' slug")
        return os.path.join(root, "clients", slug), "client"
    raise ValueError(f"unknown vault: {vault}")

def validate_controlled(root, rec, warnings):
    """Warn (do not fail) if a controlled value isn't found in the methodology taxonomy."""
    meth = os.path.join(root, "methodology")
    for field, taxfile in c.CONTROLLED_FIELDS.items():
        val = rec.get(field)
        if not val:
            continue
        path = os.path.join(meth, "taxonomies", taxfile + ".md")
        if not os.path.isfile(path):
            warnings.append(f"taxonomy '{taxfile}' not found; cannot validate {field}={val}")
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if str(val) not in text:
            warnings.append(f"PROPOSED new {field} value '{val}' not in taxonomy '{taxfile}' "
                            f"-> review before it becomes canonical")

def file_one(rec, root, global_raw, warnings):
    vault_root, vtype = resolve_vault_root(rec, root)
    if not os.path.isdir(os.path.join(vault_root, "_system")):
        raise ValueError(f"target vault not scaffolded: {vault_root}")
    t = rec["type"]
    if t not in c.ROUTES[vtype]:
        raise ValueError(f"type '{t}' not valid for {vtype}. Valid: {c.types_for(vtype)}")
    route = c.ROUTES[vtype][t]
    title = rec.get("title", "untitled")
    raw_source = rec.get("raw_source") or global_raw
    slots = rec.get("slots", {})
    created = c.today()

    validate_controlled(root, rec, warnings)

    fm = {"type": t, "title": title, "created": created, "updated": created}
    if vtype == "client":
        fm["client"] = rec.get("client")
    for k in ["tags", "source_language"]:
        if rec.get(k):
            fm[k] = rec[k]
    for k in PASSTHROUGH:
        if rec.get(k):
            fm[k] = rec[k]
    if raw_source:
        fm["raw_source"] = raw_source

    mode = route["mode"]
    produced = []

    if mode in ("new_file", "new_file_named", "named_file"):
        folder = route["folder"]
        if mode == "new_file_named":
            sub = slots.get(route["subfolder_slot"])
            if sub not in route["allowed_subfolders"]:
                raise ValueError(f"{route['subfolder_slot']}='{sub}' must be one of "
                                 f"{route['allowed_subfolders']}")
            folder = f"{folder}/{sub}"
            fname = f"{c.slugify(title)}.md"
        elif mode == "named_file":
            fname = f"{c.slugify(title)}.md"
        else:
            fname = f"{created}-{c.slugify(title)}.md"
        c.ensure_folder(vault_root, vtype, folder)
        path = os.path.join(vault_root, folder, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c.render_note(fm, title, t, slots))
        produced.append(os.path.relpath(path, vault_root))

    elif mode == "section_in_file":
        fileslot = route["file_slot"]
        which = slots.get(fileslot)
        if which not in route["allowed_files"]:
            raise ValueError(f"{fileslot}='{which}' must be one of {route['allowed_files']}")
        c.ensure_folder(vault_root, vtype, route["folder"])
        path = os.path.join(vault_root, route["folder"], which + ".md")
        content = slots.get("content", "").strip() or "_TODO_"
        if raw_source:
            content += f"\n\n(source: {raw_source})"
        c.upsert_section(path, heading=title, content=content,
                         scaffold_frontmatter={"type": "scaffold", "title": which})
        produced.append(os.path.relpath(path, vault_root))

    elif mode == "append_block":
        c.ensure_folder(vault_root, vtype, route["folder"])
        path = os.path.join(vault_root, route["folder"], route["file"] + ".md")
        block = f"### {created} — {slots.get('context','')}\n\n> {slots.get('quote','').strip()}"
        if raw_source:
            block += f"\n\n(source: {raw_source})"
        c.append_block(path, block, scaffold_frontmatter={"type": "scaffold", "title": route["file"]})
        produced.append(os.path.relpath(path, vault_root))
    else:
        raise ValueError(f"unknown mode: {mode}")

    c.rebuild_index(vault_root, vtype)
    c.append_log(vault_root, f"ingest {t} -> {produced[0]}" + (f" (from {raw_source})" if raw_source else ""))
    if raw_source:
        c.mark_ingested(vault_root, raw_source, produced)
    return [os.path.join(os.path.relpath(vault_root, root), p) for p in produced]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?", help="JSON file (default: stdin)")
    ap.add_argument("--root", default=None, help="repo root (default: resolve from cwd)")
    a = ap.parse_args()
    raw = open(a.input, encoding="utf-8").read() if a.input else sys.stdin.read()
    data = json.loads(raw)
    if isinstance(data, list):
        records, global_raw = data, None
    elif "records" in data:
        records, global_raw = data["records"], data.get("raw_source")
    else:
        records, global_raw = [data], data.get("raw_source")
    root = os.path.abspath(a.root) if a.root else c.find_root()
    if not root:
        sys.exit("repo root not found (no .content-engine marker).")
    warnings, written = [], []
    for rec in records:
        try:
            written += file_one(rec, root, global_raw, warnings)
        except (ValueError, KeyError) as e:
            print(f"Refused: {e}", file=sys.stderr)
            sys.exit(1)
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    for p in written:
        print(p)

if __name__ == "__main__":
    main()
