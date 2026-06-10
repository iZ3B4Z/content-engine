#!/usr/bin/env python3
"""search.py — deterministic keyword search across the current vault's notes."""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
ap = argparse.ArgumentParser(); ap.add_argument("query"); a = ap.parse_args()
vault, vtype = c.find_vault()
if not vault: sys.exit("no vault here")
q = a.query.lower(); hits = []
for folder, path in c.iter_notes(vault, vtype):
    text = open(path, encoding="utf-8").read().lower()
    score = text.count(q)
    if score:
        hits.append((score, os.path.relpath(path, vault)))
for score, rel in sorted(hits, reverse=True):
    print(f"{score:4d}  {rel}")
if not hits:
    print("no matches")
