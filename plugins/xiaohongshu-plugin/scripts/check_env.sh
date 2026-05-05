#!/bin/bash
# 小红书技能环境检查脚本
# 用法: bash check_env.sh
# 返回码: 0=正常, 1=Chrome未安装, 2=无图像工具

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI_DIR="$PLUGIN_DIR/xiaohongshu-skills"
EXIT_CODE=0

echo "=== 1. 检查 Python ==="
if command -v python3 &> /dev/null; then
  PY_VER=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
  PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 11 ]; }; then
    echo "✅ Python $PY_VER"
  else
    echo "❌ Python $PY_VER (需要 >= 3.11)"
    echo "   安装: brew install python@3.11"
    exit 1
  fi
else
  echo "❌ Python 未安装"
  echo "   安装: brew install python@3.11"
  exit 1
fi

echo "=== 2. 检查 uv ==="
if command -v uv &> /dev/null; then
  echo "✅ uv $(uv --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo 'installed')"
else
  echo "⚠️ uv 未安装（CLI 依赖管理工具）"
  echo "   安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

echo "=== 3. 检查 CLI 引擎 ==="
CLI="$CLI_DIR/scripts/cli.py"
if [ -f "$CLI" ]; then
  echo "✅ CLI 引擎存在: $CLI"
  # Check if dependencies are installed
  if python3 -c "import websockets" 2>/dev/null; then
    echo "✅ CLI Python 依赖已安装"
  else
    echo "⚠️ CLI Python 依赖未安装"
    echo "   执行: cd $CLI_DIR && uv sync"
  fi
else
  echo "❌ CLI 引擎不存在: $CLI"
  echo "   请克隆 xiaohongshu-skills 到 $CLI_DIR"
fi

echo "=== 4. 检查 Chrome Extension Bridge ==="
if curl -s --max-time 2 "http://127.0.0.1:9333" &>/dev/null || \
   python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('127.0.0.1', 9333))
    print('connected')
finally:
    s.close()
" 2>/dev/null | grep -q connected; then
  echo "✅ Bridge Server 运行中 (ws://localhost:9333)"
else
  echo "⚠️ Bridge Server 未运行"
  echo "   CLI 会自动启动，或手动启动: cd $CLI_DIR && python3 scripts/bridge_server.py"
fi

echo "=== 5. 检查 Chrome 浏览器 ==="
CHROME_APP="/Applications/Google Chrome.app"
if [ -d "$CHROME_APP" ]; then
  CHROME_VER=$("$CHROME_APP/Contents/MacOS/Google Chrome" --version 2>/dev/null | head -1)
  echo "✅ Chrome 已安装: ${CHROME_VER:-unknown version}"
else
  echo "❌ Chrome 未安装"
  echo "   请安装: https://www.google.com/chrome/"
  exit 1
fi

echo "=== 6. 检查图像处理工具（封面生成）==="
IMG_TOOL="none"
if command -v magick &> /dev/null; then
  IMG_TOOL="imagemagick"
  echo "✅ ImageMagick 已安装 (magick)"
elif command -v convert &> /dev/null; then
  IMG_TOOL="imagemagick"
  echo "✅ ImageMagick 已安装 (convert)"
elif python3 -c "from PIL import Image; print(Image.__version__)" 2>/dev/null; then
  IMG_TOOL="pillow"
  PILLOW_VER=$(python3 -c "from PIL import Image; print(Image.__version__)" 2>/dev/null)
  echo "✅ Pillow 已安装 (${PILLOW_VER})"
else
  echo "⚠️ 未安装 ImageMagick 或 Pillow，封面生成不可用"
  echo "   方式1: brew install imagemagick"
  echo "   方式2: pip install Pillow"
  EXIT_CODE=2
fi

echo "=== 7. 检查中文字体（封面生成）==="
FONT_FOUND=false
for f in \
  "$HOME/Library/Fonts/AlibabaPuHuiTi-3-85-Bold.otf" \
  "$HOME/Library/Fonts/AlibabaPuHuiTi-Bold.otf" \
  "/Library/Fonts/AlibabaPuHuiTi-3-85-Bold.otf" \
  "/System/Library/Fonts/STHeiti Medium.ttc" \
  "/System/Library/Fonts/Hiragino Sans GB.ttc" \
  "/Library/Fonts/Songti.ttc" \
  "/System/Library/Fonts/PingFang.ttc"; do
  if [ -f "$f" ]; then
    echo "✅ 中文字体: $(basename "$f")"
    FONT_FOUND=true
    break
  fi
done

if [ "$FONT_FOUND" = false ]; then
  if command -v fc-list &> /dev/null; then
    ZH_FONT=$(fc-list :lang=zh -f "%{family}\n" 2>/dev/null | head -1)
    if [ -n "$ZH_FONT" ]; then
      echo "✅ 中文字体 (fc-list): ${ZH_FONT}"
      FONT_FOUND=true
    fi
  fi
fi

if [ "$FONT_FOUND" = false ]; then
  echo "⚠️ 未找到中文字体，封面文字可能显示异常"
fi

echo "=== 8. 检查生图 API 配置（可选）==="
IMG_API_TYPE="${IMG_API_TYPE:-gemini}"
case "$IMG_API_TYPE" in
  gemini)
    if [ -n "${GEMINI_API_KEY:-}" ]; then
      echo "✅ Gemini API Key 已配置"
    else
      echo "⚠️ Gemini API Key 未配置（可选，用于 AI 生图）"
    fi ;;
  openai)
    if [ -n "${IMG_API_KEY:-}" ]; then
      echo "✅ OpenAI 兼容 API Key 已配置"
    else
      echo "⚠️ OpenAI API Key 未配置"
    fi ;;
  hunyuan)
    if [ -n "${HUNYUAN_SECRET_ID:-}" ] && [ -n "${HUNYUAN_SECRET_KEY:-}" ]; then
      echo "✅ 腾讯云混元 API 已配置"
    else
      echo "⚠️ 腾讯云混元 API 未配置"
    fi ;;
esac

echo ""
echo "=== 检查结果 ==="
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "✅ 环境就绪"
else
  echo "⚠️ 部分功能不可用（退出码: $EXIT_CODE）"
fi

exit $EXIT_CODE
