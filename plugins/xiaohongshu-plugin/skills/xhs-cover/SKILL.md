---
name: xhs-cover
description: |
  生成小红书封面图（3:4 比例 1080x1440）。上半部分为 AI 主题图片，下半部分为纯色底+标题文字。
  当用户需要制作小红书封面、生成封面图、设计封面时使用。
  封面 AI 生图需配置可选环境变量（GEMINI_API_KEY 或 IMG_API_KEY 或 HUNYUAN_SECRET_ID+KEY）。
---

## 封面图结构

1080x1440（3:4）：
- 上半部分（1080x720，3:2）：AI 生成的主题图片
- 下半部分（1080x720，3:2）：纯色底 + 标题文字

## 前置检查

```bash
bash {baseDir}/../../scripts/check_env.sh
```

退出码 `2` 表示无图像工具，需安装：
- `brew install imagemagick`（推荐）
- 或 `pip install Pillow`

## 执行流程

### 1. 确定标题

使用用户提供的标题，或从文案中提取核心标题（20 字以内）。

### 2. 确定封面图片来源

**询问用户**：

> 封面图的主题图片，你想怎么来？
> 1. **AI 自动生成** — 根据文案主题自动生成匹配的图片
> 2. **上传自己的图片** — 提供图片路径，我来帮你拼接封面

### 3A. 用户选择「AI 生成」

**继续询问 prompt 方式**：

> AI 图片的提示词，你想怎么来？
> 1. **预设推荐** — 我根据你的文案主题自动生成最佳英文 prompt
> 2. **自定义提示词** — 你提供想要的画面描述，我来翻译成英文 prompt

参考 `{baseDir}/../../references/cover-guide.md` 中的 Prompt 编写规范和配色库。

确认 prompt 后，根据主题从配色库选择底色和字色（必须主动搭配，禁止白底黑字）。

#### 生图模型选择策略

**优先尝试当前对话使用的模型**直接生图（如果当前模型支持图片生成）：
1. 生成 3:2 比例的主题图片，保存到临时文件（如 `/tmp/xhs_ai_img.png`）
2. 调用 cover.sh 时传入 `__USER_IMAGE__:/tmp/xhs_ai_img.png`，跳过脚本内置的 API 调用

**如果当前模型不支持生图**，**询问用户**：

> 当前模型不支持图片生成，请选择生图方式：
> 1. **Google Gemini** — 需要提供 GEMINI_API_KEY（[获取地址](https://aistudio.google.com/apikey)）
> 2. **OpenAI / OpenAI 兼容 API** — 需要提供 API Key 和 Base URL
> 3. **其他方式** — 你来提供图片，我帮你拼接封面

用户选择后，设置对应环境变量再调用 cover.sh：

```bash
# Gemini（默认）
GEMINI_API_KEY=xxx bash {baseDir}/../../scripts/cover.sh "标题" "prompt" [输出路径] [底色hex] [字色hex]

# OpenAI 兼容
IMG_API_TYPE=openai IMG_API_KEY=xxx IMG_API_BASE=https://api.openai.com/v1 IMG_MODEL=dall-e-3 bash {baseDir}/../../scripts/cover.sh "标题" "prompt" [输出路径] [底色hex] [字色hex]

# 腾讯云混元生图（AIART）
IMG_API_TYPE=hunyuan HUNYUAN_SECRET_ID=AKID... HUNYUAN_SECRET_KEY=... bash {baseDir}/../../scripts/cover.sh "标题" "prompt" [输出路径] [底色hex] [字色hex]
```

### 3B. 用户选择「上传图片」

用户提供图片路径后，搭配底色和字色，执行：

```bash
bash {baseDir}/../../scripts/cover.sh "标题文字" "__USER_IMAGE__:/path/to/image.jpg" [输出路径] [底色hex] [字色hex]
```

### 4. 确认输出

封面图默认输出到 `/tmp/xhs_cover.png`。展示给用户确认，不满意可调整配色或重新生成。

## Fallback 链

1. **AI 生图失败** → cover.sh 自动生成渐变色占位图，保证流程不中断
2. **语义断句失败** → cover.sh 自动按标点符号简单断句兜底
3. **ImageMagick 不可用** → 自动降级到 Pillow
4. **两者都不可用** → 报错退出，提示安装

## 参考资料

- 封面设计规范：`{baseDir}/../../references/cover-guide.md`
- 图片处理工具：`{baseDir}/../../scripts/cover.sh`
- 环境检查：`{baseDir}/../../scripts/check_env.sh`
