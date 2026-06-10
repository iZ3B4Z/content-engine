---
name: wiki-query
description: >
  Find and read notes in the current vault deterministically. Triggers on: "search the
  wiki", "find notes about", "what do we have on", "show the index".
allowed-tools: Bash Read
---

# query — search and read

```bash
python3 <engine>/scripts/search.py "<keyword>"     # ranked keyword search in this vault
cat <vault>/index.md                                # the auto-built catalog
```

For cross-vault answers, search each vault from its folder, or read
`<repo-root>/methodology/index.md`.

## Talking to the user (always)

Present findings readably: a short list of the relevant notes by their human title with a
one-line gist, and quote the useful part. Do not dump raw file paths or search scores
unless asked. If nothing matches, say so plainly and suggest what to ingest. Match the
user's language.
