# 常见问题排查

## 安装与配置

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `ModuleNotFoundError: No module named 'feedparser'` | 依赖未安装 | `python -m pip install -r requirements.txt` |
| `playwright._impl._errors.Error: Executable doesn't exist` | Playwright浏览器未安装 | `python -m playwright install chromium` |
| `RuntimeError: 缺少环境变量: OPENAI_API_KEY` | .env 未配置 | 编辑 `~/social-autopilot/.env` 填入 OpenAI-compatible API Key |
| `FileNotFoundError: config.json` | 首次运行未初始化 | 运行 `python scripts/run.py setup.py` |

## RSS 抓取

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| "抓取完成: 0 条匹配" | 关键词过滤太严格 | 检查 config.json 中 keywords_whitelist |
| "请求失败: 403 Forbidden" | Google News 限流 | 等待几分钟后重试；减少请求频率 |
| "RSS解析异常" | Feed 格式变化 | 检查 URL 是否仍有效；更新 RSS URL |
| 所有新闻都被去重 | 之前已处理过 | 正常情况；检查 `data/news.db` |

## LLM 帖子生成

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| "LLM调用错误: 401" | API Key 无效 | 检查 OPENAI_API_KEY 是否正确 |
| "LLM调用错误: 429" | 配额用尽 | 等待配额重置或升级计划 |
| "JSON解析失败" | LLM 返回非JSON | 自动重试3次；通常第2次成功 |
| "相关性不足" | 新闻与电商无关 | 正常过滤；可降低 MIN_RELEVANCE_SCORE |

## 卡片图片生成

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| "Playwright 未安装" | 缺少 playwright 包 | `pip install playwright && python -m playwright install chromium` |
| 卡片文字显示异常 | Google Fonts 加载失败 | 检查网络连接；Playwright 需要联网加载字体 |
| 图片全黑或空白 | HTML 模板问题 | 检查 templates/news_card.html 是否完整 |
| `/codex-image` 不可用 | 未安装 openai-plugin | 按根 README 运行 `npx skills add istarwyh/agent-plugins`，或安装 `openai-plugin@agent-plugins` |
| `Codex CLI 未安装` | 未安装 Codex CLI | 运行 `npm install -g @openai/codex`，然后 `codex login` |
| `Codex 未登录` | Codex OAuth 未登录或过期 | 运行 `codex login` 后重试 `generate_ai_covers.py` |
| `/image-skill` 不可用 | OpenAI-compatible 图片备选未安装 | 按根 README 安装 `openai-plugin@agent-plugins` |

## Meta 排期

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| "META_PAGE_ACCESS_TOKEN 未配置" | 未完成Meta配置 | 参考 SETUP_GUIDE.md |
| "Token状态: 无效" | Token 已过期 | 重新获取 Page Token（参考 SETUP_GUIDE.md 第3~5步） |
| "Facebook排期失败: 403" | 权限不足 | 检查 Token 是否有 pages_manage_posts 权限 |
| "容器处理失败" | Instagram 图片URL无法访问 | 确保图片URL是公开可访问的 |

## 小红书渠道

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| "小红书渠道未检测到 xiaohongshu-plugin" | 未安装小红书插件 | 按根 README 运行 `npx skills add istarwyh/agent-plugins`，或安装 `xiaohongshu-plugin@agent-plugins` |
| "小红书未登录" | 浏览器会话未登录 | 运行 `/xhs-login` |
| "小红书环境检查失败" | Chrome Bridge 或扩展异常 | 运行 `/setup-xhs` |
| "缺少可用图片" | 小红书图文至少需要 1 张图片 | 优先运行 `generate_ai_covers.py` 或 `/codex-image` 生成封面；失败时模板卡片会 fallback |
| 发布超时或结果不确定 | 小红书页面可能已提交但 CLI 未返回 | 先查 `xiaohongshu-plugin/references/publish-troubleshooting.md`，确认个人主页没有笔记后再重试 |

## 定时任务

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Cron 任务不执行 | Python 路径错误 | 运行 `which python` 确认路径；重新安装 cron |
| 日志文件不更新 | 日志目录不存在 | 运行 `python scripts/run.py setup.py` |
| 重复执行 | 安装了多份 cron | `crontab -l` 检查，`install_cron.py --remove` 清理 |

## 数据维护

**清理旧数据**（超过90天的已处理新闻）:
```sql
sqlite3 ~/social-autopilot/data/news.db \
  "DELETE FROM processed_news WHERE processed_at < datetime('now', '-90 days')"
```

**重置数据库**:
```bash
rm ~/social-autopilot/data/news.db
python scripts/run.py pipeline --dry-run  # 自动重建
```
