#!/bin/bash
# 小红书技能 Mac 环境检查脚本
# 用法: bash check_env.sh
# 返回码: 0=正常, 1=Chrome未安装, 2=无图像工具

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXIT_CODE=0

echo "=== 1. 检查 Chrome 浏览器 ==="
CHROME_APP="/Applications/Google Chrome.app"
if [ -d "$CHROME_APP" ]; then
  CHROME_VER=$("$CHROME_APP/Contents/MacOS/Google Chrome" --version 2>/dev/null | head -1)
  echo "✅ Chrome 已安装: ${CHROME_VER:-unknown version}"
else
  echo "❌ Chrome 未安装"
  echo "   请安装: https://www.google.com/chrome/"
  exit 1
fi

echo "=== 2. 检查 Chrome DevTools 调试端口 ==="
PORT=9222
if curl -s --max-time 2 "http://127.0.0.1:$PORT/json/version" | grep -q '"Browser"'; then
  echo "✅ Chrome 调试端口已就绪 (port $PORT)"
else
  echo "⚠️ Chrome 调试端口未开启"
  echo "   可执行: bash ${SCRIPT_DIR}/scripts/ensure-chrome-debug.sh"
  echo "   或手动启动带 --remote-debugging-port=9222 参数的 Chrome"
fi

echo "=== 3. 检查图像处理工具 ==="
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
  echo "❌ 未安装 ImageMagick 或 Pillow，封面生成不可用"
  echo "   方式1: brew install imagemagick"
  echo "   方式2: pip install Pillow"
  EXIT_CODE=2
fi

echo "=== 4. 检查中文字体 ==="
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
  # Try fc-list as fallback
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
  echo "   Mac 系统通常自带 PingFang / STHeiti，如缺失可安装阿里巴巴普惠体"
fi

echo "=== 5. 检查生图 API 配置 ==="
IMG_API_TYPE="${IMG_API_TYPE:-gemini}"
IMG_OK=false

case "$IMG_API_TYPE" in
  gemini)
    if [ -n "${GEMINI_API_KEY:-}" ]; then
      echo "✅ Gemini API Key 已配置"
      IMG_OK=true
    else
      echo "⚠️ Gemini API Key 未配置（可选，用于 AI 生图）"
    fi
    ;;
  openai)
    if [ -n "${IMG_API_KEY:-}" ]; then
      echo "✅ OpenAI 兼容 API Key 已配置"
      IMG_OK=true
    else
      echo "⚠️ OpenAI API Key 未配置"
    fi
    ;;
  hunyuan)
    if [ -n "${HUNYUAN_SECRET_ID:-}" ] && [ -n "${HUNYUAN_SECRET_KEY:-}" ]; then
      echo "✅ 腾讯云混元 API 已配置"
      IMG_OK=true
    else
      echo "⚠️ 腾讯云混元 API 未配置"
    fi
    ;;
esac

if [ "$IMG_OK" = false ]; then
  echo "   生图 API 为可选配置，不影响基本功能"
  echo "   如需 AI 生图，可设置: GEMINI_API_KEY / IMG_API_KEY / HUNYUAN_SECRET_ID+KEY"
fi

echo ""
echo "=== 检查结果 ==="
if [ "$EXIT_CODE" -eq 0 ]; then
  echo "✅ 环境就绪，可以使用小红书技能"
else
  echo "⚠️ 部分功能不可用（退出码: $EXIT_CODE）"
fi

exit $EXIT_CODE
