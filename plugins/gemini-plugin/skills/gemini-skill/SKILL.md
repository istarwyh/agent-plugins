---
name: gemini-skill
description: 当用户想通过 Google Gemini 生成文本、生成图片、或提到"Gemini"/"问问Gemini"时触发。支持文本问答和图片创建，使用浏览器自动化与 Gemini 网页交互。
---

# Gemini AI 技能

通过浏览器自动化与 Google Gemini 交互，支持文本生成和图片创建。每次交互打开新浏览器会话，获取响应后自动关闭。

## 核心规则：必须使用 run.py

**所有命令必须通过 `python scripts/run.py [脚本名]` 执行，不可直接调用脚本。**

`run.py` 自动处理：创建 `.venv` -> 安装依赖 -> 激活环境 -> 执行脚本。

## 核心工作流

### 1. 检查认证状态

```bash
python scripts/run.py auth_manager.py status
```

### 2. 认证（首次使用）

```bash
python scripts/run.py auth_manager.py setup
```

浏览器会自动打开，用户需手动登录 Google 账号。告知用户："浏览器窗口将打开，请登录 Google 账号"。

### 3. 文本生成

```bash
python scripts/run.py ask_gemini.py --question "你的问题"
python scripts/run.py ask_gemini.py --question "..." --show-browser  # 调试模式
```

参数：
- `--question`（必需）：要问 Gemini 的问题
- `--show-browser`：显示浏览器窗口用于调试

### 4. 图片生成

```bash
python scripts/run.py generate_image.py --prompt "图片描述"
python scripts/run.py generate_image.py --prompt "..." --output ./my_images
python scripts/run.py generate_image.py --prompt "..." --headless
python scripts/run.py generate_image.py --prompt "..." --debug
```

参数：
- `--prompt`（必需）：图片描述
- `--output`：输出目录（默认当前目录）
- `--headless`：隐藏浏览器运行
- `--debug`：调试模式

输出格式：`gemini_image_1_[时间戳].png`

## 认证管理

```bash
python scripts/run.py auth_manager.py setup    # 初始设置（浏览器可见）
python scripts/run.py auth_manager.py status   # 检查状态
python scripts/run.py auth_manager.py reauth   # 重新认证
python scripts/run.py auth_manager.py clear    # 清除认证
```

## 决策流程

```
用户请求文本/图片 → 检查认证(status) → 未认证则 setup → 执行对应脚本 → 返回结果
```

## 数据存储

所有数据存储在 `~/.claude/skills/gemini-skill/data/`：
- `auth_info.json` - 认证状态
- `browser_state/` - 浏览器 cookies 和会话

受 `.gitignore` 保护，不会提交到 git。

## 配置

可选 `.env` 文件：
```env
HEADLESS=false
SHOW_BROWSER=false
STEALTH_ENABLED=true
TYPING_WPM_MIN=160
TYPING_WPM_MAX=240
PAGE_LOAD_TIMEOUT=30000
```

## 局限性

- 无会话持久性（每次查询 = 新浏览器）
- 免费 Google 账户有速率限制
- 图片生成可能需要几分钟
- 依赖 Gemini 网页界面可用性

## 参考文档

详细信息请查阅 `references/` 目录：
- `api_reference.md` - 所有脚本的详细 API 文档
- `troubleshooting.md` - 常见问题和解决方案
- `usage_patterns.md` - 使用模式和工作流示例
- `AUTHENTICATION.md` - 认证架构的技术细节
