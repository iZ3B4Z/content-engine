---
name: wiki-setup
description: >
  Initialize a Content Engine monorepo (one methodology vault + a clients/ folder) and
  create client vaults. Pure mechanics, no judgment. Triggers on: "set up content engine",
  "create the wiki", "new client vault", "init the repo", "add a client".
allowed-tools: Bash Read
---

# setup — initialize the repo and create client vaults

Setup is pure mechanics. Do not improvise structure; run the scripts.
`<engine>` = the folder containing `scripts/` (this package).

## Create the monorepo root (once)

```bash
python3 <engine>/scripts/init_repo.py "<location>"
```

Creates a single contained root folder (default `content-wiki`) holding: the
`.content-engine` marker, a scaffolded `methodology/` vault, and an empty `clients/`.
Nothing is scattered into `<location>`.

## Add a client (anytime)

```bash
python3 <engine>/scripts/new_client.py <slug> --root "<repo-root>"
```

`<slug>`: lowercase letters, digits, dashes. Creates `clients/<slug>/` scaffolded as a
client vault (skeleton only). Content folders appear lazily on first ingest.

## The standard (do not break it)

The catalog of allowed folders is CLOSED (see `<vault>/_system/rules.md`); only catalog
folders may be created, only when content needs them. Topic and sector are frontmatter
tags, never folders.

## Talking to the user (always)

Speak naturally; never show Python, paths, or raw output unless asked. After creating a
repo or client, confirm in one sentence ("Done, I created Maria's space, empty and ready").
Do not paste the scaffold tree of system files; the user does not need it. If the user
asks for something that changes the base structure (a new folder or type), say it changes
the standard and offer to flag it for the operator rather than improvising. Match the
user's language.
