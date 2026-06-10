#!/usr/bin/env python3
"""
template_admin.py — deterministically add or remove a template/type in types.json.
Adding a brand-new type is a governed change to the standard: it must route into an
existing catalog folder (new folders are an engine-level change, not done here).

Add:    template_admin.py add --vault client --type case-study --folder corpus \
                 --mode new_file --sections "Context:context;What happened:what;Result:result"
Remove: template_admin.py remove --vault client --type case-study
"""
import os, sys, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c

MODES = {"new_file", "named_file", "new_file_named", "section_in_file", "append_block"}

def load():
    with open(c.TYPES_PATH, encoding="utf-8") as f:
        return json.load(f)

def save(d):
    with open(c.TYPES_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--vault", required=True, choices=["client", "methodology"])
    a.add_argument("--type", required=True)
    a.add_argument("--folder", required=True)
    a.add_argument("--mode", required=True, choices=sorted(MODES))
    a.add_argument("--sections", default="")   # "Head:slot;Head2:slot2"
    a.add_argument("--file-slot", dest="file_slot", default=None)
    a.add_argument("--subfolder-slot", dest="subfolder_slot", default=None)
    a.add_argument("--file", default=None)
    r = sub.add_parser("remove")
    r.add_argument("--vault", required=True, choices=["client", "methodology"])
    r.add_argument("--type", required=True)
    args = ap.parse_args()

    defs = load()
    if args.cmd == "add":
        if args.type in defs[args.vault]:
            sys.exit(f"type '{args.type}' already exists in {args.vault}")
        folder = args.folder.strip("/")
        if folder not in c.allowed_folders(args.vault):
            sys.exit(f"folder '{folder}' is not in the {args.vault} catalog. "
                     f"New folders are an engine-level change, not done here. "
                     f"Allowed: {sorted(c.allowed_folders(args.vault))}")
        entry = {"folder": folder, "mode": args.mode}
        if args.sections:
            secs = []
            for pair in args.sections.split(";"):
                head, _, slot = pair.partition(":")
                secs.append([head.strip(), (slot.strip() or c.slugify(head))])
            entry["sections"] = secs
        if args.mode == "section_in_file":
            if not args.file_slot:
                sys.exit("--file-slot required for section_in_file")
            entry["file_slot"] = args.file_slot
        if args.mode == "new_file_named":
            if not args.subfolder_slot:
                sys.exit("--subfolder-slot required for new_file_named")
            entry["subfolder_slot"] = args.subfolder_slot
        if args.mode == "append_block":
            if not args.file:
                sys.exit("--file required for append_block")
            entry["file"] = args.file
        defs[args.vault][args.type] = entry
        save(defs)
        print(f"added type '{args.type}' to {args.vault} -> {folder}/ ({args.mode})")
    else:
        if args.type not in defs[args.vault]:
            sys.exit(f"type '{args.type}' not found in {args.vault}")
        defs[args.vault].pop(args.type)
        save(defs)
        print(f"removed type '{args.type}' from {args.vault} "
              f"(existing notes are left untouched)")

if __name__ == "__main__":
    main()
