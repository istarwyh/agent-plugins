---
name: social-autopilot
description: >
  当用户要求监控极客新闻(漫威/DC/星战/F1/游戏)、生成社交媒体帖子、
  发布小红书/XHS/RED 笔记、配置Instagram/Facebook/小红书发布渠道、
  做多渠道社媒自动化、或提到热点资讯自动化时触发。用户说“帮我发一批小红书热点”、
  “直接发小红书”、“发布漫威/星战/游戏资讯到小红书”时也必须使用本 skill，默认执行找新闻
  → 生成小红书中文草稿 → Codex AI 封面 → 预览确认 → 发布的一条龙流程。
  也在用户输入 /social-autopilot 时触发。
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
6. 如需高质量 AI 封面/素材，安装 `openai-plugin` 并优先使用 `/codex-image`；`/image-skill` 可作为 OpenAI-compatible 备选

## 命令

| 操作 | 命令 |
|------|------|
| 首次配置 | `python scripts/run.py setup.py` |
| 抓取新闻 | `python scripts/run.py poll_news.py --priority high` |
| 生成帖子 | `python scripts/run.py generate_posts.py --channel xiaohongshu --limit 5` |
| AI 封面生成 | `python scripts/run.py generate_ai_covers.py --platform xiaohongshu --limit 3`（Codex CLI / `/codex-image` 工作流） |
| AI 图片生成 | 优先调用 `/codex-image`，备选 `/image-skill`，缺失时提示安装 `openai-plugin` |
| 模板卡片图 | `python scripts/run.py generate_card.py --title "标题" --category marvel` |
| Meta排期 | `python scripts/run.py schedule_meta.py --mode facebook_only` |
| 小红书渠道预览 | `python scripts/run.py publish_channels.py --channel xiaohongshu --dry-run` |
| 小红书直接发布 | `python scripts/run.py publish_channels.py --channel xiaohongshu --xhs-publish-mode publish` |
| 发布全部启用渠道 | `python scripts/run.py publish_channels.py --enabled` |
| 小红书一条龙准备 | `python scripts/run.py pipeline --channel xiaohongshu --limit 5 --ai-covers --ai-cover-limit 3 --no-publish` |
| 全链路运行 | `python scripts/run.py pipeline --limit 5`；指定渠道用 `--channel xiaohongshu`，需要 AI 封面时加 `--ai-covers --ai-cover-limit 3` |
| 安装定时任务 | `python scripts/run.py install_cron.py` |
| 状态检查 | `python scripts/run.py status.py` |
| 试运行 | 任意命令加 `--dry-run`（只打印预览，不改发布状态、不调用发布 CLI） |

## 首次配置流程

当用户首次使用此 skill 时，按以下步骤引导：

1. 运行 `python scripts/run.py setup.py` 创建 `~/social-autopilot/` 目录结构和配置文件。
2. 配置 LLM API Key：编辑 `~/social-autopilot/.env`，填入 `OPENAI_API_KEY`。
3. 检查 AI 图片生成能力：优先使用 `/codex-image`（Codex OAuth + gpt-image-2），备选 `/image-skill`；如果不可用，按根 README 安装 `openai-plugin`。
4. 配置发布渠道：
   - Meta：参考 `SETUP_GUIDE.md` 完成 Meta App 和 Token 配置。
   - 小红书：先安装 `xiaohongshu-plugin`，再运行 `/setup-xhs` 和 `/xhs-login`。
5. 先跑 LLM 预检和小批量试运行：`python scripts/run.py pipeline --dry-run --limit 3`。
6. 按需安装定时任务：`python scripts/run.py install_cron.py`。

如果用户尚未配置任何发布渠道，全链路终点为生成草稿（JSON + 卡片图），用户可手动发布。

## AI 图片生成

当用户要生成新闻配图、封面、海报、视觉素材或明确要求“用图片生成 LLM”时，优先调用 `/codex-image`（Codex CLI 的 gpt-image-2 工作流），不要只用本 skill 的 HTML 模板截图。`generate_ai_covers.py` 可批量读取待发布草稿并按 codex-image 风格生成封面；`generate_card.py` 只是模板卡片 fallback，适合没有图片模型时生成可用占位卡片。

如果 `/codex-image` 或 `/image-skill` 不可用，提示用户按根 README 安装：

```bash
npx skills add istarwyh/agent-plugins
```

或使用 Claude Code 插件市场：

```bash
claude plugin marketplace add istarwyh/agent-plugins
claude plugin install openai-plugin@agent-plugins
```

安装后重启 Claude Code；如使用 `/codex-image`，还需要本机安装 Codex CLI 并完成 `codex login`。

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

脚本会自动检测插件市场/本仓库安装的 versioned `xiaohongshu-plugin` CLI；只有手动安装时才需要在 `~/social-autopilot/.env` 设置：

```bash
XHS_CLI_PATH=/absolute/path/to/xiaohongshu-skills/scripts/cli.py
```

小红书图文笔记至少需要一张图片。发布层会优先使用 `card_path`；想要更精致封面时，先运行 `generate_ai_covers.py` 或调用 `/codex-image --size 1024x1536 --quality high --out ~/social-autopilot/output/ai-covers ...` 生成素材；没有 AI 封面时才自动用新闻标题生成模板卡片。

更多细节见 `references/channels/xiaohongshu.md`。

## 日常使用流程

### 用户要“发小红书/发布 XHS/发一批热点”时

默认执行端到端小红书流程，除非用户只要求生成草稿：

1. 运行 `python scripts/run.py status.py`，检查 LLM、Codex Image、XHS CLI 和登录状态。
2. 小批量准备内容：`python scripts/run.py pipeline --channel xiaohongshu --limit 5 --ai-covers --ai-cover-limit 3 --no-publish`。
3. 如果 LLM 预检失败，先修正 `OPENAI_MODEL` / `OPENAI_BASE_URL` / `OPENAI_API_KEY`，不要继续跑全链路。
4. 如果 Codex 图片生成不可用，继续用模板卡片 fallback，但要说明封面质量降级。
5. 预览待发布内容：`python scripts/run.py publish_channels.py --channel xiaohongshu --dry-run --limit 5`，向用户展示标题、正文摘要、标签、图片路径和数量。
6. 只问一次确认：“确认发布这些小红书笔记吗？”
7. 用户确认后发布：`python scripts/run.py publish_channels.py --channel xiaohongshu --xhs-publish-mode publish --limit 5`。

如果用户明确说“直接发布/不用确认/全自动发”，可以跳过第 5-6 步，直接运行：

```bash
python scripts/run.py pipeline --channel xiaohongshu --limit 5 --ai-covers --ai-cover-limit 3 --xhs-publish-mode publish
```

### 用户只说“看看新闻/有什么热点”时

只准备和预览，不自动发布：

1. 默认小批量运行 `python scripts/run.py pipeline --channel xiaohongshu --limit 5 --ai-covers --ai-cover-limit 3 --no-publish`。
2. 向用户报告结果：抓取 X 条新闻、生成 Y 条小红书草稿、生成 Z 张 AI 封面/模板卡片。
3. 展示草稿和图片路径，等待用户选择修改、保存草稿或发布。

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

小红书默认关闭；配置启用后会生成 `platform=xiaohongshu` 的平台专属草稿。临时小红书发布任务可用 `--channel xiaohongshu` 覆盖配置，不需要先编辑 `config.json`。`publish_mode: "draft"` 只填入发布页；`publish_mode: "publish"` 会直接点击发布，只有用户明确确认后才使用。

## 内容生成职责分离

生成阶段先读取 `channels` 配置，确定目标平台，再生成内容：

1. `content_briefs`：平台无关复用层，保存新闻事实、相关性、内容角度、商品关联、视觉方向和基础标签。
2. `post_drafts`：平台专属发布队列，每个启用平台一条草稿。Meta 行保存 PT-BR 文案和 20 个 hashtag；小红书行保存中文 `platform_title`、中文正文和 3-6 个话题。

发布模块只消费对应平台的 `post_drafts`，不再临时把 Meta 文案转换成小红书文案。

## 安全规则

- **确认后再发布**: 排期或发布前先展示帖子内容、图片路径和目标渠道让用户确认。
- **小红书默认不自动发布**: 默认只调用 `fill-publish` 填表/生成待发布草稿；只有用户明确确认或配置 `publish_mode: "publish"` 时才调用 `publish` 直接发布。
- **不提交 .env**: 包含 API Key 和 Token，绝不提交到 git。
- **Token 安全**: Meta Page Token 存储在 `.env` 中，不输出到日志。
- **内容审核**: 保留人工审核环节，避免自动发布不当内容。
- **回滚**: Meta 已排期帖子可通过 Graph API 删除；小红书发布前取消时使用 `/post-to-xhs` 中的保存草稿流程。

## 参考文档

- `SETUP_GUIDE.md` — Meta API 全流程配置引导
- `references/channels/xiaohongshu.md` — 小红书渠道配置和发布约束
- `references/card-design.md` — 新闻卡片设计规范和 `/codex-image` / `/image-skill` 配合方式
- `references/troubleshooting.md` — 常见问题排查
