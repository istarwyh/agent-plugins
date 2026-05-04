#!/usr/bin/env bash
# Cross-platform notification script for Claude Code
# Supports macOS, Linux, and Windows (via WSL/Git Bash)

set -euo pipefail

# Default values
DEFAULT_TITLE="Claude Code"
DEFAULT_MESSAGE="任务已完成，请查看结果"
SOUND_ENABLED="${NOTIFY_SOUND:-true}"
TERMINAL_OUTPUT="${NOTIFY_TERMINAL:-true}"

# Parse arguments
TITLE="${1:-$DEFAULT_TITLE}"
MESSAGE="${2:-$DEFAULT_MESSAGE}"
SOUND="${3:-$SOUND_ENABLED}"
TERMINAL="${4:-$TERMINAL_OUTPUT}"

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Darwin*)    echo "macos";;
        Linux*)     echo "linux";;
        MINGW*|MSYS*|CYGWIN*)    echo "windows";;
        *)          echo "unknown";;
    esac
}

# Send notification based on platform
send_notification() {
    local platform
    platform=$(detect_platform)

    case "$platform" in
        macos)
            send_macos_notification
            ;;
        linux)
            send_linux_notification
            ;;
        windows)
            send_windows_notification
            ;;
        *)
            echo "Unsupported platform: $(uname -s)" >&2
            send_terminal_notification
            return 1
            ;;
    esac

    # Terminal output
    if [[ "$TERMINAL" == "true" ]]; then
        send_terminal_notification
    fi
}

# macOS notification using osascript
send_macos_notification() {
    # Escape backslashes and double quotes for AppleScript string literals
    local safe_title safe_message
    safe_title="${TITLE//\\/\\\\}"
    safe_title="${safe_title//\"/\\\"}"
    safe_message="${MESSAGE//\\/\\\\}"
    safe_message="${safe_message//\"/\\\"}"
    osascript -e "display notification \"$safe_message\" with title \"$safe_title\""

    if [[ "$SOUND" == "true" ]]; then
        osascript -e "beep"
    fi
}

# Linux notification using notify-send
send_linux_notification() {
    if command -v notify-send &> /dev/null; then
        notify-send "$TITLE" "$MESSAGE"

        if [[ "$SOUND" == "true" ]]; then
            # Try paplay first (PulseAudio), then aplay
            if command -v paplay &> /dev/null; then
                paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true
            elif command -v aplay &> /dev/null; then
                aplay /usr/share/sounds/sound-icons/xylophone.wav 2>/dev/null || true
            fi
        fi
    else
        echo "notify-send not found. Install libnotify-bin package." >&2
        send_terminal_notification
    fi
}

# Windows notification using PowerShell
send_windows_notification() {
    if command -v powershell.exe &> /dev/null; then
        # Pass title and message via environment variables to avoid command injection
        NOTIFY_TITLE="$TITLE" NOTIFY_MESSAGE="$MESSAGE" \
        powershell.exe -Command "
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            \$safeTitle = [System.Security.SecurityElement]::Escape(\$env:NOTIFY_TITLE)
            \$safeMessage = [System.Security.SecurityElement]::Escape(\$env:NOTIFY_MESSAGE)

            \$template = @\"
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>\$safeTitle</text>
            <text>\$safeMessage</text>
        </binding>
    </visual>
</toast>
\"@

            \$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            \$xml.LoadXml(\$template)
            \$toast = [Windows.UI.Notifications.ToastNotification]::new(\$xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Claude Code').Show(\$toast)
        " 2>/dev/null || {
            echo "PowerShell notification failed" >&2
            send_terminal_notification
        }
    else
        echo "PowerShell not found" >&2
        send_terminal_notification
    fi
}

# Terminal notification (fallback)
send_terminal_notification() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔔 $TITLE"
    echo "   $MESSAGE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Bell character for terminal beep
    if [[ "$SOUND" == "true" ]]; then
        printf '\a'
    fi
}

# Main execution
send_notification
