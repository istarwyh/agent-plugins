---
name: xhs-explore
description: |
  浏览小红书推荐流、查看笔记详情和评论。
  当用户想看推荐内容、刷首页、查看某条笔记的详情/评论、或已有 feed_id 想获取完整内容时使用。
---

## 输入判断

- 用户想浏览推荐 → 步骤 1
- 用户提供了 feed_id → 步骤 2

## 执行流程

### 1. 获取推荐流

**方式一：MCP 工具**

调用 `list_feeds`（无参数），返回首页推荐笔记列表。

**方式二：Chrome DevTools MCP（MCP 工具失败/超时/返回空时）**

```bash
bash {baseDir}/../scripts/ensure-chrome-debug.sh
```

- `navigate_page` → `https://www.xiaohongshu.com/explore`
- `take_snapshot` → 获取首页 Feed 卡片列表
- 提取每条笔记的标题、作者、链接

展示每条笔记的标题、作者、互动数据，附带 `feed_id` 和 `xsec_token`。

### 2. 查看笔记详情

**方式一：MCP 工具**

调用 `get_feed_detail`：
- `feed_id`（string，必填）
- `xsec_token`（string，必填）
- `load_all_comments`（bool，可选，默认 false，仅返回前 10 条评论）
- `limit`（int，可选，load_all_comments=true 时生效，默认 20）
- `click_more_replies`（bool，可选，是否展开二级回复）
- `reply_limit`（int，可选，跳过回复数超过此值的评论，默认 10）
- `scroll_speed`（string，可选：slow | normal | fast）

**方式二：Chrome DevTools MCP（MCP 工具失败时）**

- `navigate_page` → 笔记详情 URL
- `take_snapshot` → 提取标题、正文、图片、互动数据
- 滚动加载评论 → `take_snapshot` 获取评论列表

展示：笔记内容、图片、作者信息、互动数据、评论列表。

提示用户可以：
- 点赞/收藏（使用 xhs-interact）
- 发表评论（使用 xhs-interact）
- 查看作者主页（使用 xhs-profile）

## 失败处理

| 场景 | 处理 |
|---|---|
| 未登录 | 引导使用 xhs-login |
| 笔记已删除或不可见 | 告知用户该笔记无法访问 |
| MCP 工具失败/超时 | 自动切换到 Chrome DevTools MCP 路径 |
| Chrome DevTools 操作失败 | `take_snapshot` 查看页面结构重试 |
