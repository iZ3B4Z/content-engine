#!/usr/bin/env python3
"""resolve_vault.py — print the current vault root + type and the repo root."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c
vault, vtype = c.find_vault()
root = c.find_root()
print(f"repo_root: {root}")
print(f"vault_root: {vault}")
print(f"vault_type: {vtype}")
if not vault:
    sys.exit(1)
