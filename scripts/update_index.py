#!/usr/bin/env python3
"""update_index.py — rebuild index.md for the current vault (or all vaults with --all)."""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true")
ap.add_argument("--root", default=None); a = ap.parse_args()
def do(vault_root, vtype):
    c.rebuild_index(vault_root, vtype); print(f"index rebuilt: {vault_root}")
if a.all:
    root = os.path.abspath(a.root) if a.root else c.find_root()
    do(os.path.join(root, "methodology"), "methodology")
    cl = os.path.join(root, "clients")
    for s in sorted(os.listdir(cl)) if os.path.isdir(cl) else []:
        vr = os.path.join(cl, s)
        if os.path.isdir(os.path.join(vr, "_system")):
            do(vr, "client")
else:
    vault, vtype = c.find_vault()
    if not vault: sys.exit("no vault here")
    do(vault, vtype)
