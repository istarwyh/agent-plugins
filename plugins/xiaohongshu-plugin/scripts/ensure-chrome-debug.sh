#!/bin/bash
# Ensure Chrome is running with remote debugging enabled.
# Reuses the user's original Chrome profile via symlinks.
#
# Usage: bash ensure-chrome-debug.sh
# Exit codes: 0 = ready, 1 = failed

PORT=9222
ORIGINAL_DIR="$HOME/Library/Application Support/Google/Chrome"
LINKED_DIR="/tmp/chrome-linked-profile"

# Check if already connected
if curl -s --max-time 2 "http://127.0.0.1:$PORT/json/version" | grep -q '"Browser"'; then
  echo "OK: Chrome debugging already available on port $PORT"
  exit 0
fi

echo "Chrome debugging not available. Setting up..."

# Kill existing Chrome
killall -9 "Google Chrome" 2>/dev/null
sleep 4

# Verify all Chrome processes are gone
REMAINING=$(ps aux | grep -i "[G]oogle Chrome" | wc -l | tr -d ' ')
if [ "$REMAINING" -gt 0 ]; then
  echo "WARNING: $REMAINING Chrome processes still running, force killing by PID..."
  ps aux | grep -i "[G]oogle Chrome" | awk '{print $2}' | xargs kill -9 2>/dev/null
  sleep 3
fi

# Create symlinked user-data-dir
if [ -d "$ORIGINAL_DIR" ]; then
  rm -rf "$LINKED_DIR"
  mkdir -p "$LINKED_DIR"
  ls "$ORIGINAL_DIR" | while read item; do
    ln -s "$ORIGINAL_DIR/$item" "$LINKED_DIR/$item" 2>/dev/null
  done
  echo "Symlinked profile created at $LINKED_DIR"
else
  echo "WARNING: Original Chrome profile not found at $ORIGINAL_DIR"
  echo "Using fresh profile at $LINKED_DIR"
  mkdir -p "$LINKED_DIR"
fi

# Launch Chrome
# Note: --remote-allow-origins=* is required to allow WebSocket connections from external tools.
# Without this flag, Chrome will reject WebSocket handshakes with HTTP 403 Forbidden.
arch -arm64 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=$PORT \
  --user-data-dir="$LINKED_DIR" \
  --remote-allow-origins=* 2>/dev/null &

# Wait for Chrome to be ready (up to 15 seconds)
for i in $(seq 1 15); do
  sleep 1
  if curl -s --max-time 1 "http://127.0.0.1:$PORT/json/version" | grep -q '"Browser"'; then
    echo "OK: Chrome debugging ready on port $PORT (took ${i}s)"
    exit 0
  fi
done

echo "FAILED: Chrome debugging not available after 15 seconds"
echo "Check /tmp/chrome_debug_err.log for details"
exit 1
