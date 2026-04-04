---
name: social-autopilot
description: >
  当用户要求监控极客新闻(漫威/DC/星战/F1/游戏)、生成社交媒体帖子、
  配置Instagram或Facebook自动发布、或提到热点资讯自动化时触发。
  也在用户输入 /social-autopilot 时触发。
---

# 极客电商社媒自动化

监控热点新闻 → LLM生成帖子 → 新闻卡片图片 → Meta排期发布。
所有命令通过 `python scripts/run.py <脚本> [参数...]` 从 skill 根目录执行。

## 前置条件

1. Python >= 3.11
2. 安装依赖: `python -m pip install -r requirements.txt`
3. 安装 Playwright 浏览器: `python -m playwright install chromium`
4. 复制 `.env.example` 到 `~/social-autopilot/.env` 并填入凭证
5. 如任何必要环境变量缺失，提示用户填写后再继续

## 命令

| 操作 | 命令 |
|------|------|
| 首次配置 | `python scripts/run.py setup.py` |
| 抓取新闻 | `python scripts/run.py poll_news.py --priority high` |
| 生成帖子 | `python scripts/run.py generate_posts.py` |
| 生成卡片图 | `python scripts/run.py generate_card.py --title "标题" --category marvel` |
| Meta排期 | `python scripts/run.py schedule_meta.py --mode facebook_only` |
| 全链路运行 | `python scripts/run.py pipeline` |
| 安装定时任务 | `python scripts/run.py install_cron.py` |
| 状态检查 | `python scripts/run.py status.py` |
| 试运行 | 任意命令加 `--dry-run`（只打印不执行） |

## 首次配置流程

当用户首次使用此skill时，按以下步骤引导：

1. **运行 setup.py**: 自动创建 `~/social-autopilot/` 目录结构和配置文件
2. **配置 LLM API Key**: 用户已在使用 Claude Code，引导填入 ANTHROPIC_API_KEY
3. **配置 Meta API**（可选）: 参考 SETUP_GUIDE.md 引导用户完成 Meta App 创建和 Token 获取
4. **试运行验证**: `python scripts/run.py pipeline --dry-run`
5. **安装定时任务**: `python scripts/run.py install_cron.py`

如果用户尚未配置 Meta API，全链路终点为生成草稿（JSON + 卡片图），用户可手动发布。

## 日常使用流程

用户输入 `/social-autopilot` 或 "帮我看看有什么新闻" 时：

1. 运行 `python scripts/run.py pipeline`
2. 向用户报告结果：抓取X条新闻、生成Y条帖子、Z条已排期
3. 展示生成的帖子草稿供用户预览
4. 如用户要求修改，直接编辑 `~/social-autopilot/output/drafts/` 中的JSON

## 安全规则

- **确认后再发布**: 排期到Meta前先展示帖子内容让用户确认
- **不提交 .env**: 包含 API Key，绝不提交到 git
- **Token 安全**: Meta Page Token 存储在 .env 中，不输出到日志
- **内容审核**: 建议保留人工审核环节，避免自动发布不当内容
- **回滚**: 可通过 Graph API 删除已排期帖子

## 参考文档

- `SETUP_GUIDE.md` — Meta API 全流程配置引导
- `references/card-design.md` — 新闻卡片设计规范
- `references/troubleshooting.md` — 常见问题排查
