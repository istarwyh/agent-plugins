---
name: notify-on-complete
description: Send system notifications when Claude Code completes tasks. Use when the user wants to configure task completion notifications, set up alerts for long-running tasks, or customize notification settings.
---

# Task Completion Notification

Send system notifications when Claude Code tasks complete, perfect for long-running tasks or team collaboration.

## Quick Setup

Run this command to enable notifications:

```bash
bash ~/.claude/plugins/meta-plugin/scripts/setup-notification.sh
```

## Manual Configuration

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/plugins/meta-plugin/scripts/notify.sh \"Claude Code\" \"任务已完成，请查看结果\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## Customization

```bash
# Custom title and message
bash ~/.claude/plugins/meta-plugin/scripts/notify.sh "My Project" "代码审查完成"

# Disable sound
NOTIFY_SOUND=false bash ~/.claude/plugins/meta-plugin/scripts/notify.sh

# Disable terminal output
NOTIFY_TERMINAL=false bash ~/.claude/plugins/meta-plugin/scripts/notify.sh
```

## Platform Support

| Platform | Method | Requirements |
|----------|--------|--------------|
| macOS | osascript | Built-in |
| Linux | notify-send | `libnotify-bin` package |
| Windows | PowerShell | WSL or Git Bash |

## Test Notification

```bash
bash ~/.claude/plugins/meta-plugin/scripts/notify.sh "Test" "Test notification"
```

## Troubleshooting

### Linux: notify-send not found

```bash
# Ubuntu/Debian
sudo apt-get install libnotify-bin

# Fedora
sudo dnf install libnotify
```

### No sound on Linux

```bash
sudo apt-get install pulseaudio-utils
```

## Support

For issues, report at the repository's issue tracker.
