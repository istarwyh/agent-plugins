---
name: xhs-profile
description: |
  查看小红书用户主页：基本信息、粉丝/关注/获赞数据、发布的笔记列表。
  当用户想查看某个博主、作者、用户的主页信息和作品时使用。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 执行流程

### 1. 获取用户信息

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py user-profile \
  --user-id <user_id> \
  --xsec-token <xsec_token>
```

`user_id` 和 `xsec_token` 从搜索或笔记详情结果中获取。

### 2. 展示结果

- 基本信息：昵称、头像、简介、性别、地区
- 数据：粉丝数、关注数、获赞与收藏数
- 最近发布的笔记列表

## 兜底（Chrome DevTools MCP）

CLI 失败时：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

- `navigate_page` → 用户主页 URL
- `take_snapshot` → 提取用户信息和笔记列表
