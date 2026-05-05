---
name: xhs-interact
description: |
  对小红书笔记进行互动：点赞/取消点赞、收藏/取消收藏、发表评论、回复评论。
  当用户想对小红书笔记进行互动时使用。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 约束

- 评论和回复执行前展示内容让用户确认（公开发表，无法撤回）
- 点赞和收藏可直接执行（操作可逆）
- 所有操作都需要 `feed_id` + `xsec_token`（来自搜索或详情结果）

## 执行流程

### 点赞

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py like-feed \
  --feed-id <feed_id> --xsec-token <xsec_token>
```

取消点赞：加 `--unlike`

### 收藏

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py favorite-feed \
  --feed-id <feed_id> --xsec-token <xsec_token>
```

取消收藏：加 `--unfavorite`

### 发表评论

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py post-comment \
  --feed-id <feed_id> --xsec-token <xsec_token> --content "评论内容"
```

发送前展示评论内容让用户确认。

### 回复评论

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py reply-comment \
  --feed-id <feed_id> --xsec-token <xsec_token> --content "回复内容" \
  --comment-id <comment_id>
```

或通过用户 ID 回复：`--user-id <user_id>`（与 `--comment-id` 二选一）

发送前展示回复内容让用户确认。

## 兜底（Chrome DevTools MCP）

CLI 失败时：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

- 导航到笔记详情页
- `take_snapshot` 找到对应按钮（点赞/收藏/评论输入框）→ `click` / `fill`
