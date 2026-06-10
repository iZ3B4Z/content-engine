"""Generate the condensed standard written into each vault's _system/rules.md."""
import common as c

def rules_md(vault_type):
    cat = c.CATALOG[vault_type]
    lines = [f"---", f"vault_type: {vault_type}", f"type: system", "---", "",
             f"# Content Engine — {vault_type} vault rules (marker)", "",
             "This file is the vault marker AND the condensed standard. Do not delete.", "",
             "## The one law", "",
             "Closed catalog + lazy creation + no topic folders. Only the folders listed",
             "below may exist. Each is created only when content first needs it. Topic and",
             "sector are frontmatter tags, never folders.", "",
             "## Allowed content folders"]
    for folder in sorted(cat.keys()):
        spec = cat[folder]
        extra = ""
        if spec["shape"] == "fixed-files":
            extra = " (files: " + ", ".join(spec["files"]) + ")"
        elif spec["shape"] == "closed-subfolders":
            extra = " (subfolders: " + ", ".join(spec["subfolders"]) + ")"
        lines.append(f"- `{folder}/` — {spec['shape']}{extra}")
    lines += ["", "Plus the system layer: `_system/`, `index.md`, `log.md`, `.raw/`.", "",
              "## Types routed here"]
    for t in c.types_for(vault_type):
        r = c.ROUTES[vault_type][t]
        lines.append(f"- `{t}` -> `{r['folder']}/` ({r['mode']})")
    lines.append("")
    return "\n".join(lines)
