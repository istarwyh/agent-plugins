#!/usr/bin/env bash
# Setup notification hooks for Claude Code
# This script adds the Stop hook to ~/.claude/settings.json

set -euo pipefail

SETTINGS_FILE="$HOME/.claude/settings.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFY_SCRIPT="$SCRIPT_DIR/notify.sh"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔔 Claude Code Notification Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if notify.sh exists
if [[ ! -f "$NOTIFY_SCRIPT" ]]; then
    echo -e "${RED}Error: notify.sh not found at $NOTIFY_SCRIPT${NC}"
    exit 1
fi

# Make notify.sh executable
chmod +x "$NOTIFY_SCRIPT"

# Create settings directory if needed
mkdir -p "$(dirname "$SETTINGS_FILE")"

# Check if settings file exists
if [[ ! -f "$SETTINGS_FILE" ]]; then
    echo "{}" > "$SETTINGS_FILE"
    echo -e "${YELLOW}Created new settings file: $SETTINGS_FILE${NC}"
fi

# Check if jq is available
if command -v jq &> /dev/null; then
    # Check if Stop hook already exists
    if jq -e '.hooks.Stop' "$SETTINGS_FILE" &> /dev/null; then
        echo -e "${YELLOW}Stop hook already exists. Updating...${NC}"
    fi

    # Append notification hook to Stop hooks (non-destructive)
    local new_hook
    new_hook=$(jq -n \
        --arg cmd "bash $NOTIFY_SCRIPT \"Claude Code\" \"任务已完成，请查看结果\"" \
        '{"type": "command", "command": $cmd, "timeout": 10}')
    jq --argjson hook "$new_hook" '
        .hooks.Stop //= [{"hooks": []}] |
        .hooks.Stop[0].hooks //= [] |
        .hooks.Stop[0].hooks += [$hook]
    ' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"

    echo -e "${GREEN}✓ Notification hooks configured successfully!${NC}"
else
    # Manual instructions if jq not available
    echo -e "${YELLOW}jq not found. Please manually add this to $SETTINGS_FILE:${NC}"
    echo ""
    cat <<EOF
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash $NOTIFY_SCRIPT \"Claude Code\" \"任务已完成，请查看结果\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
EOF
    echo ""
    echo -e "${YELLOW}Note: If you have existing hooks, merge them carefully.${NC}"
fi

# Test the notification
echo ""
echo "Testing notification..."
"$NOTIFY_SCRIPT" "Claude Code" "通知配置完成！" "true" "true"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  ✅ Setup Complete!${NC}"
echo ""
echo "  Notifications will appear when Claude Code"
echo "  completes tasks (Stop event)."
echo ""
echo "  To customize, edit:"
echo "    ~/.claude/settings.json"
echo ""
echo "  To test again:"
echo "    bash $NOTIFY_SCRIPT \"Test\" \"Test message\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
