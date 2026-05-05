---
name: xhs-content-plan
description: |
  小红书内容策划助手：搜索分析热门内容和竞品，帮助规划内容方向、选题、标签策略。
  当用户想做小红书运营规划时使用——内容策划、选题灵感、竞品分析、爆款分析、热门话题研究、涨粉策略等。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 执行流程

### 1. 明确策划需求

向用户了解：目标领域/赛道、策划目的（选题灵感/竞品分析/热门趋势）、目标人群、内容风格。

### 2. 搜索分析

```bash
# 多关键词搜索覆盖领域
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py search-feeds \
  --keyword "关键词" --sort-by "最多点赞"

python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py search-feeds \
  --keyword "关键词" --sort-by "最新"
```

对高互动笔记获取详情：

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py get-feed-detail \
  --feed-id xxx --xsec-token yyy
```

分析：标题写法、内容结构、话题标签、评论区用户关注点。

如需分析特定博主：

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py user-profile \
  --user-id xxx --xsec-token yyy
```

### 3. 输出策划建议

整理分析结果，为用户提供：热门选题方向、标题参考模板、推荐话题标签、内容结构建议。

## 内容策划原则

**平台偏好**：真实、接地气、视觉美观、排版清晰的实用内容

**标题方向**：数字 + 痛点/好处 + emoji，结合"新手必看""建议收藏""避坑"等价值点

**结构建议**：开头痛点共鸣 → 主体 3-5 分点 → 结尾总结+互动引导

**标签组合**：热门话题 1-2 个 + 精准定位 2-3 个 + 长尾标签 1-2 个

**运营节奏**：新手每周 2-3 篇，进阶每周 3-5 篇，高峰时段 7-9/12-14/18-22 点

**禁忌事项**：不做硬广、不抄袭、不堆砌无关标签、不输出排版混乱的方案

## 参考资料

- 标题规范：`{baseDir}/../../references/title-guide.md`
- 正文规范：`{baseDir}/../../references/content-guide.md`
- 封面设计：`{baseDir}/../../references/cover-guide.md`

## 约束

- 这是只读分析 skill，不执行发布或互动操作
- 搜索操作需要已登录状态
