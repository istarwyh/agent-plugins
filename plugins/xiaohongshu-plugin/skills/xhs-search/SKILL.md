---
name: xhs-search
argument-hint: "[搜索关键词]"
description: |
  搜索小红书笔记，支持关键词搜索和多维度筛选。
  当用户想在小红书上搜索、查找内容时使用。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 执行流程

### 1. 确认搜索条件

- `keyword`（必填）— 搜索关键词
- `sort_by`（可选）— 综合 | 最新 | 最多点赞 | 最多评论 | 最多收藏
- `note_type`（可选）— 不限 | 视频 | 图文
- `publish_time`（可选）— 不限 | 一天内 | 一周内 | 半年内
- `search_scope`（可选）— 不限 | 已看过 | 未看过 | 已关注
- `location`（可选）— 不限 | 同城 | 附近

### 2. 执行搜索

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py search-feeds \
  --keyword "关键词" \
  --sort-by "最多点赞" \
  --note-type "图文" \
  --publish-time "一周内"
```

### 3. 展示结果

返回 JSON 中 `feeds` 数组，每条包含标题、作者、互动数据、`feed_id` 和 `xsec_token`。

整理为列表展示，提示用户可查看详情（`/xhs-explore`）或互动（`/xhs-interact`）。

## 兜底（Chrome DevTools MCP）

CLI 失败时：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

- `navigate_page` → `https://www.xiaohongshu.com/explore`
- `take_snapshot` → 找到搜索框 → `fill` 关键词 → `press_key Enter`
- `take_snapshot` → 获取搜索结果
