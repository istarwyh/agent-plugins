# 小红书渠道

`social-autopilot` 只做热点监控、文案/卡片生成和渠道编排；小红书登录、填表、发布等浏览器自动化能力复用仓库里的 `xiaohongshu-plugin`。

## 依赖的已有 skill

- `/xiaohongshu` — 小红书总入口
- `/setup-xhs` — 安装 Python CLI 引擎和 Chrome 扩展
- `/xhs-login` — 检查/完成登录
- `/post-to-xhs` — 发布图文、视频、长文
- `/codex-image` — 使用 Codex CLI + gpt-image-2 生成高质量新闻封面/素材
- `/image-skill` — OpenAI-compatible 图片生成备选
- `/xhs-cover` — 生成或裁切 1080x1440 小红书封面

## 安装方式

优先按根 README 安装整个插件仓库：

```bash
npx skills add istarwyh/agent-plugins
```

或使用 Claude Code 插件市场：

```bash
claude plugin marketplace add istarwyh/agent-plugins
claude plugin install xiaohongshu-plugin@agent-plugins
```

安装后重启 Claude Code，并运行：

```text
/setup-xhs
/xhs-login
```

脚本会自动检测插件市场缓存和本仓库里的 versioned `xiaohongshu-plugin` CLI。如果小红书 CLI 是手动安装的，在 `~/social-autopilot/.env` 设置：

```bash
XHS_CLI_PATH=/absolute/path/to/xiaohongshu-skills/scripts/cli.py
```

## 发布约束

- 标题最多 20 个中文字；ASCII 约每 2 个字符算 1 个中文单位。
- 图文笔记至少需要 1 张图片；发布层会优先使用 `card_path`（包括 `generate_ai_covers.py` 或 `/codex-image` 生成的 AI 封面），缺失时自动生成模板新闻卡片。
- 图片和视频不能混用。
- 正文段落用空行分隔。
- 需要 AI 图片时优先调用 `/codex-image` 或运行 `generate_ai_covers.py`；`/image-skill` 是备选，缺失时按根 README 安装 `openai-plugin`。
- 发布前展示标题、正文、标签、图片路径和可见范围。
- 默认只填入发布页，不自动点击发布；用户明确确认后可用 `publish_mode: "publish"` 或 `--xhs-publish-mode publish` 直接发布。
- 发布超时或结果不确定时，先查 `xiaohongshu-plugin/references/publish-troubleshooting.md` 并确认个人主页状态，未确认失败前不要重试。

## 内容生成与字段映射

生成阶段先创建平台无关 `content_briefs`，再为小红书生成 `platform=xiaohongshu` 的专属 `post_drafts` 行。发布阶段只消费这条小红书专属草稿，不再把 Meta 文案临时改写成小红书文案。

| social-autopilot 字段 | 小红书字段 |
|---|---|
| `platform_title` | 小红书标题，生成阶段控制在 20 中文字单位以内，发布前仍会防御性截断 |
| `caption` | 小红书中文正文，生成阶段已按小红书风格分段 |
| `hashtags` | 小红书话题标签，通常 3-6 个，不依赖 `#` |
| `card_path` | 图文笔记图片 |
| `news_url` | 正文末尾来源 |

旧草稿如果没有 `platform_title`，发布层会 fallback 到 `news_title` 并合并配置标签，保证兼容。

## 状态检查

运行：

```bash
python scripts/run.py status.py
```

状态含义：

- `CLI: 未安装`：按上方安装命令安装 `xiaohongshu-plugin`。
- `Login: 未登录`：运行 `/xhs-login`。
- `环境检查失败`：运行 `/setup-xhs` 检查 Chrome Bridge 和扩展。

## 运行方式

端到端准备小红书内容（抓新闻、生成中文草稿、生成 Codex AI 封面，但不发布）：

```bash
python scripts/run.py pipeline --channel xiaohongshu --limit 5 --ai-covers --ai-cover-limit 3 --no-publish
```

临时指定小红书渠道时可用 `--channel xiaohongshu`，不必先把 `config.json` 里的 xiaohongshu 设为 enabled。

预览小红书草稿，不调用 CLI：

```bash
python scripts/run.py publish_channels.py --channel xiaohongshu --dry-run
```

为待发布小红书草稿生成高质量 AI 封面：

```bash
python scripts/run.py generate_ai_covers.py --platform xiaohongshu --limit 3 --quality high
```

填入小红书发布页但不点击发布：

```bash
python scripts/run.py publish_channels.py --channel xiaohongshu
```

用户确认后直接发布：

```bash
python scripts/run.py publish_channels.py --channel xiaohongshu --xhs-publish-mode publish
```

启用小红书渠道后，新生成内容会先写入平台无关 brief，再生成 `platform=xiaohongshu` 的小红书专属草稿。长期使用可写入配置，临时任务用 `--channel xiaohongshu` 即可：

```json
{
  "channels": {
    "xiaohongshu": {
      "enabled": true,
      "publish_mode": "draft",
      "visibility": "公开可见",
      "tags": ["极客资讯", "漫威", "DC", "星球大战", "游戏"]
    }
  }
}
```
