# 小红书渠道

`social-autopilot` 只做热点监控、文案/卡片生成和渠道编排；小红书登录、填表、发布等浏览器自动化能力复用仓库里的 `xiaohongshu-plugin`。

## 依赖的已有 skill

- `/xiaohongshu` — 小红书总入口
- `/setup-xhs` — 安装 Python CLI 引擎和 Chrome 扩展
- `/xhs-login` — 检查/完成登录
- `/post-to-xhs` — 发布图文、视频、长文
- `/image-skill` — 使用图片生成 LLM 生成新闻配图或封面主体图
- `/xhs-cover` — 生成 1080x1440 小红书封面

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

如果小红书 CLI 是手动安装的，在 `~/social-autopilot/.env` 设置：

```bash
XHS_CLI_PATH=/absolute/path/to/xiaohongshu-skills/scripts/cli.py
```

## 发布约束

- 标题最多 20 个中文字；ASCII 约每 2 个字符算 1 个中文单位。
- 图文笔记至少需要 1 张图片。
- 图片和视频不能混用。
- 正文段落用空行分隔。
- 需要 AI 图片时优先调用 `/image-skill`；缺失时按根 README 安装 `openai-plugin`。
- 发布前展示标题、正文、标签、图片路径和可见范围。
- 默认只填入发布页，不自动点击发布。
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

预览小红书草稿，不调用 CLI：

```bash
python scripts/run.py publish_channels.py --channel xiaohongshu --dry-run
```

填入小红书发布页但不点击发布：

```bash
python scripts/run.py publish_channels.py --channel xiaohongshu
```

启用小红书渠道后，新生成内容会先写入平台无关 brief，再生成 `platform=xiaohongshu` 的小红书专属草稿：

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
