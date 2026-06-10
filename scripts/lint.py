#!/usr/bin/env python3
"""lint.py — detect drift from the standard in the current vault.
Flags: off-catalog folders, notes whose type doesn't match their folder, missing
frontmatter (type/title), and raw files not yet ingested."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c

def fm_get(text, key):
    m = re.search(r"(?m)^%s:\s*(.+)$" % re.escape(key), text)
    return m.group(1).strip() if m else None

def main():
    vault, vtype = c.find_vault()
    if not vault:
        sys.exit("no vault here")
    issues = []
    allowed = c.allowed_folders(vtype)
    content_top = {f.split("/")[0] for f in allowed} | {"_system", ".raw"}
    for name in os.listdir(vault):
        full = os.path.join(vault, name)
        if os.path.isdir(full) and not name.startswith(".") and name not in content_top:
            issues.append(f"[folder] off-catalog top-level folder: {name}/")
    # off-catalog subfolders + note checks
    for folder in sorted(allowed):
        d = os.path.join(vault, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if os.path.isdir(p) and f"{folder}/{name}" not in allowed:
                issues.append(f"[folder] off-catalog subfolder: {folder}/{name}/")
            if name.endswith(".md"):
                text = open(p, encoding="utf-8").read()
                typ = fm_get(text, "type")
                if not typ:
                    issues.append(f"[frontmatter] missing type: {folder}/{name}")
                elif typ in c.ROUTES.get(vtype, {}):
                    exp = c.ROUTES[vtype][typ]["folder"]
                    if not folder.startswith(exp):
                        issues.append(f"[routing] type '{typ}' should live in {exp}/ : {folder}/{name}")
                if not fm_get(text, "title") and typ not in ("scaffold", "system"):
                    issues.append(f"[frontmatter] missing title: {folder}/{name}")
    # un-ingested raw
    man = c.load_manifest(vault)
    rawdir = os.path.join(vault, ".raw")
    if os.path.isdir(rawdir):
        for dp, dn, fn in os.walk(rawdir):
            dn[:] = [x for x in dn if not x.startswith(".")]
            for f in fn:
                if f.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(dp, f), vault)
                if not any(rel in k or k in rel for k in man):
                    issues.append(f"[raw] not yet ingested: {rel}")
    if issues:
        print(f"LINT: {len(issues)} issue(s) in {vault}")
        for i in issues:
            print("  " + i)
        sys.exit(1)
    print(f"LINT OK: {vault}")

if __name__ == "__main__":
    main()
