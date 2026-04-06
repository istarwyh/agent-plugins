#!/usr/bin/env bash
# Check Claude Code version and Agent Teams enablement.
# Exit codes: 0 = ready, 1 = version too low, 2 = Agent Teams not enabled
set -euo pipefail

MIN_VERSION="2.1.32"

# --- Version check ---
RAW_VERSION=$(claude --version 2>/dev/null || echo "0.0.0")
# Extract semver (e.g. "2.3.1" from "claude 2.3.1 (build ...)")
VERSION=$(echo "$RAW_VERSION" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
VERSION=${VERSION:-"0.0.0"}

version_ge() {
  # Returns 0 if $1 >= $2
  printf '%s\n%s' "$2" "$1" | sort -V -C
}

if ! version_ge "$VERSION" "$MIN_VERSION"; then
  echo "FAIL:VERSION:$VERSION"
  echo "Agent Teams requires Claude Code v${MIN_VERSION}+. Current: v${VERSION}"
  echo "Run: claude update"
  exit 1
fi

echo "OK:VERSION:$VERSION"

# --- Agent Teams check ---
if [ "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "1" ]; then
  echo "OK:AGENT_TEAMS:enabled"
  exit 0
else
  echo "FAIL:AGENT_TEAMS:not_enabled"
  echo "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is not set to 1."
  echo "Need to add it to ~/.claude/settings.json and restart Claude Code."
  exit 2
fi
