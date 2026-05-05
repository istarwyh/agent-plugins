---
name: post-to-xhs
argument-hint: "[标题或内容描述]"
description: |
  发布内容到小红书，支持图文笔记、视频笔记和长文。自动判断发布类型，校验标题和素材，用户确认后发布。
  当用户想在小红书发布内容时使用——包括发笔记、发图文、发视频、写一篇小红书、种草笔记、好物分享等。
---

CLI 路径：`python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py`

## 输入判断

- 提供了视频文件 → 视频笔记（`fill-publish-video`）
- 提供了图片 → 图文笔记（`fill-publish`）
- 长文内容（>500 字或用户要求） → 长文发布（`long-article`）
- 仅提供文本 → 提示用户至少提供图片或视频

## 约束

- 标题最多 20 个中文字（UTF-16 计算：汉字/全角=1，ASCII 每 2 个=1）
- 图文笔记至少 1 张图片
- 图片和视频不能混用
- 正文段落使用双换行分隔
- 话题标签格式：`#标签1 #标签2`（CLI 会自动从正文末尾提取）
- 发布前展示完整内容让用户确认（发布后无法撤回）

## 执行流程

### 1. 收集发布信息

确保以下内容齐全：
- `title`（必填）— 标题（≤20 字）
- `content`（必填）— 正文
- 图片列表或视频路径（必填其一）
- `tags`（可选）— 话题标签
- `schedule_at`（可选）— 定时发布，ISO8601 格式
- `is_original`（可选）— 声明原创
- `visibility`（可选）— 公开可见 | 仅自己可见 | 仅互关好友可见

### 2. 内容校验与优化

- 检查标题长度（≤20 中文字）
- 检查图片/视频文件路径是否为绝对路径
- 如用户提供 URL 内容，先用 WebFetch 提取文本和图片
- 如用户只给出主题或草稿，先按内容质量原则补齐

参考 `{baseDir}/../../references/title-guide.md` 和 `{baseDir}/../../references/content-guide.md` 进行内容优化。

#### 内容质量原则

**标题策略**：数字 + 痛点/好处 + emoji，避免平淡、空泛

**正文结构**：开头抓注意力 → 主体分点 → 结尾互动引导

**排版美学**：每 1-2 句换行，段落间留空行，统一少量符号（✨📌💡⚠️❤️）

**标签策略**：3-6 个标签，组合热门话题 + 精准定位 + 长尾标签

### 3. 封面图（图文笔记）

如果用户没有提供封面图，引导使用 `/xhs-cover` 生成封面图。

### 4. 确认发布

向用户展示完整的发布内容预览：标题、正文、标签、图片/视频路径、定时时间、可见范围。

等待用户确认后才执行发布。

### 5. 执行发布

#### 图文笔记（分步发布，推荐）

```bash
# 1. 写入临时文件
echo "标题文字" > /tmp/xhs_title.txt
echo "正文内容" > /tmp/xhs_content.txt

# 2. 填表（不发布）
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py fill-publish \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --images /path/to/img1.jpg /path/to/img2.jpg \
  --tags "标签1" "标签2" \
  --visibility "公开可见"

# 3. 用户确认后发布
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py click-publish
```

用户取消时：
```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py save-draft
```

#### 视频笔记

```bash
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py fill-publish-video \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt \
  --video /path/to/video.mp4

python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py click-publish
```

#### 长文发布

```bash
# 1. 填写长文内容
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py long-article \
  --title-file /tmp/xhs_title.txt \
  --content-file /tmp/xhs_content.txt

# 2. 选择模板
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py select-template --name "模板名"

# 3. 下一步（填写描述）
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py next-step \
  --content-file /tmp/xhs_description.txt

# 4. 发布
python3 {baseDir}/../../xiaohongshu-skills/scripts/cli.py click-publish
```

### 6. 报告结果

发布成功后，告知用户发布状态。

## 失败处理

| 场景 | 处理 |
|---|---|
| 未登录 | 引导使用 xhs-login |
| 标题超长 | 提示用户缩短标题 |
| 图片路径无效 | 提示检查路径是否为绝对路径 |
| CLI 失败（Extension 未连接） | 自动切换到 Chrome DevTools MCP 兜底 |
| CLI 超时 | 重试一次，仍失败则切换兜底 |

## 兜底（Chrome DevTools MCP）

CLI 失败时，按 `{baseDir}/../../references/workflow.md` 的 SOP 执行：

```bash
bash {baseDir}/../../scripts/ensure-chrome-debug.sh
```

关键技术模式见 `{baseDir}/../../references/workflow.md`（nativeInputValueSetter、ClipboardEvent、published=true 判断）。

## 参考资料

- 发布 SOP：`{baseDir}/../../references/workflow.md`
- 页面结构：`{baseDir}/../../references/web-structure.md`
- 标题规范：`{baseDir}/../../references/title-guide.md`
- 正文规范：`{baseDir}/../../references/content-guide.md`
- 封面图生成：`{baseDir}/../xhs-cover/SKILL.md`
