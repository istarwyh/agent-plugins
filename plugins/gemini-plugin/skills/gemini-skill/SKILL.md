---
name: gemini-skill
description: Interact with Google Gemini for AI-powered conversations, Q&A, and image generation. Features browser automation, persistent authentication, and multi-modal capabilities including text generation and image creation. (user)
---

# Gemini AI Assistant Skill

Interact with Google Gemini for AI-powered conversations, question answering, and image generation. Each interaction opens a fresh browser session, retrieves the response, and closes cleanly.

**Main capabilities:**
- **Text Generation**: Ask questions and get AI-generated responses
- **Image Generation**: Create images from text descriptions
- **Multi-modal Support**: Handle both text and image-based queries
- **Browser Automation**: Seamless integration with Gemini web interface

---

## 🚀 Quick Start Guide / 快速上手指南

### One-Time Setup / 一次性设置

#### 1. Authentication / 认证（首次使用）

```bash
python scripts/run.py auth_manager.py setup
```

Browser will automatically open - please log in to your Google account. After authentication, both Gemini features are ready to use.

浏览器会自动打开，请登录您的 Google 账号。认证完成后，Gemini 功能都可以使用。

#### 2. Verify Authentication / 验证认证状态

```bash
python scripts/run.py auth_manager.py status
```

### Quick Examples / 快速示例

**Text Generation / 文本生成:**
```bash
# General knowledge / 通用知识问题
python scripts/run.py ask_gemini.py --question "什么是人工智能？"

# Creative writing / 创意写作
python scripts/run.py ask_gemini.py --question "帮我写一首关于春天的诗"

# Code generation / 代码生成
python scripts/run.py ask_gemini.py --question "用 Python 写一个快速排序算法"

# Debug mode / 调试模式
python scripts/run.py ask_gemini.py --question "..." --show-browser
```

**Image Generation / 图片生成:**
```bash
# Generate image / 生成图片
python scripts/run.py generate_image.py --prompt "画一个可爱的雪人"

# Specify output directory / 指定输出目录
python scripts/run.py generate_image.py --prompt "A futuristic city" --output ./my_images

# Generate art / 生成艺术作品
python scripts/run.py generate_image.py --prompt "Abstract art with vibrant colors"
```

**Image Storage / 图片保存位置:**
- Default: Current directory / 默认保存在当前目录
- Custom: Use `--output` parameter / 使用 `--output` 指定其他目录
- Format: `gemini_image_1_[timestamp].png` / 文件名格式

## When to Use This Skill / 使用场景

**Text Generation Mode / 文本生成模式** - Trigger when user:
- Asks general knowledge questions / 询问通用知识问题
- Needs help with writing, brainstorming, or creative tasks / 需要写作、头脑风暴或创意任务
- Wants code generation or explanation / 需要代码生成或解释
- Uses phrases like "ask Gemini", "query AI", "help me write" / 使用类似 "问问 Gemini"、"查询 AI"、"帮我写" 的短语

**Image Generation Mode / 图片生成模式** - Trigger when user:
- Requests image creation or generation / 请求图片创建或生成
- Uses visual descriptions or wants to create visuals / 使用视觉描述或想创建视觉内容
- Uses phrases like "generate image", "create picture", "draw" / 使用类似 "生成图片"、"创建图片"、"画" 的短语
- Mentions specific visual elements they want created / 提到想要创建的特定视觉元素

## Critical: Always Use run.py Wrapper

**NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:**

```bash
# ✅ CORRECT - Always use run.py:
python scripts/run.py auth_manager.py status
python scripts/run.py ask_gemini.py --question "..."
python scripts/run.py generate_image.py --prompt "..."

# ❌ WRONG - Never call directly:
python scripts/auth_manager.py status  # Fails without venv!
```

The `run.py` wrapper automatically:
1. Creates `.venv` if needed
2. Installs all dependencies
3. Activates environment
4. Executes script properly

## Core Workflow

### Step 1: Check Authentication Status
```bash
python scripts/run.py auth_manager.py status
```

If not authenticated, proceed to setup.

### Step 2: Authenticate (One-Time Setup)
```bash
# Browser MUST be visible for manual Google login
python scripts/run.py auth_manager.py setup
```

**Important:**
- Browser is VISIBLE for authentication
- Browser window opens automatically
- User must manually log in to Google
- Tell user: "A browser window will open for Google login"

### Step 3: Generate Text Responses / 生成文本响应

```bash
# Ask Gemini a question / 向 Gemini 提问
python scripts/run.py ask_gemini.py --question "Your question here"

# Show browser for debugging / 显示浏览器进行调试
python scripts/run.py ask_gemini.py --question "..." --show-browser
```

**Use Cases / 使用场景:**
- General knowledge questions / 通用知识问题
- Creative writing and brainstorming / 创意写作和头脑风暴
- Code generation and explanation / 代码生成和解释
- Problem-solving and analysis / 问题解决和分析
- Language translation and summarization / 语言翻译和总结

### Step 4: Generate Images / 生成图片

```bash
# Generate images using Gemini / 使用 Gemini 生成图片
python scripts/run.py generate_image.py --prompt "Your image description"

# Specify output directory / 指定输出目录
python scripts/run.py generate_image.py --prompt "..." --output ./my_images

# Run in headless mode (hidden browser) / 在无头模式下运行（隐藏浏览器）
python scripts/run.py generate_image.py --prompt "..." --headless

# Enable debug mode with pauses / 启用带暂停的调试模式
python scripts/run.py generate_image.py --prompt "..." --debug
```

**Examples / 示例:**
```bash
# Generate a cute snowman / 生成一个可爱的雪人
python scripts/run.py generate_image.py --prompt "画一个可爱的雪人"

# Generate a futuristic city / 生成一个未来城市
python scripts/run.py generate_image.py --prompt "A futuristic city with flying cars"

# Generate abstract art / 生成抽象艺术
python scripts/run.py generate_image.py --prompt "Abstract art with vibrant colors"
```

**Image Generation Features / 图片生成功能:**
- Automatic image detection using precise selectors / 使用精确选择器自动检测图片
- Download button integration for high-quality images / 下载按钮集成以获取高质量图片
- Screenshot fallback for reliability / 可靠的截图备用方案
- Supports multiple images per generation / 支持每次生成多个图片
- Saves as PNG files with timestamps / 保存为带时间戳的 PNG 文件
- Custom output directory support / 支持自定义输出目录

## Script Reference

### Authentication Management (`auth_manager.py`)
```bash
python scripts/run.py auth_manager.py setup    # Initial setup (browser visible)
python scripts/run.py auth_manager.py status   # Check authentication
python scripts/run.py auth_manager.py reauth   # Re-authenticate (browser visible)
python scripts/run.py auth_manager.py clear    # Clear authentication
```

### Gemini Text Interface (`ask_gemini.py`)
```bash
python scripts/run.py ask_gemini.py --question "..." [--show-browser]
```

**Parameters:**
- `--question` (required): Text question to ask Gemini
- `--show-browser`: Show browser window for debugging

**Features:**
- Multi-language support (Chinese and English interfaces)
- Multiple input selector strategies
- Response stability detection
- 2-minute timeout for responses
- Error handling and retry logic

### Image Generation (`generate_image.py`)
```bash
python scripts/run.py generate_image.py --prompt "..." [--output DIR] [--headless] [--debug]
```

**Parameters:**
- `--prompt` (required): Image description for generation
- `--output`: Output directory (default: current directory)
- `--headless`: Run browser in hidden mode
- `--debug`: Enable debug mode with pauses

**Features:**
- Automatic image generation mode detection
- Download button integration for high-quality images
- Screenshot fallback for reliability
- Multiple image support per generation
- 5-minute timeout for image generation
- Custom filename generation with timestamps

## Environment Management

The virtual environment is automatically managed:
- First run creates `.venv` automatically
- Dependencies install automatically
- Chromium browser installs automatically
- Everything isolated in skill directory

Manual setup (only if automatic fails):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m patchright install chromium
```

## Data Storage

All data stored in `~/.claude/skills/gemini-skill/data/`:
- `auth_info.json` - Authentication status and session data
- `browser_state/` - Browser cookies and session persistence

**Security:** Protected by `.gitignore`, never commit to git.

## Configuration

Optional `.env` file in skill directory:
```env
HEADLESS=false           # Browser visibility
SHOW_BROWSER=false       # Default browser display
STEALTH_ENABLED=true     # Human-like behavior
TYPING_WPM_MIN=160       # Typing speed
TYPING_WPM_MAX=240
PAGE_LOAD_TIMEOUT=30000  # Page load timeout in milliseconds
```

## Decision Flow

### Text Generation Workflow
```
User asks question or requests text
    ↓
Check auth → python scripts/run.py auth_manager.py status
    ↓
If not authenticated → python scripts/run.py auth_manager.py setup
    ↓
Ask Gemini → python scripts/run.py ask_gemini.py --question "..."
    ↓
Return response to user
```

### Image Generation Workflow
```
User requests image generation
    ↓
Check auth → python scripts/run.py auth_manager.py status
    ↓
If not authenticated → python scripts/run.py auth_manager.py setup
    ↓
Generate image → python scripts/run.py generate_image.py --prompt "..."
    ↓
Download and save images
    ↓
Return image paths to user
```

## Troubleshooting / 故障排查

| Problem / 问题 | Solution / 解决方案 |
|---------|----------|
| ModuleNotFoundError | Use `run.py` wrapper / 使用 `run.py` 包装器 |
| Authentication fails / 认证失败 | Browser must be visible for setup! / 浏览器必须可见才能设置！ |
| Rate limit exceeded / 达到速率限制 | Wait or switch Google account / 等待或切换 Google 账号 |
| Browser crashes / 浏览器崩溃 | Clear browser data and restart / 清除浏览器数据并重启 |
| Image generation fails / 图片生成失败 | Try with `--debug` flag to inspect / 使用 `--debug` 标志进行检查 |
| No response from Gemini / Gemini 无响应 | Check internet connection and auth status / 检查网络连接和认证状态 |
| Download fails / 下载失败 | Fallback to screenshot mode automatically / 自动回退到截图模式 |

### FAQ / 常见问题

**Q: 认证失败怎么办？/ What to do if authentication fails?**
A: 确保网络连接正常，重试：/ Ensure network connection is normal, retry:
```bash
python scripts/run.py auth_manager.py reauth
```

**Q: 超时错误？/ Timeout errors?**
A: 已设置 5 分钟超时，如果网络很慢，可以使用 `--show-browser` 查看进度
A: 5-minute timeout is set. If network is slow, use `--show-browser` to see progress

**Q: 如何清除所有数据？/ How to clear all data?**
A: / A:
```bash
python scripts/run.py cleanup_manager.py --confirm
```

## Best Practices / 最佳实践

1. **Always use run.py / 始终使用 run.py** - Handles environment automatically / 自动处理环境
2. **Check auth first / 首先检查认证** - Before any operations / 在任何操作之前
3. **Use specific prompts / 使用具体的提示** - Better prompts give better results / 更好的提示产生更好的结果
4. **Browser visible for auth / 认证时浏览器可见** - Required for manual login / 手动登录必需
5. **Include context / 包含上下文** - Each question is independent / 每个问题都是独立的
6. **For images / 对于图片** - Use descriptive prompts with visual details / 使用带有视觉细节的描述性提示
7. **Debug mode / 调试模式** - Use `--debug` or `--show-browser` for troubleshooting / 使用 `--debug` 或 `--show-browser` 进行故障排查

## Usage in Claude Code / 在 Claude Code 中使用

When you mention "Gemini" in Claude Code, the skill will automatically activate.

当您在 Claude Code 中提到 "Gemini" 时，skill 会自动激活。

**Example Dialogue / 示例对话:**

```
You: 问问 Gemini 什么是量子计算 / Ask Gemini what quantum computing is
Claude: [Automatically calls ask_gemini.py and returns result / 自动调用 ask_gemini.py 并返回结果]

You: 用 Gemini 生成一个机器人的图片 / Generate a robot image with Gemini
Claude: [Automatically calls generate_image.py and returns image paths / 自动调用 generate_image.py 并返回图片路径]
```

## Quick Command Reference / 快速命令参考

```bash
# Gemini Text Query / Gemini 文本查询
python scripts/run.py ask_gemini.py --question "..."

# Gemini Image Generation / Gemini 图片生成
python scripts/run.py generate_image.py --prompt "..." [--output DIR] [--headless] [--debug]

# Authentication Management / 认证管理
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py reauth
python scripts/run.py auth_manager.py clear
```

---

**Important Note / 重要提示:** All commands must use `python scripts/run.py [script_name]` format to properly load the virtual environment!

**重要提示:** 所有命令都必须使用 `python scripts/run.py [脚本名]` 的格式，这样才能正确加载虚拟环境！

## Limitations / 局限性

- No session persistence (each query = new browser) / 无会话持久性（每次查询 = 新浏览器）
- Rate limits on free Google accounts / 免费 Google 账户的速率限制
- Image generation may take several minutes / 图片生成可能需要几分钟
- Browser overhead (few seconds per query) / 浏览器开销（每次查询几秒）
- Dependent on Gemini web interface availability / 依赖于 Gemini 网络界面的可用性

## Resources (Skill Structure)

**Important directories and files:**

- `scripts/` - All automation scripts (ask_gemini.py, generate_image.py, etc.)
- `data/` - Local storage for authentication and browser state
- `references/` - Extended documentation:
  - `api_reference.md` - Detailed API documentation for all scripts
  - `troubleshooting.md` - Common issues and solutions
  - `usage_patterns.md` - Best practices and workflow examples
- `.venv/` - Isolated Python environment (auto-created on first run)
- `.gitignore` - Protects sensitive data from being committed
