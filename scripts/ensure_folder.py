#!/usr/bin/env python3
"""ensure_folder.py — lazily create a catalog folder in the current vault (guarded)."""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
ap = argparse.ArgumentParser(); ap.add_argument("folder"); a = ap.parse_args()
vault, vtype = c.find_vault()
if not vault: sys.exit("no vault here")
try:
    p = c.ensure_folder(vault, vtype, a.folder); print(f"ok: {p}")
except ValueError as e:
    sys.exit(str(e))
