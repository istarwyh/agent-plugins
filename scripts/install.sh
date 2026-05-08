#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE="agent-plugins"
REPO="istarwyh/agent-plugins"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[info]${NC} $*"; }
ok()    { echo -e "${GREEN}[ok]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC} $*"; }
err()   { echo -e "${RED}[error]${NC} $*" >&2; }

# Check claude CLI
if ! command -v claude &>/dev/null; then
  err "Claude Code CLI not found."
  echo "  Install it first: npm install -g @anthropic-ai/claude-code"
  exit 1
fi

# Ensure marketplace is added
if ! claude plugin marketplace list 2>/dev/null | grep -q "$MARKETPLACE"; then
  info "Adding marketplace: $REPO ..."
  claude plugin marketplace add "$REPO"
  ok "Marketplace added."
else
  ok "Marketplace '$MARKETPLACE' already configured."
fi

# Available plugins in this marketplace
PLUGINS=(
  chrome-fetch-plugin
  env-config-plugin
  gemini-plugin
  meta-plugin
  oss-plugin
  social-autopilot-plugin
  swarm-plugin
  wechat-plugin
  xiaohongshu-plugin
)

install_plugin() {
  local name="$1"
  info "Installing ${name}@${MARKETPLACE} ..."
  claude plugin install "${name}@${MARKETPLACE}"
  ok "Done! Restart Claude Code to activate."
}

# If a plugin name was passed as argument, install it directly
if [[ ${1:-} ]]; then
  install_plugin "$1"
  exit 0
fi

# Interactive menu
echo ""
echo "Available plugins:"
echo ""
for i in "${!PLUGINS[@]}"; do
  printf "  ${CYAN}%2d${NC}) %s\n" "$((i+1))" "${PLUGINS[$i]}"
done
echo ""
read -rp "Enter number(s) to install (e.g. 1 or 1,3,5), or 'q' to quit: " choice

if [[ "$choice" == "q" || "$choice" == "Q" ]]; then
  echo "Bye!"
  exit 0
fi

IFS=',' read -ra nums <<< "$choice"
for n in "${nums[@]}"; do
  n=$(echo "$n" | tr -d ' ')
  idx=$((n - 1))
  if [[ $idx -ge 0 && $idx -lt ${#PLUGINS[@]} ]]; then
    install_plugin "${PLUGINS[$idx]}"
  else
    warn "Skipping invalid choice: $n"
  fi
done
