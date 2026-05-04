# 小红书发布工作流 SOP

基于 Chrome DevTools MCP 的可靠发布流程，支持两种模式。

## 前置条件

1. Chrome 浏览器已安装
2. Chrome DevTools MCP 已连接（端口 9222）
3. 小红书账号已登录

## Mode A：自定义封面图上传

适用场景：已通过 cover.sh 或 AI 生成封面图。

### 步骤

1. **启动 Chrome 调试模式**
```bash
bash {baseDir}/scripts/ensure-chrome-debug.sh
```

2. **导航到创作中心**
```
navigate_page → url: https://creator.xiaohongshu.com/publish/publish
```

3. **点击"上传图文"**
```
take_snapshot → 找到"上传图文"元素 → click
```

4. **上传封面图**
```
take_snapshot → 找到 input[type="file"] 或上传区域 → upload_file(filePath: "/tmp/xhs_cover.png")
```

5. **等待图片处理完成**
```
wait_for → text: ["下一步"]
take_screenshot → 确认图片已显示
```

6. **点击"下一步"**
```
take_snapshot → 找到"下一步"按钮 → click
```

7. **填写标题**（nativeInputValueSetter 模式）
```javascript
// evaluate_script
(titleText) => {
  const titleInput = document.querySelector('input[placeholder*="标题"]') ||
                     document.querySelectorAll('input[type="text"]')[0];
  if (!titleInput) return { success: false };
  titleInput.focus();
  const setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  setter.call(titleInput, titleText);
  titleInput.dispatchEvent(new Event('input', { bubbles: true }));
  titleInput.dispatchEvent(new Event('change', { bubbles: true }));
  return { success: true, value: titleInput.value };
}
```
验证：字数计数器显示正确数字（非 0/20）。

8. **填写正文**（如有额外描述）
```
take_snapshot → 找到正文输入区域 → fill 或 type_text
```

9. **发布**
```
take_snapshot → 找到"发布"按钮 → click
```

10. **验证成功**
```javascript
// evaluate_script
() => {
  const url = window.location.href;
  return {
    // URL 会跳转到 publish/success 路径（不是 published=true）
    published: url.includes('/success') || url.includes('published=true'),
    currentUrl: url
  };
}
```
预期：URL 跳转到 `https://creator.xiaohongshu.com/publish/success?...`，页面显示"发布成功"和笔记预览。

## Mode B：文字配图发布（平台生成图片）

适用场景：无自定义封面，使用平台内置文字配图功能。

### 步骤

1. **启动 Chrome 调试模式**
```bash
bash {baseDir}/scripts/ensure-chrome-debug.sh
```

2. **导航到创作中心**
```
navigate_page → url: https://creator.xiaohongshu.com/publish/publish
```

3. **点击"上传图文"**
```
take_snapshot → 找到"上传图文"元素 → click
```

4. **激活文字配图**
```
take_snapshot → 找到"文字配图"元素 → click
```
预期：出现 `.tiptap.ProseMirror` 编辑器。

5. **填充内容**（ClipboardEvent 模式）

单张卡片（≤200 字）：
```javascript
// evaluate_script
(content) => {
  const editor = document.querySelector('.tiptap.ProseMirror');
  if (!editor) return { success: false };
  editor.focus();
  document.execCommand('selectAll');
  document.execCommand('delete');
  const lines = content.split('\n');
  const html = lines.map(l => `<p>${l || '<br>'}</p>`).join('');
  const dt = new DataTransfer();
  dt.setData('text/html', html);
  dt.setData('text/plain', content);
  editor.dispatchEvent(new ClipboardEvent('paste', {
    bubbles: true, cancelable: true, clipboardData: dt
  }));
  return { success: true, length: content.length };
}
```

多张卡片（>200 字）：按逻辑分段，每张 ≤200 字。填完一张后点击"再写一张"添加下一张。

**为什么用 ClipboardEvent？**
tiptap (ProseMirror) 通过内部事务管理文档状态。直接修改 innerHTML 绕过状态管理，导致生成图片时换行丢失。ClipboardEvent 触发原生粘贴处理器，正确解析 `<p>` 标签为独立段落。

6. **生成图片**
```javascript
// evaluate_script
() => {
  const btn = Array.from(document.querySelectorAll('*'))
    .find(el => el.textContent?.trim() === '生成图片');
  if (btn) {
    let target = btn;
    while (target.children.length === 1) target = target.children[0];
    target.click();
    return { clicked: true };
  }
}
```

7. **进入发布编辑页**
```
take_screenshot → 确认图片预览
take_snapshot → 找到"下一步"按钮 → click
```

8. **填写标题**（同 Mode A 步骤 7）

9. **发布**（同 Mode A 步骤 9）

10. **验证成功**（同 Mode A 步骤 10）

## 关键技术模式

### nativeInputValueSetter（React 输入框）

小红书使用 React，直接设置 `.value` 不触发状态更新。必须：
```javascript
const setter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
setter.call(input, value);
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

**注意**：通过 `Runtime.evaluate` 传入箭头函数时，返回值会被包装在 `result.result.value` 中。如果函数返回对象，需要用 `arguments` 参数传递外部变量，避免闭包问题。

### ClipboardEvent（tiptap 编辑器）

tiptap 编辑器内容必须通过剪贴板粘贴：
```javascript
const dt = new DataTransfer();
dt.setData('text/html', htmlContent);
dt.setData('text/plain', plainText);
editor.dispatchEvent(new ClipboardEvent('paste', {
  bubbles: true, cancelable: true, clipboardData: dt
}));
```

### React 按钮点击（发布按钮等）

小红书的按钮使用 React 合成事件系统。普通 `element.click()` 或 `Input.dispatchMouseEvent` 有时无法触发 React 事件处理器。可靠方式是通过 React Fiber 树直接调用 onClick：

```javascript
(function() {
    var buttons = document.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].textContent.trim() === '发布' && buttons[i].className.includes('bg-red')) {
            var btn = buttons[i];
            // 方式1：直接 click（大部分情况有效）
            btn.click();
            return 'Clicked';
        }
    }
})();
```

如果 `click()` 不生效，尝试通过 Fiber 树调用：
```javascript
var fiberKey = Object.keys(btn).find(key =>
    key.startsWith('__reactFiber$') || key.startsWith('__reactInternalInstance$')
);
if (fiberKey) {
    var fiber = btn[fiberKey];
    while (fiber) {
        if (fiber.memoizedProps && fiber.memoizedProps.onClick) {
            fiber.memoizedProps.onClick();
            return 'Called React onClick';
        }
        fiber = fiber.return;
    }
}
```

### CDP 文件上传（不依赖 MCP 工具）

当 Chrome DevTools MCP 不可用时，可直接通过 CDP websocket 上传文件：

```javascript
// 1. 获取 file input 的 objectId
var result = await evaluate("document.querySelector('input[type=\"file\"][accept*=\".jpg\"]')");
var objectId = result.result.result.objectId;

// 2. 设置文件
send("DOM.setFileInputFiles", { objectId, files: ["/tmp/xhs_cover.png"] });
```

### Shadow DOM 元素操作

小红书的部分 UI（如协议勾选框）在 Shadow DOM 中，`document.querySelectorAll` 无法访问。解决方案：

1. 遍历所有元素检查 `shadowRoot`：`element.shadowRoot.querySelectorAll(...)`
2. 如果 Shadow DOM 也找不到，使用坐标点击：`Input.dispatchMouseEvent` 在截图中观察到的位置点击

### Chrome DevTools MCP 连接问题

当 Chrome 使用自定义 `--user-data-dir` 启动时（如 `ensure-chrome-debug.sh` 创建的 symlinked profile），MCP 工具在默认路径找不到 `DevToolsActivePort` 文件。

**解决方案**：
```bash
# 将 DevToolsActivePort 写入默认 Chrome 配置目录
echo "9222" > "$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort"
echo "ws://127.0.0.1:9222/devtools/browser/xxx" >> "$HOME/Library/Application Support/Google/Chrome/DevToolsActivePort"
```

**或直接使用 CDP websocket**：`ws://127.0.0.1:9222` 不依赖 MCP 工具。

## 内容质量检查（发布前）

```javascript
// evaluate_script
() => {
  const editor = document.querySelector('.tiptap.ProseMirror');
  const content = editor ? editor.textContent : '';
  return {
    length: content.length,
    hasEmoji: /[\u{1F300}-\u{1F9FF}]/u.test(content),
    hasHashtag: content.includes('#'),
    lineBreaks: (content.match(/\n/g) || []).length,
    ok: content.length > 0 && content.length <= 500
  };
}
```

## 错误处理

| 问题 | 解决 |
|------|------|
| 页面加载超时 | 等 5-10 秒后 `take_screenshot` 确认 |
| 元素未找到 | `take_snapshot` 查看页面结构 |
| 内容超 500 字 | 拆分多张卡片 |
| 标题超 20 字 | 截断或提示修改 |
| 登录过期 | 检测到登录页时提示重新登录 |

## 性能指标

- 发布时间：50-70 秒/篇
- 成功率：>95%
