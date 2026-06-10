#!/usr/bin/env python3
"""
new_client.py — create a client vault under <root>/clients/<slug>. Resolves repo root.
Usage: new_client.py <slug> [--root ROOT]
"""
import os, re, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
import scaffold_vault

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", a.slug):
        sys.exit("slug may only contain lowercase letters, digits, and dashes")
    root = os.path.abspath(a.root) if a.root else c.find_root()
    if not root:
        sys.exit("repo root not found (no .content-engine marker). Run init_repo.py first.")
    client_dir = os.path.join(root, "clients", a.slug)
    if os.path.isdir(os.path.join(client_dir, "_system")):
        print(f"Client already exists: {client_dir}"); return
    sys.argv = ["scaffold_vault.py", client_dir, "--type", "client", "--client", a.slug]
    scaffold_vault.main()

if __name__ == "__main__":
    main()
