#!/usr/bin/env python3
"""
scaffold_vault.py — create a vault skeleton of a given type. Idempotent, skeleton only.
Usage: scaffold_vault.py <vault_root> --type {methodology|client} [--client SLUG]
Creates _system/{rules.md,hot.md}, index.md, log.md, and .raw/ zones. Content folders
are created lazily by ingest, never here.
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
import rules_text

RAW_ZONES = {"client": ["corpus", "inspiration", "intake"],
             "methodology": ["external", "frameworks", "taxonomies"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_root")
    ap.add_argument("--type", required=True, choices=["methodology", "client"])
    ap.add_argument("--client", default=None)
    a = ap.parse_args()
    root = os.path.abspath(a.vault_root)
    os.makedirs(os.path.join(root, "_system"), exist_ok=True)
    marker = os.path.join(root, c.MARKER)
    if not os.path.isfile(marker):
        with open(marker, "w", encoding="utf-8") as f:
            f.write(rules_text.rules_md(a.type))
    hot = os.path.join(root, "_system", "hot.md")
    if not os.path.isfile(hot):
        with open(hot, "w", encoding="utf-8") as f:
            f.write("# Hot cache\n\nRecent context. Trimmed periodically.\n")
    for fn, title in [("index.md", "# Index\n"), ("log.md", "# Log\n")]:
        p = os.path.join(root, fn)
        if not os.path.isfile(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(title)
    for zone in RAW_ZONES[a.type]:
        os.makedirs(os.path.join(root, ".raw", zone), exist_ok=True)
    if not os.path.isfile(c.manifest_path(root)):
        c.save_manifest(root, {})
    print(f"Scaffolded {a.type} vault: {root}")

if __name__ == "__main__":
    main()
