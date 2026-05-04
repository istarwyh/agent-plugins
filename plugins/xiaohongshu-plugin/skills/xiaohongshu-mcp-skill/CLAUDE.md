# CLAUDE.md

Skills 层不包含业务实现代码，所有功能通过调用 xiaohongshu-mcp 的 MCP 工具完成。MCP 工具失败时，降级到 Chrome DevTools MCP 直接操作浏览器。

## MCP 工具映射表

| MCP 工具 | 类型 | 对应 Skill | Fallback | 说明 |
|---|---|---|---|---|
| `check_login_status` | ReadOnly | xhs-login | Chrome DevTools | 检查登录状态 |
| `get_login_qrcode` | ReadOnly | xhs-login | Chrome DevTools | 获取登录二维码 |
| `delete_cookies` | Destructive | xhs-login | — | 删除 cookies 重置登录 |
| `publish_content` | Destructive | post-to-xhs | **Chrome DevTools** | 发布图文笔记 |
| `publish_with_video` | Destructive | post-to-xhs | **Chrome DevTools** | 发布视频笔记 |
| `list_feeds` | ReadOnly | xhs-explore | **Chrome DevTools** | 获取推荐流 |
| `search_feeds` | ReadOnly | xhs-search | — | 搜索笔记 |
| `get_feed_detail` | ReadOnly | xhs-explore | Chrome DevTools | 获取笔记详情和评论 |
| `user_profile` | ReadOnly | xhs-profile | — | 获取用户主页 |
| `like_feed` | Destructive | xhs-interact | Chrome DevTools | 点赞/取消点赞 |
| `favorite_feed` | Destructive | xhs-interact | Chrome DevTools | 收藏/取消收藏 |
| `post_comment_to_feed` | Destructive | xhs-interact | Chrome DevTools | 发表评论 |
| `reply_comment_in_feed` | Destructive | xhs-interact | Chrome DevTools | 回复评论 |

## Chrome DevTools MCP 工具

当 MCP 工具不可用或调用失败时，使用 Chrome DevTools MCP 工具直接操作浏览器：

| Chrome DevTools 工具 | 用途 |
|---|---|
| `navigate_page` | 导航到指定 URL |
| `take_snapshot` | 获取页面无障碍树（元素 + UID） |
| `take_screenshot` | 截图确认页面状态 |
| `click` | 点击元素 |
| `fill` | 填写表单 |
| `upload_file` | 上传文件 |
| `evaluate_script` | 执行 JavaScript（用于 nativeInputValueSetter、ClipboardEvent 等） |
| `press_key` | 按键操作 |
| `wait_for` | 等待页面元素出现 |

## 关键技术模式

### nativeInputValueSetter（React 输入框）

小红书使用 React，直接设置 `.value` 不触发状态更新：

```javascript
const input = document.querySelector('input[placeholder*="标题"]');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '标题文字');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

### ClipboardEvent（tiptap 编辑器）

`.tiptap.ProseMirror` 编辑器必须通过剪贴板粘贴：

```javascript
const editor = document.querySelector('.tiptap.ProseMirror');
const dt = new DataTransfer();
dt.setData('text/html', '<p>内容</p>');
dt.setData('text/plain', '内容');
const evt = new ClipboardEvent('paste', {
  bubbles: true, cancelable: true, clipboardData: dt
});
editor.dispatchEvent(evt);
```

### 发布成功判断

小红书不显示"发布成功"文字。判断标准：**URL 包含 `published=true`**。

## Fallback 触发条件

- MCP 工具返回错误
- MCP 工具调用超时（>60 秒）
- MCP 工具返回空结果（如 `list_feeds` 返回空但页面有内容）

触发后自动切换到 Chrome DevTools MCP，参考 `{baseDir}/../references/workflow.md` 和 `{baseDir}/../references/web-structure.md` 执行操作。

## SKILL.md 编写规范

每个 SKILL.md 包含 YAML frontmatter（name + description）和 Markdown 正文。

正文必须包含：输入判断、约束条件、执行流程（含 MCP 工具调用 + Fallback）、失败处理。

编写原则：
- 控制在 200 行以内
- Destructive 操作需用户确认
- 工具名和参数必须与 xiaohongshu-mcp 源码一致
- 需要写操作的 skill 必须包含 Chrome DevTools fallback 路径

## 参考资源

- **xiaohongshu-mcp 源码**：`~/src/zy/xiaohongshu-mcp`（Go MCP 服务）
- **发布 SOP 工作流**：`{baseDir}/../references/workflow.md`
- **页面结构参考**：`{baseDir}/../references/web-structure.md`
- **标题创作规范**：`{baseDir}/../references/title-guide.md`
- **正文创作规范**：`{baseDir}/../references/content-guide.md`
- **封面设计规范**：`{baseDir}/../references/cover-guide.md`
