# Agent Plugins

A curated collection of Claude Code skills and agent plugins for enhanced AI workflows and productivity.

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skills-purple.svg)](https://www.anthropic.com/news/skills)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Transform your Claude Code experience** with specialized skills that extend Claude's capabilities with domain-specific knowledge, workflows, and integrations.

---

## Contents

- [What Are Claude Skills?](#what-are-claude-skills)
- [Available Skills](#available-skills)
- [Getting Started](#getting-started)
- [Creating Skills](#creating-skills)
- [Contributing](#contributing)
- [Resources](#resources)

## What Are Claude Skills?

Claude Skills are customizable workflows that teach Claude how to perform specific tasks according to your unique requirements. Skills enable Claude to execute tasks in a repeatable, standardized manner across all Claude platforms (Claude.ai, Claude Code, and API).

Each skill is a self-contained folder with instructions, scripts, and resources that Claude can invoke to accomplish specialized tasks.

## Available Skills

<!-- SKILLS:START -->
### chrome-fetch-plugin
> Fetch web page content via Chrome DevTools MCP when WebFetch fails (e.g., 'Unable to verify if domain is safe'), when pages require authentication from the user's Chrome session, or when SPAs need JavaScript rendering. Uses the user's running Chrome browser instance with autoConnect.

| Skill | Description |
|-------|-------------|
| `/chrome-fetch` | Fetch web page content using Chrome DevTools MCP when WebFetch fails, returns domain verification... |

### env-config-plugin
> Claude Code environment variable configuration wizard. Interactive guided setup based on user persona (local, proxy, non-Anthropic model, cloud, CI). Optimized for mainland China users. Maintains a YAML catalog of 60+ env vars with smart recommendations.

| Skill | Description |
|-------|-------------|
| `/configuring-env` | 提供 Claude Code 环境变量配置向导。通过交互式问答，根据用户的身份和使用场景， 推荐合适的环境变量配置，并使用 update-config 应用到 settings.json。 当用... |

### gemini-plugin
> Triggers when user wants to ask Gemini questions, generate text/images via Google Gemini, or mentions 'Gemini'. Provides browser-automated Gemini text generation and image creation with persistent Google authentication.

| Skill | Description |
|-------|-------------|
| `/gemini-skill` | 当用户想通过 Google Gemini 生成文本、生成图片、或提到"Gemini"/"问问Gemini"时触发。支持文本问答和图片创建，使用浏览器自动化与 Gemini 网页交互。 |

### meta-plugin
> Meta plugin for Claude Code utilities. Includes: 1) Slash command generator with semantic versioning, automatic backups, and changelog tracking; 2) Task completion notifications with cross-platform support (macOS/Linux/Windows).

| Skill | Description |
|-------|-------------|
| `/notify-on-complete` | Send system notifications when Claude Code completes tasks. Use when the user wants to configure ... |

### openai-plugin
> Generate images through OpenAI-compatible CLI providers and Codex CLI OAuth. Includes cliproxyapi defaults plus a codex-image skill for local gpt-image-2 output without API key management.

| Skill | Description |
|-------|-------------|
| `/codex-image` | Generate images through Codex CLI's built-in image_gen tool with gpt-image-2 and Codex OAuth, wit... |
| `/image-skill` | Use this skill whenever the user wants to generate an image with the OpenAI CLI, mentions OpenAI-... |

### oss-plugin
> Trigger when the user asks to upload, download, list, delete, sync, or generate signed URLs for files on Alibaba Cloud OSS (Object Storage Service). Operates via Python CLI scripts wrapping the oss2 SDK.

| Skill | Description |
|-------|-------------|
| `/oss-skill` | Trigger when the user asks to upload, download, list, delete, or sync files on Alibaba Cloud OSS,... |

### social-autopilot-plugin
> 极客电商社媒自动化：监控漫威/DC/星战等热点新闻，自动生成 Instagram/Facebook/小红书 多渠道帖子并生成草稿或排期发布。支持 /social-autopilot 命令和自然语言触发。

| Skill | Description |
|-------|-------------|
| `/social-autopilot` | 当用户要求监控极客新闻(漫威/DC/星战/F1/游戏)、生成社交媒体帖子、 发布小红书/XHS/RED 笔记、配置Instagram/Facebook/小红书发布渠道、 做多渠道社媒自动化、或提... |

### swarm-plugin
> Decomposes complex tasks into parallel subtasks and coordinates an Agent Team of teammates. Triggers when user describes a multi-part development task or uses keywords like team/swarm/parallel/拆分/并行.

| Skill | Description |
|-------|-------------|
| `/swarm-skill` | Decompose complex development tasks into a parallel Agent Team, create self-contained teammate ta... |

### wechat-plugin
> Generate WeChat official account (微信公众号) cover image layouts as self-contained HTML files. Triggered when user wants to create WeChat cover images, 微信公众号封面, or dual-cover designs (main cover + 朋友圈分享 cover).

| Skill | Description |
|-------|-------------|
| `/wechat-cover-layout-designer` | Generate WeChat official account (微信公众号) dual-cover image layouts as self-contained HTML files. U... |

### xiaohongshu-plugin
> Automate Xiaohongshu (小红书) via Chrome DevTools MCP. Triggered when the user wants to open, log in, browse, search, or interact with Xiaohongshu/小红书. Supports login (QR code or phone number), browsing the feed, searching content, viewing post details, and reading user profiles.

| Skill | Description |
|-------|-------------|
| `/post-to-xhs` | 发布内容到小红书，支持图文笔记、视频笔记和长文。自动判断发布类型，校验标题和素材，用户确认后发布。 |
| `/setup-xhs` | 安装部署小红书自动化环境：Python CLI 引擎 + Chrome 浏览器扩展。 |
| `/xhs-content-plan` | 小红书内容策划助手：搜索分析热门内容和竞品，帮助规划内容方向、选题、标签策略。 |
| `/xhs-cover` | 生成小红书封面图（3:4 比例 1080x1440）。上半部分为 AI 主题图片，下半部分为纯色底+标题文字。 |
| `/xhs-explore` | 浏览小红书推荐流、查看笔记详情和评论。 |
| `/xhs-interact` | 对小红书笔记进行互动：点赞/取消点赞、收藏/取消收藏、发表评论、回复评论。 |
| `/xhs-login` | 管理小红书登录状态：检查是否已登录、二维码扫码登录、手机验证码登录、退出登录。 |
| `/xhs-profile` | 查看小红书用户主页：基本信息、粉丝/关注/获赞数据、发布的笔记列表。 |
| `/xhs-search` | 搜索小红书笔记，支持关键词搜索和多维度筛选。 |
| `/xiaohongshu` | 小红书（RED/XHS）自动化助手。通过 Python CLI 引擎 + Chrome 浏览器扩展，提供完整的小红书操作能力：登录、发布图文/视频/长文、搜索笔记、浏览详情、点赞收藏评论、查看博... |

<!-- SKILLS:END -->

---

## Getting Started

### Installing Skills

#### Option 1: One-Line Install (Recommended)

```bash
npx skills add istarwyh/agent-plugins
```

#### Option 2: Using Claude Code CLI

```bash
# Add the marketplace (one-time setup)
claude plugin marketplace add istarwyh/agent-plugins

# Install a plugin
claude plugin install env-config-plugin@agent-plugins
```

### Using Skills in Claude Code

1. Install plugins using one of the methods above
2. Restart Claude Code: `claude`
3. Skills load automatically and activate when relevant
4. Check installed plugins: `claude plugin list`

### Using Skills in Claude.ai

1. Click the skill icon (🧩) in your chat interface
2. Upload the skill's SKILL.md file
3. Claude automatically activates the skill based on your task

### Using Skills via API

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    skills=["skill-id-here"],
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

See the [Skills API documentation](https://docs.claude.com/en/api/skills-guide) for details.

---

## Creating Skills

### Basic Skill Structure

Each skill is a folder containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: Skill instructions and metadata
├── scripts/          # Optional: Helper scripts
├── templates/        # Optional: Document templates
├── resources/        # Optional: Reference files
└── README.md         # Optional: User-facing documentation
```

### Minimal SKILL.md Template

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---

# My Skill Name

Detailed description of the skill's purpose and capabilities.

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Instructions

[Detailed instructions for Claude on how to execute this skill]

## Examples

[Real-world examples showing the skill in action]
```

### Skill Best Practices

- Focus on specific, repeatable tasks
- Include clear examples and edge cases
- Write instructions for Claude, not end users
- Test across Claude.ai, Claude Code, and API when possible
- Document prerequisites and dependencies
- Include error handling guidance

For detailed guidance, see our [template-skill](./template-skill/) example.

---

## Contributing

We welcome contributions! Whether you have a skill to share or want to improve existing ones, please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to submit new skills
- Skill quality standards
- Pull request process
- Code of conduct

### Quick Contribution Steps

1. Ensure your skill is based on a real use case
2. Check for duplicates in existing skills
3. Follow the skill structure template
4. Test your skill across platforms
5. Submit a pull request with clear documentation

---

## Resources

### Official Documentation

- [Claude Skills Overview](https://www.anthropic.com/news/skills) - Official announcement and features
- [Skills User Guide](https://support.claude.com/en/articles/12512180-using-skills-in-claude) - How to use skills in Claude
- [Creating Custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) - Skill development guide
- [Skills API Documentation](https://docs.claude.com/en/api/skills-guide) - API integration guide

### Community Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official example skills
- [Awesome Claude Skills](https://github.com/ComposioHQ/awesome-claude-skills) - Community skill collection
- [Claude Community](https://community.anthropic.com) - Discuss skills with other users

### Inspiration

- [Lenny's Newsletter](https://www.lennysnewsletter.com/p/everyone-should-be-using-claude-code) - 50 ways people use Claude Code
- [Skills Marketplace](https://claude.ai/marketplace) - Discover and share skills

---

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Individual skills may have different licenses - please check each skill's folder for specific licensing information.

---

## Support

- **Issues & Bug Reports**: [GitHub Issues](https://github.com/istarwyh/agent-plugins/issues)
- **General Support**: [Support Guide](SUPPORT.md) - How to report issues and get help
- **Discussions**: [GitHub Discussions](https://github.com/istarwyh/agent-plugins/discussions)

---

**Note**: Claude Skills work across Claude.ai, Claude Code, and the Claude API. Once you create a skill, it's portable across all platforms, making your workflows consistent everywhere you use Claude.
