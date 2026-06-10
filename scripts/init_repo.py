#!/usr/bin/env python3
"""
init_repo.py — create a Content Engine monorepo root with a methodology vault.
Usage: init_repo.py <location> [--name NAME]
Always contains everything under a 'wiki' root folder named after the repo (default
'content-wiki'): drops the .content-engine marker, scaffolds methodology/, creates clients/.
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
import scaffold_vault

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("location")
    ap.add_argument("--name", default="content-wiki")
    a = ap.parse_args()
    loc = os.path.abspath(a.location)
    root = loc if os.path.basename(loc) == a.name else os.path.join(loc, a.name)
    os.makedirs(root, exist_ok=True)
    marker = os.path.join(root, c.ROOT_MARKER)
    if not os.path.isfile(marker):
        with open(marker, "w", encoding="utf-8") as f:
            f.write("content-engine repo root\n")
    sys.argv = ["scaffold_vault.py", os.path.join(root, "methodology"), "--type", "methodology"]
    scaffold_vault.main()
    os.makedirs(os.path.join(root, "clients"), exist_ok=True)
    print(f"Repo root ready: {root}")

if __name__ == "__main__":
    main()
