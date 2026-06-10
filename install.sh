#!/usr/bin/env bash
# Content Engine installer. Installs the engine into ~/.claude/skills/content-engine and
# optionally creates a monorepo root. Usage:
#   bash install.sh [<parent-dir>]      # non-interactive: also init_repo at <parent-dir>
#   bash install.sh                     # interactive prompt
set -euo pipefail
REPO_URL="https://github.com/iZ3B4Z/content-engine"
DEST="${HOME}/.claude/skills/content-engine"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Installing engine to $DEST"
mkdir -p "$DEST"
if [ -f "$SRC_DIR/scripts/common.py" ]; then
  cp -R "$SRC_DIR/scripts" "$SRC_DIR/skills" "$DEST/"
else
  TMP="$(mktemp -d)"; git clone --depth 1 "$REPO_URL" "$TMP/ce"
  cp -R "$TMP/ce/scripts" "$TMP/ce/skills" "$DEST/"
fi
echo "    done."

PARENT="${1:-}"
if [ -z "$PARENT" ] && [ -t 0 ]; then
  printf "Create a content-wiki repo now? [Y/n]: "; read -r ans
  if [ "${ans:-Y}" = "Y" ] || [ "${ans:-y}" = "y" ] || [ -z "${ans:-}" ]; then
    printf "Parent folder [default: %s]: " "$PWD"; read -r PARENT; PARENT="${PARENT:-$PWD}"
  fi
fi
if [ -n "$PARENT" ]; then
  python3 "$DEST/scripts/init_repo.py" "$PARENT"
fi
echo "==> Done."
