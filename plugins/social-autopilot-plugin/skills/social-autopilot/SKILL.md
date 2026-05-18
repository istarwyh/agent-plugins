---
name: social-autopilot
description: >
  当用户要求监控极客新闻(漫威/DC/星战/F1/游戏)、生成社交媒体帖子、
  配置Instagram/Facebook/小红书/XHS/RED发布渠道、做多渠道社媒自动化、
  或提到热点资讯自动化时触发。也在用户输入 /social-autopilot 时触发。
---

# 极客电商社媒自动化

监控热点新闻 → 生成平台中立内容简报 → 按启用渠道生成平台专属草稿 → 新闻卡片图片 → 按渠道填表或排期发布。
所有命令通过 `python scripts/run.py <脚本> [参数...]` 从 skill 根目录执行。

## 前置条件

1. Python >= 3.11
2. 安装依赖: `python -m pip install -r requirements.txt`
3. 安装 Playwright 浏览器: `python -m playwright install chromium`
4. 复制 `.env.example` 到 `~/social-autopilot/.env` 并填入 `OPENAI_API_KEY`
5. 如需 Meta 渠道，配置 Meta API；如需小红书渠道，安装并登录 `xiaohongshu-plugin`

## 命令

| 操作 | 命令 |
|------|------|
| 首次配置 | `python scripts/run.py setup.py` |
| 抓取新闻 | `python scripts/run.py poll_news.py --priority high` |
| 生成帖子 | `python scripts/run.py generate_posts.py` |
| 生成卡片图 | `python scripts/run.py generate_card.py --title "标题" --category marvel` |
| Meta排期 | `python scripts/run.py schedule_meta.py --mode facebook_only` |
| 小红书渠道预览 | `python scripts/run.py publish_channels.py --channel xiaohongshu --dry-run` |
| 发布全部启用渠道 | `python scripts/run.py publish_channels.py --enabled` |
| 全链路运行 | `python scripts/run.py pipeline` |
| 安装定时任务 | `python scripts/run.py install_cron.py` |
| 状态检查 | `python scripts/run.py status.py` |
| 试运行 | 任意命令加 `--dry-run`（只打印不执行） |

## 首次配置流程

当用户首次使用此 skill 时，按以下步骤引导：

1. 运行 `python scripts/run.py setup.py` 创建 `~/social-autopilot/` 目录结构和配置文件。
2. 配置 LLM API Key：编辑 `~/social-autopilot/.env`，填入 `OPENAI_API_KEY`。
3. 配置发布渠道：
   - Meta：参考 `SETUP_GUIDE.md` 完成 Meta App 和 Token 配置。
   - 小红书：先安装 `xiaohongshu-plugin`，再运行 `/setup-xhs` 和 `/xhs-login`。
4. 试运行验证：`python scripts/run.py pipeline --dry-run`。
5. 按需安装定时任务：`python scripts/run.py install_cron.py`。

如果用户尚未配置任何发布渠道，全链路终点为生成草稿（JSON + 卡片图），用户可手动发布。

## 小红书渠道

小红书发布复用仓库里的 `xiaohongshu-plugin`，不要在本 skill 中复制浏览器自动化逻辑。

如果 `python scripts/run.py status.py` 显示未检测到小红书渠道，引导用户按根 README 安装：

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

如用户已经手动安装小红书 CLI，可在 `~/social-autopilot/.env` 设置：

```bash
XHS_CLI_PATH=/absolute/path/to/xiaohongshu-skills/scripts/cli.py
```

小红书图文笔记至少需要一张图片。优先使用本 skill 生成的 `card_path`；如果没有可用图片，提示用户先生成卡片，或使用 `/xhs-cover` 生成 1080x1440 封面。

更多细节见 `references/channels/xiaohongshu.md`。

## 日常使用流程

用户输入 `/social-autopilot` 或“帮我看看有什么新闻”时：

1. 运行 `python scripts/run.py pipeline`。
2. 向用户报告结果：抓取 X 条新闻、生成 Y 条帖子、各渠道处理 Z 条。
3. 展示生成的帖子草稿、卡片路径和目标渠道供用户预览。
4. 如用户要求修改，直接编辑 `~/social-autopilot/output/drafts/` 中的 JSON 或重新生成。

## 多渠道配置

渠道配置位于 `~/social-autopilot/config.json` 的 `channels` 字段：

```json
{
  "channels": {
    "meta": {"enabled": true, "mode": "facebook_only"},
    "xiaohongshu": {
      "enabled": false,
      "publish_mode": "draft",
      "visibility": "公开可见",
      "tags": ["极客资讯", "漫威", "DC", "星球大战", "游戏"]
    }
  }
}
```

小红书默认关闭，用户明确启用后才会生成 `platform=xiaohongshu` 的平台专属草稿。

## 内容生成职责分离

生成阶段先读取 `channels` 配置，确定目标平台，再生成内容：

1. `content_briefs`：平台无关复用层，保存新闻事实、相关性、内容角度、商品关联、视觉方向和基础标签。
2. `post_drafts`：平台专属发布队列，每个启用平台一条草稿。Meta 行保存 PT-BR 文案和 20 个 hashtag；小红书行保存中文 `platform_title`、中文正文和 3-6 个话题。

发布模块只消费对应平台的 `post_drafts`，不再临时把 Meta 文案转换成小红书文案。

## 安全规则

- **确认后再发布**: 排期或发布前先展示帖子内容、图片路径和目标渠道让用户确认。
- **小红书默认不自动发布**: 默认只调用 `fill-publish` 填表/生成待发布草稿，不调用 `click-publish`。
- **不提交 .env**: 包含 API Key 和 Token，绝不提交到 git。
- **Token 安全**: Meta Page Token 存储在 `.env` 中，不输出到日志。
- **内容审核**: 保留人工审核环节，避免自动发布不当内容。
- **回滚**: Meta 已排期帖子可通过 Graph API 删除；小红书发布前取消时使用 `/post-to-xhs` 中的保存草稿流程。

## 参考文档

- `SETUP_GUIDE.md` — Meta API 全流程配置引导
- `references/channels/xiaohongshu.md` — 小红书渠道配置和发布约束
- `references/card-design.md` — 新闻卡片设计规范
- `references/troubleshooting.md` — 常见问题排查
