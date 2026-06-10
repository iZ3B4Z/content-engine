# Content Engine

A deterministic knowledge engine for a content-creation business, built on a strict folder
standard. It turns any raw document into structured Obsidian markdown, routed automatically
between a shared **methodology** vault and isolated **client** vaults.

## Core idea: one law

**Closed catalog + lazy creation + no topic folders.** Only a fixed set of folders may
exist; each is created only when content needs it; topic and sector are frontmatter tags,
never folders. The standard is enforced by code (creation is refused off-catalog; lint
detects drift), so the structure never sprawls.

## Two vault types (one monorepo)

```
content-wiki/                 (.content-engine marker = repo root)
├── methodology/              transferable: taxonomies, frameworks, principles, templates, learnings
└── clients/
    └── <slug>/               per client, isolated: identity, voice, corpus, inspiration, outputs
```

Ingest is the single smart router: a single document can produce notes in both vaults at
once. The model only classifies (emits a small structured record); fixed scripts do all
file mechanics. See `scripts/common.py` for the catalogs, routing, and templates, and each
vault's `_system/rules.md` for the condensed standard.

## Install

Content Engine needs **Python 3.10+** and **git** (both preinstalled on most Macs).
Pick one of the two paths below. Replace `~/Documents` with wherever you want the wiki.

**Path A — Terminal (recommended, one command):**

```bash
# 1) open the Terminal app, then check prerequisites:
python3 --version        # must be 3.10 or newer
git --version

# 2) install the engine AND create the wiki in one command (exact repo URL):
curl -fsSL https://raw.githubusercontent.com/iZ3B4Z/content-engine/main/install.sh | bash -s -- ~/Documents

# 3) verify it worked:
ls ~/Documents/content-wiki     # you should see: methodology  clients
```

This installs the engine once at `~/.claude/skills/content-engine` and creates
`~/Documents/content-wiki/`.

**Path B — Claude Code plugin:**

```
/plugin marketplace add iZ3B4Z/content-engine
/plugin install content-engine@content-engine
```

Then tell Claude in plain language: "set up content engine in ~/Documents".

## Use

```
wiki-setup      init the repo, add client vaults
wiki-ingest     document in -> structured notes routed across vaults
wiki-query      search and read
wiki-maintain   lint for drift, rebuild indexes
wiki-templates  show the template catalog (deterministic Unicode panel), add/remove a template
```

All scripts are pure Python stdlib (3.10+), cross-platform. The engine is installed once
(outside the vaults); vaults are resolved by walking up to their marker, so there is no
per-client copy of the engine and no hard-coded paths.
