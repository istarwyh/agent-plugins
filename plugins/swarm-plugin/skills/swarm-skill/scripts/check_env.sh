#!/usr/bin/env bash
# Check Claude Code version and Agent Teams enablement.
# Exit codes: 0 = ready, 1 = version too low, 2 = Agent Teams not enabled
set -euo pipefail

MIN_VERSION="2.1.32"
STATE_DIR="${SWARM_SKILL_STATE_DIR:-$HOME/.claude/swarm-skill}"
READY_FILE="$STATE_DIR/agent-teams-ready"
FORCE_CHECK=0

for arg in "$@"; do
  case "$arg" in
    --force|--recheck)
      FORCE_CHECK=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 64
      ;;
  esac
done

if [ "$FORCE_CHECK" != "1" ] && [ -f "$READY_FILE" ]; then
  CACHED_VERSION=$(grep -E '^claude_code_version=' "$READY_FILE" 2>/dev/null | cut -d= -f2- || true)
  echo "OK:CACHE:agent_teams_ready"
  if [ -n "${CACHED_VERSION:-}" ]; then
    echo "OK:VERSION:$CACHED_VERSION"
  fi
  echo "Run with --force to recheck Claude Code version and Agent Teams enablement."
  exit 0
fi

# --- Version check ---
RAW_VERSION=$(claude --version 2>/dev/null || echo "0.0.0")
# Extract semver (e.g. "2.3.1" from "claude 2.3.1 (build ...)")
VERSION=$(echo "$RAW_VERSION" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
VERSION=${VERSION:-"0.0.0"}

version_ge() {
  # Returns 0 if $1 >= $2
  awk -v have="$1" -v need="$2" '
    BEGIN {
      split(have, h, "."); split(need, n, ".")
      for (i = 1; i <= 3; i++) {
        hv = h[i] + 0; nv = n[i] + 0
        if (hv > nv) exit 0
        if (hv < nv) exit 1
      }
      exit 0
    }'
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
  mkdir -p "$STATE_DIR"
  {
    printf 'status=ready\n'
    printf 'claude_code_version=%s\n' "$VERSION"
    date -u '+checked_at=%Y-%m-%dT%H:%M:%SZ'
  } > "$READY_FILE"
  echo "OK:AGENT_TEAMS:enabled"
  echo "OK:CACHE:recorded:$READY_FILE"
  exit 0
else
  echo "FAIL:AGENT_TEAMS:not_enabled"
  echo "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is not set to 1."
  echo "Need to add it to ~/.claude/settings.json and restart Claude Code."
  exit 2
fi
