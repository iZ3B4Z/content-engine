#!/usr/bin/env python3
"""
catalog.py — deterministic, fixed-width Unicode view of the template/type catalog.
Reads types.json (via common). Same input -> byte-identical output, every time.
Usage: catalog.py            # show both vaults
       catalog.py client     # one vault
"""
import os, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as c

CW = 72  # inner content width (chars between the borders, incl. 1 leading space)

def _line(text=""):
    return "│ " + text[:CW].ljust(CW) + " │"

def _wrap(prefix, body, indent="     "):
    out, width = [], CW - len(indent)
    chunks = textwrap.wrap(body, width=width) or [""]
    out.append(_line(indent + prefix + chunks[0]))
    for ch in chunks[1:]:
        out.append(_line(indent + " " * len(prefix) + ch))
    return out

def descriptor(vault, t):
    r = c.ROUTES[vault][t]
    mode, folder = r["mode"], r["folder"]
    secs = " · ".join(h for h, _ in c.TEMPLATES.get(t, []))
    if mode == "new_file":
        return folder + "/", ("sections: " + secs)
    if mode == "named_file":
        return folder + "/<name>.md", ("sections: " + secs)
    if mode == "new_file_named":
        return folder + "/<kind>/", ("kinds: " + ", ".join(r["allowed_subfolders"]) +
                                     ("   sections: " + secs if secs else ""))
    if mode == "section_in_file":
        return folder + "/", ("files: " + ", ".join(r["allowed_files"]))
    if mode == "append_block":
        return folder + "/" + r["file"] + ".md", "appends dated blocks"
    return folder + "/", ""

def box(vault, title):
    lines = ["╭" + "─" * (CW + 2) + "╮", _line(title), "├" + "─" * (CW + 2) + "┤"]
    types = c.types_for(vault)
    for i, t in enumerate(types):
        dest, desc = descriptor(vault, t)
        lines.append(_line(t.ljust(22) + "→ " + dest))
        lines += _wrap("", desc)
        if i != len(types) - 1:
            lines.append(_line())
    lines.append("╰" + "─" * (CW + 2) + "╯")
    return "\n".join(lines)

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else None
    order = [("client", "CLIENT VAULT  ·  templates (closed standard)"),
             ("methodology", "METHODOLOGY VAULT  ·  templates (closed standard)")]
    blocks = [box(v, title) for v, title in order if which in (None, v)]
    print("\n\n".join(blocks))

if __name__ == "__main__":
    main()
