---
name: xhs-explore
description: |
  浏览小红书推荐流、查看笔记详情和评论。
  当用户想看推荐内容、刷首页、查看某条笔记的详情/评论、或已有 feed_id 想获取完整内容时使用。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 输入判断

- 用户想浏览推荐 → 步骤 1
- 用户提供了 feed_id → 步骤 2

## 执行流程

### 1. 获取推荐流

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py list-feeds
```

返回 JSON 中 `feeds` 数组。展示每条笔记的标题、作者、互动数据，附带 `feed_id` 和 `xsec_token`。

### 2. 查看笔记详情

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py get-feed-detail \
  --feed-id <feed_id> \
  --xsec-token <xsec_token> \
  --load-all-comments \
  --max-comment-items 50
```

可选参数：
- `--load-all-comments` — 加载全部评论（默认仅前 10 条）
- `--click-more-replies` — 展开子评论
- `--max-replies-threshold 10` — 跳过回复数超过此值的评论
- `--max-comment-items 50` — 限制评论数量
- `--scroll-speed normal` — 滚动速度：slow | normal | fast

展示：笔记内容、图片、作者信息、互动数据、评论列表。

提示用户可以点赞/收藏/评论（`/xhs-interact`）或查看作者主页（`/xhs-profile`）。

## 兜底（Chrome DevTools MCP）

CLI 失败时：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

- `navigate_page` → `https://www.xiaohongshu.com/explore`
- `take_snapshot` → 获取首页 Feed 卡片列表
- 点击笔记 → `take_snapshot` → 提取详情内容
