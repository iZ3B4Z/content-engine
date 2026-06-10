---
name: wiki-maintain
description: >
  Keep a vault compliant with the standard: detect drift and rebuild indexes. Triggers on:
  "lint the wiki", "check the vault", "rebuild the index", "is anything off-standard".
allowed-tools: Bash Read
---

# maintain — lint and reindex

```bash
python3 <engine>/scripts/lint.py                                    # drift report (this vault)
python3 <engine>/scripts/update_index.py                            # rebuild this vault's index
python3 <engine>/scripts/update_index.py --all --root "<repo-root>" # all vaults
```

`lint.py` flags off-catalog folders, type/folder mismatches, missing frontmatter, and
un-ingested raw files. Fix by moving content into a catalog folder or correcting `type` —
never by inventing a folder.

## Talking to the user (always)

Translate lint output into plain language; never show raw issue codes like "[routing]".
Summarize what is off and offer fixes as choices ("Two notes look misfiled, want me to
move them?"). Only act after the user agrees. Reassure when the vault is clean. Match the
user's language.
