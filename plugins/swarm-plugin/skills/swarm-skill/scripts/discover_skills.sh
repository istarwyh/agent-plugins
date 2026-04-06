#!/usr/bin/env bash
# Discover available skills and commands from the filesystem.
# Outputs a formatted list. Does NOT cover session-level skills from system-reminder
# (those must be parsed by Claude from context).
set -euo pipefail

echo "=== User Commands ==="
if ls ~/.claude/commands/*.md 2>/dev/null 1>&2; then
  for f in ~/.claude/commands/*.md; do
    name=$(basename "$f" .md)
    # Try to extract description from frontmatter
    desc=$(sed -n '/^---$/,/^---$/{ /^description:/s/^description:[[:space:]]*//p; }' "$f" 2>/dev/null || echo "")
    if [ -z "$desc" ]; then
      desc="(user command)"
    fi
    echo "- /${name}: ${desc}"
  done
else
  echo "(none)"
fi

echo ""
echo "=== Project Commands ==="
if ls .claude/commands/*.md 2>/dev/null 1>&2; then
  for f in .claude/commands/*.md; do
    name=$(basename "$f" .md)
    desc=$(sed -n '/^---$/,/^---$/{ /^description:/s/^description:[[:space:]]*//p; }' "$f" 2>/dev/null || echo "")
    if [ -z "$desc" ]; then
      desc="(project command)"
    fi
    echo "- /${name}: ${desc}"
  done
else
  echo "(none)"
fi
