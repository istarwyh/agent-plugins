#!/bin/bash
# Chrome DevTools 兜底脚本
# 仅在 CLI Extension Bridge 不可用时使用
#
# 使用方式: bash ensure-chrome-debug.sh
# 退出码: 0=就绪, 1=失败
#
# 注意: 此脚本会重启 Chrome 以启用调试端口。
# 如果用户正在使用 Extension Bridge 模式，请不要调用此脚本。

PORT=9222
ORIGINAL_DIR="$HOME/Library/Application Support/Google/Chrome"
LINKED_DIR="/tmp/chrome-linked-profile"

# Step 1: 如果调试端口已就绪，直接返回
if curl -s --max-time 2 "http://127.0.0.1:$PORT/json/version" | grep -q '"Browser"'; then
  echo "OK: Chrome debugging already available on port $PORT"
  exit 0
fi

echo "Chrome debugging not available on port $PORT."
echo "NOTE: This will restart Chrome (any Extension Bridge connection will be lost)."
echo "Proceeding in 3 seconds... (Ctrl+C to cancel)"
sleep 3

# Step 2: 关闭现有 Chrome
killall -9 "Google Chrome" 2>/dev/null
sleep 4

# Verify all Chrome processes are gone
REMAINING=$(ps aux | grep -i "[G]oogle Chrome" | wc -l | tr -d ' ')
if [ "$REMAINING" -gt 0 ]; then
  echo "WARNING: $REMAINING Chrome processes still running, force killing by PID..."
  ps aux | grep -i "[G]oogle Chrome" | awk '{print $2}' | xargs kill -9 2>/dev/null
  sleep 3
fi

# Step 3: 创建 symlinked user-data-dir（复用登录状态）
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

# Step 4: 启动 Chrome with debugging port
arch -arm64 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=$PORT \
  --user-data-dir="$LINKED_DIR" \
  --remote-allow-origins=* 2>/dev/null &

# Step 5: 等待就绪（最多 15 秒）
for i in $(seq 1 15); do
  sleep 1
  if curl -s --max-time 1 "http://127.0.0.1:$PORT/json/version" | grep -q '"Browser"'; then
    echo "OK: Chrome debugging ready on port $PORT (took ${i}s)"
    exit 0
  fi
done

echo "FAILED: Chrome debugging not available after 15 seconds"
exit 1
