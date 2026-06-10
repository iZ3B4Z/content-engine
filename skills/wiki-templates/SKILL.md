---
name: wiki-templates
description: >
  Show the closed catalog of note templates/types (per vault) as a fixed, deterministic
  Unicode panel, and add or remove a template. Triggers on: "show templates", "what
  templates exist", "list the note types", "add a template", "remove a template",
  "ver plantillas", "agregar plantilla", "configuracion de plantillas".
allowed-tools: Bash Read
---

# wiki-templates — view and edit the template catalog

This is a command-like skill: the view is rendered by a fixed script, so it looks the same
every time. Do not hand-draw or summarize it; print exactly what the script outputs.

## Show the catalog (always run this first)

```bash
python3 <engine>/scripts/catalog.py
```

Print its output verbatim inside a fenced code block (it is a fixed-width Unicode panel).
Then, underneath, offer the two actions in plain language:

> You can **add a new template** or **remove one**. Want to do either?

## Add a template (governed change to the standard)

A new template/type must route into a folder that already exists in the catalog (creating a
brand-new folder is an engine-level change, not done here). Collect from the user, in
natural language: which vault (client or methodology), the type name, the destination
folder (must be an existing catalog folder), and the section headings. Then run:

```bash
python3 <engine>/scripts/template_admin.py add --vault <client|methodology> \
  --type <name> --folder <existing-folder> --mode new_file \
  --sections "Heading one:slot_one;Heading two:slot_two"
```

For special shapes: `--mode section_in_file --file-slot <slot>` (upsert into a fixed file),
`--mode append_block --file <name>` (append blocks), `--mode new_file_named --subfolder-slot
<slot>` (named file in a closed subfolder). After adding, re-run `catalog.py` and show the
updated panel so the user sees the change.

## Remove a template

```bash
python3 <engine>/scripts/template_admin.py remove --vault <client|methodology> --type <name>
```

Existing notes are left untouched; only the template definition is removed. Confirm with the
user before removing, then re-render the catalog.

## Talking to the user (always)

Show the panel verbatim; never paste the raw script command or JSON unless asked. Offer
add/remove as a simple choice. Confirm before removing. If the user wants a brand-new
folder (not just a new type in an existing folder), explain that changes the base structure
and is an operator/engine task, not a normal edit. Match the user's language.
