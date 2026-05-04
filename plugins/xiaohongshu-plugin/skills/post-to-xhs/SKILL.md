---
name: post-to-xhs
argument-hint: "[标题或内容描述]"
description: |
  发布内容到小红书，支持图文笔记和视频笔记。自动判断发布类型，校验标题和素材，用户确认后发布。
  当用户想在小红书发布内容时使用——包括发笔记、发图文、发视频、上传图片、写一篇小红书、把内容发到红书上、种草笔记、好物分享等，即使用户只说"帮我发一下"但上下文明确是小红书也应触发。
---

## 输入判断

根据用户提供的素材判断发布类型：
- 提供了视频文件 → 视频笔记
- 提供了图片 → 图文笔记
- 仅提供文本 → 提示用户至少提供图片或视频

## 约束

- 标题最多 20 个中文字或英文单词（小红书平台限制，超长会被截断）
- 图文笔记至少 1 张图片（小红书不允许纯文本笔记）
- 视频笔记仅支持本地视频文件绝对路径（MCP 服务需要读取本地文件）
- 图片和视频不能混用，只能二选一（小红书平台限制）
- 正文中不要包含 # 标签（标签通过 `tags` 参数单独传递，MCP 服务会自动处理格式）
- 发布前展示完整内容让用户确认（发布后无法撤回）

## 执行流程

### 1. 收集发布信息

确保以下内容齐全：
- `title`（必填）— 标题
- `content`（必填）— 正文
- 图片列表或视频路径（必填其一）
- `tags`（可选）— 话题标签
- `schedule_at`（可选）— 定时发布，ISO8601 格式
- `is_original`（可选，仅图文）— 声明原创
- `visibility`（可选）— 公开可见 | 仅自己可见 | 仅互关好友可见

信息不完整时，向用户询问缺少的部分。

### 2. 内容校验与优化

- 检查标题长度（≤20 中文字）
- 检查图片/视频文件路径是否为绝对路径
- 如用户提供 URL 内容，先用 WebFetch 提取文本和图片
- 如用户只给出主题或草稿，先按内容质量原则补齐标题、正文和标签

参考 `{baseDir}/../references/title-guide.md` 和 `{baseDir}/../references/content-guide.md` 进行内容优化。

#### 内容质量原则

**标题策略**：
- 使用"数字 + 痛点/好处 + emoji"增强吸引力
- 可使用悬念、共鸣、价值、对比或限定人群提升点击意愿
- 避免过于平淡、空泛或与正文不符的标题

**正文结构**：
- 开头用 1-2 行抓住注意力，可选择痛点共鸣、惊喜发现或直接给出价值
- 主体分点呈现，每点包含具体说明或实际案例
- 结尾加入互动引导，但不要强行营销

**排版美学**：
- 每 1-2 句话换行，分点内容必须换行，段落间留空行
- 统一使用少量符号，如 `✨`、`📌`、`💡`、`⚠️`、`❤️`
- 不要每句话都加 emoji，不要混用过多符号

**标签策略**：
- 使用 3-6 个标签，通过 `tags` 参数单独传递
- 组合热门话题、精准定位和长尾标签
- 标签必须与内容强相关，避免堆砌无关大词

### 3. 封面图（图文笔记）

如果用户没有提供封面图，引导使用 `/xhs-cover` 生成封面图：
- 有封面图 → 使用封面图上传模式（Mode A）
- 无封面图 → 使用文字配图模式（Mode B，平台自动生成图片）

### 4. 确认发布

向用户展示完整的发布内容预览：
- 标题、正文、标签
- 图片列表/封面图/视频路径
- 定时时间、可见范围（如有）

等待用户确认后才执行发布。

### 5. 执行发布（双引擎）

**方式一：MCP 工具（优先）**

图文笔记 — 调用 `publish_content`：
- `title`（string，必填）
- `content`（string，必填）
- `images`（string[]，必填）— 图片路径或 URL
- `tags`（string[]，可选）
- `schedule_at`（string，可选）
- `is_original`（bool，可选）
- `visibility`（string，可选）

视频笔记 — 调用 `publish_with_video`：
- `title`（string，必填）
- `content`（string，必填）
- `video`（string，必填）— 本地视频绝对路径
- `tags`（string[]，可选）
- `schedule_at`（string，可选）
- `visibility`（string，可选）

**MCP 工具失败判断**：
- 返回错误信息
- 调用超时（>60 秒无响应）
- 返回成功但无法验证

**方式二：Chrome DevTools MCP（MCP 失败时自动切换）**

当 MCP 工具失败/超时时，切换到浏览器直接操作：

1. 确保 Chrome 调试模式：
   ```bash
   bash {baseDir}/../scripts/ensure-chrome-debug.sh
   ```

2. 导航到创作中心：
   ```
   navigate_page → url: https://creator.xiaohongshu.com/publish/publish
   ```

3. 参考 `{baseDir}/../references/workflow.md` 执行发布 SOP：

   **Mode A：自定义封面图上传**
   - `take_snapshot` 找到"上传图文"按钮 → `click`
   - `upload_file` 上传封面图
   - 等待处理 → `take_snapshot` 找到"下一步" → `click`
   - 用 `evaluate_script` 填写标题（nativeInputValueSetter 模式）
   - `take_snapshot` 找到"发布"按钮 → `click`

   **Mode B：文字配图发布**
   - `take_snapshot` 找到"上传图文" → `click`
   - `take_snapshot` 找到"文字配图" → `click`
   - 用 `evaluate_script` 通过 ClipboardEvent 粘贴内容到 `.tiptap.ProseMirror` 编辑器
   - 点击"生成图片" → 等待预览
   - "下一步" → 填写标题 → 发布

4. 验证发布成功：**URL 包含 `published=true`**（小红书不显示"发布成功"文字）

5. 每步操作后用 `take_screenshot` 或 `take_snapshot` 确认状态

#### 关键技术模式

**标题填写（React 应用）**：
```javascript
const input = document.querySelector('input[placeholder*="标题"]');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '标题文字');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

**正文粘贴（tiptap 编辑器）**：
```javascript
const editor = document.querySelector('.tiptap.ProseMirror');
const dt = new DataTransfer();
dt.setData('text/html', '<p>正文内容</p>');
dt.setData('text/plain', '正文内容');
const evt = new ClipboardEvent('paste', {
  bubbles: true, cancelable: true, clipboardData: dt
});
editor.dispatchEvent(evt);
```

### 6. 报告结果

发布成功后，告知用户笔记 ID 和发布状态。

## 失败处理

| 场景 | 处理 |
|---|---|
| 未登录 | 引导使用 xhs-login |
| 标题超长 | 提示用户缩短标题 |
| 图片路径无效 | 提示检查路径是否正确 |
| 视频使用了相对路径 | 提示改为绝对路径 |
| 内容质量不足 | 先优化标题、正文、排版和标签，再请求用户确认 |
| MCP 工具失败/超时 | 自动切换到 Chrome DevTools MCP 路径 |
| Chrome DevTools 操作失败 | `take_snapshot` 查看页面结构重试 |
| 页面加载超时 | 等 5-10 秒后 `take_screenshot` 确认 |
| 登录过期 | 检测到登录页时提示重新登录 |

## 参考资料

- 发布 SOP 工作流：`{baseDir}/../references/workflow.md`
- 页面结构参考：`{baseDir}/../references/web-structure.md`
- 标题创作规范：`{baseDir}/../references/title-guide.md`
- 正文创作规范：`{baseDir}/../references/content-guide.md`
- 封面图生成：`{baseDir}/xhs-cover/SKILL.md`
