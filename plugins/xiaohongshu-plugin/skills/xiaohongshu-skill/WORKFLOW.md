# 小红书自动发帖工作流 SOP

基于 AI Agent + Chrome DevTools MCP 的可靠发布流程。

## 前置条件

1. **Chrome 浏览器**（145+版本）
2. **Chrome DevTools MCP** 已配置
3. **小红书账号** 已登录

## 发布进度清单

复制此清单并在完成每步时打勾：

```
发布进度：
- [ ] 步骤1: 启动Chrome调试模式
- [ ] 步骤2: 导航到小红书创作中心
- [ ] 步骤3: 切换到图文发布模式
- [ ] 步骤4: 激活文字配图功能
- [ ] 步骤5: 填充内容（≤500字）
- [ ] 步骤6: 生成图片
- [ ] 步骤7: 进入发布编辑页面
- [ ] 步骤8: 填写标题（≤20字）
- [ ] 步骤9: 发布
- [ ] 步骤10: 验证发布成功
```

## 工作流程

### 第一步：启动 Chrome 调试模式

```bash
bash /path/to/xiaohongshu-plugin/scripts/ensure-chrome-debug.sh
```

验证：访问 `http://localhost:9222/json/version` 应返回 Chrome 信息

### 第二步：导航到小红书创作中心

使用 MCP 工具：
```
chrome-devtools:mcp1_navigate_page
  type: url
  url: https://creator.xiaohongshu.com/publish/publish
```

**预期结果**：页面显示"上传视频"或"上传图文"标签

### 第三步：切换到图文发布模式

**截图确认**：使用 `chrome-devtools:mcp1_take_screenshot` 查看当前页面

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const allElements = Array.from(document.querySelectorAll('*'));
const imageTextBtn = allElements.find(el => 
  el.textContent && el.textContent.trim() === '上传图文'
);
if (imageTextBtn) {
  imageTextBtn.click();
  return { clicked: true };
}
```

**预期结果**：页面显示"上传图片，或写文字生成图片"

### 第四步：激活文字配图功能

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const buttons = Array.from(document.querySelectorAll('*'));
const textImageBtn = buttons.find(btn => 
  btn.textContent && btn.textContent.includes('文字配图')
);
if (textImageBtn) {
  textImageBtn.click();
  return { clicked: true };
}
```

**预期结果**：出现文本编辑器（.tiptap.ProseMirror）

### 第五步：填充内容

**重要**：
- 单张卡片内容建议 ≤ 200 字符（文字过多会导致图片挤压、换行丢失）
- 总内容 ≤ 500 字符，超过 200 字时拆分为多张卡片
- 使用剪贴板粘贴（ClipboardEvent）替代 innerHTML，确保 tiptap 编辑器正确识别段落换行
- 支持 emoji 和话题标签

**方案A：单张卡片（内容 ≤ 200 字）**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const editor = document.querySelector('.tiptap.ProseMirror');
if (!editor) return { success: false };

const content = `你的内容
支持换行
支持emoji 🎯
支持话题 #标签`;

editor.focus();

// 选中并清除现有内容
document.execCommand('selectAll');
document.execCommand('delete');

// 将纯文本转为 HTML 段落
const lines = content.split('\n');
const htmlContent = lines.map(line =>
  `<p>${line || '<br>'}</p>`
).join('');

// 通过 ClipboardEvent 粘贴，让 tiptap 原生解析 HTML 段落
// 比直接操作 innerHTML 更可靠，能正确保留换行
const dt = new DataTransfer();
dt.setData('text/html', htmlContent);
dt.setData('text/plain', content);
const pasteEvent = new ClipboardEvent('paste', {
  bubbles: true,
  cancelable: true,
  clipboardData: dt
});
editor.dispatchEvent(pasteEvent);

return { success: true, contentLength: content.length };
```

**方案B：多张卡片（内容 > 200 字，推荐）**：

将内容按逻辑分段，每张卡片 ≤ 200 字，图片排版更清晰美观。

```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
// 第一张卡片：填入第一段内容
const editor = document.querySelector('.tiptap.ProseMirror');
if (!editor) return { success: false };

const card1Content = `第一段内容（开头 + 核心信息）
控制在200字以内
排版更清晰`;

editor.focus();
document.execCommand('selectAll');
document.execCommand('delete');

const lines = card1Content.split('\n');
const htmlContent = lines.map(line =>
  `<p>${line || '<br>'}</p>`
).join('');

const dt = new DataTransfer();
dt.setData('text/html', htmlContent);
dt.setData('text/plain', card1Content);
editor.dispatchEvent(new ClipboardEvent('paste', {
  bubbles: true,
  cancelable: true,
  clipboardData: dt
}));

return { success: true, card: 1, contentLength: card1Content.length };
```

然后点击"再写一张"按钮添加后续卡片：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const addBtn = Array.from(document.querySelectorAll('*'))
  .find(el => el.textContent?.trim() === '再写一张');
if (addBtn) {
  addBtn.click();
  return { clicked: true };
}
```

在新卡片编辑器中填入第二段内容，重复上述粘贴流程。

**为什么用 ClipboardEvent 而不是 innerHTML？**
- tiptap (ProseMirror) 编辑器通过内部事务管理文档状态
- 直接修改 innerHTML 绕过了 tiptap 的状态管理，导致：
  - 生成图片时换行丢失，内容挤成一段
  - 发布编辑页正文预览中段落信息丢失
- ClipboardEvent 触发 tiptap 的原生粘贴处理器，正确解析 `<p>` 标签为独立段落

**验证**：使用 `chrome-devtools:mcp1_take_screenshot` 确认：
1. 编辑器中内容分段显示（非连续文本）
2. 每段之间有明确换行

### 第六步：生成图片

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const allElements = Array.from(document.querySelectorAll('*'));
const generateBtn = allElements.find(el => 
  el.textContent?.trim() === '生成图片'
);
if (generateBtn) {
  let target = generateBtn;
  while (target.children.length === 1) {
    target = target.children[0];
  }
  target.click();
  return { clicked: true };
}
```

**预期结果**：页面跳转到"预览图片"界面，显示生成的图片卡片

#### 图片质量检查与优化

**重要**：生成图片后必须检查质量，如果图片丑陋需要优化

1. **检查图片质量**
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
// 等待图片加载完成
await new Promise(resolve => setTimeout(resolve, 3000));

// 检查图片是否生成成功
const imageElements = document.querySelectorAll('img[src*="generated"], img[src*="ai-image"]');
const hasValidImage = imageElements.length > 0 && 
                     imageElements[0].complete && 
                     imageElements[0].naturalWidth > 0;

if (!hasValidImage) {
  return { success: false, reason: '图片生成失败或未加载' };
}

// 检查图片质量指标
const img = imageElements[0];
const qualityIssues = [];

// 检查分辨率
if (img.naturalWidth < 800 || img.naturalHeight < 800) {
  qualityIssues.push('分辨率过低');
}

// 检查是否为纯色或简单图案
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
canvas.width = 50;
canvas.height = 50;
ctx.drawImage(img, 0, 0, 50, 50);
const imageData = ctx.getImageData(0, 0, 50, 50);
const uniqueColors = new Set();
for (let i = 0; i < imageData.data.length; i += 4) {
  const rgb = `${imageData.data[i]},${imageData.data[i+1]},${imageData.data[i+2]}`;
  uniqueColors.add(rgb);
}
if (uniqueColors.size < 10) {
  qualityIssues.push('图片过于简单，色彩单一');
}

return { 
  success: true, 
  qualityIssues,
  imageInfo: {
    width: img.naturalWidth,
    height: img.naturalHeight,
    colorVariety: uniqueColors.size
  }
};
```

2. **如果图片质量差，尝试优化**
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
// 方法1: 重新生成
const regenerateBtn = Array.from(document.querySelectorAll('*'))
  .find(el => el.textContent?.includes('重新生成') || el.textContent?.includes('换一批'));
if (regenerateBtn) {
  regenerateBtn.click();
  return { action: 'regenerating' };
}

// 方法2: 调整内容后重新生成
// 返回上一步修改内容
const backBtn = Array.from(document.querySelectorAll('*'))
  .find(el => el.textContent?.includes('上一步') || el.textContent?.includes('返回'));
if (backBtn) {
  backBtn.click();
  return { action: 'back_to_edit', suggestion: '增加更多描述性文字、emoji或话题标签' };
}

// 方法3: 手动优化建议
return { 
  action: 'manual_optimization_needed',
  suggestions: [
    '增加更多描述性文字，让AI生成更丰富的图片',
    '添加相关的emoji符号',
    '使用更具体的话题标签',
    '调整文字结构，使用分点描述'
  ]
};
```

3. **图片美化技巧**
如果多次生成仍不满意，尝试以下内容优化：

- **增加感官描述**：添加颜色、形状、风格等词汇
- **使用情感词汇**：温馨、清新、高级感等
- **添加场景元素**：咖啡、书本、植物等背景
- **指定风格**：简约、ins风、复古等

**示例优化**：
```
原内容：今天分享3个护肤技巧
优化后：分享3个让肌肤焕发光彩的护肤技巧 ✨ 温馨的卧室场景，ins风格
```

### 第七步：进入发布编辑页面

**截图确认**：使用 `chrome-devtools:mcp1_take_screenshot` 查看预览界面

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const buttons = Array.from(document.querySelectorAll('button'));
const nextBtn = buttons.find(btn => 
  btn.textContent && btn.textContent.trim() === '下一步'
);
if (nextBtn) {
  nextBtn.click();
  return { clicked: true };
}
```

**预期结果**：进入发布编辑页面，显示标题输入框、正文预览和"发布"按钮

### 第八步：填写标题

**重要**：标题必须 ≤ 20 字符

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
// 注意：小红书使用 React，直接设置 .value 不会触发状态更新
// 必须使用 nativeInputValueSetter 绕过 React 的合成事件
const titleInput = document.querySelector('input[placeholder*="标题"]') ||
                   document.querySelectorAll('input[type="text"]')[0];

if (titleInput) {
  titleInput.focus();
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, 'value'
  ).set;
  nativeInputValueSetter.call(titleInput, '你的标题（≤20字）');
  titleInput.dispatchEvent(new Event('input', { bubbles: true }));
  titleInput.dispatchEvent(new Event('change', { bubbles: true }));
  return { titleFilled: true, title: titleInput.value };
}
```

**验证**：确认标题字数计数器显示正确数字（而非 0/20），且不超过20字

### 第九步：发布

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const buttons = Array.from(document.querySelectorAll('button'));
const publishBtn = buttons.find(btn => 
  btn.textContent && btn.textContent.trim() === '发布'
);
if (publishBtn) {
  publishBtn.click();
  return { clicked: true };
}
```

**预期结果**：
- URL 跳转为包含 `published=true` 参数的新页面
- 页面回到创作中心首页（上传视频/图文界面）
- 注意：平台不显示"发布成功"文字提示，以 URL 变化为准

### 第十步：验证发布成功

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
// 注意：不要 wait_for "发布成功" 文字，平台不显示该文本
// 发布成功的标志是 URL 包含 published=true
const url = window.location.href;
const published = url.includes('published=true');
return {
  published,
  currentUrl: url,
  tip: published ? '发布成功' : '可能仍在处理中，等待几秒后重新检查 URL'
};
```

**备用验证**：如果 URL 检测不到 `published=true`，等待 5 秒后重试，
或使用 `chrome-devtools:mcp1_take_snapshot` 检查页面是否回到创作中心首页。

## 内容质量检查（发布前必做）

在第五步填充内容后，执行质量检查：

```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const editor = document.querySelector('.tiptap.ProseMirror');
const content = editor ? editor.textContent : '';

return {
  contentLength: content.length,
  hasEmoji: /[\u{1F300}-\u{1F9FF}]/u.test(content),
  hasHashtag: content.includes('#'),
  lineBreaks: (content.match(/\n/g) || []).length,
  qualityCheck: {
    lengthOK: content.length > 0 && content.length <= 500,
    hasStructure: (content.match(/\n/g) || []).length >= 3,
    hasEmoji: /[\u{1F300}-\u{1F9FF}]/u.test(content),
    hasHashtag: content.includes('#')
  }
};
```

**检查清单**：
```
内容质量：
- [ ] 字数在500字以内
- [ ] 有清晰的段落结构（至少3个换行）
- [ ] 使用了emoji增强可读性
- [ ] 包含话题标签
- [ ] 开头吸引人
- [ ] 有互动引导
```

如果检查未通过，返回第五步重新优化内容。

## 错误处理

### 常见问题

1. **页面加载超时**
   - 等待 5-10 秒后重试
   - 使用 `chrome-devtools:mcp1_take_screenshot` 确认页面状态

2. **元素未找到**
   - 使用 `chrome-devtools:mcp1_take_snapshot` 查看页面结构
   - 检查选择器是否正确

3. **内容超过500字**
   - 截断内容或分成多条帖子
   - 提示用户修改内容

4. **标题超过20字**
   - 自动截断到20字
   - 或提示用户修改

5. **登录过期**
   - 检测到登录页面时，提示用户重新登录
   - 等待用户登录后继续

## 性能指标

- **发布时间**：50-70 秒/篇
- **成功率**：>95%（基于 AI Agent 视觉反馈）
- **内容质量**：遵循小红书平台最佳实践

## 注意事项

1. **首次使用**需要人工登录小红书账号
2. **保持 Chrome 窗口**不要关闭
3. **内容质量优先**：宁可多花时间优化，不要急于发布
4. **平台规则**：
   - 避免硬广、微商内容
   - 不要虚假宣传
   - 遵守社区规范
5. **内容审核**：小红书可能对内容进行审核，发布成功不代表立即可见
6. **使用截图**：每个关键步骤都应该截图确认状态

## 优势

**内容创作**：
✅ **美学指导** - 遵循小红书平台美学规范
✅ **运营策略** - 标题、排版、标签优化
✅ **质量保证** - 发布前自动质量检查

**技术实现**：
✅ **可靠性高** - AI 视觉反馈，实时适应页面
✅ **智能决策** - 根据页面状态动态调整
✅ **易于调试** - 截图直观展示每步状态

## 工具依赖

- `chrome-devtools:mcp1_navigate_page` - 页面导航
- `chrome-devtools:mcp1_take_screenshot` - 截图查看
- `chrome-devtools:mcp1_take_snapshot` - 获取页面结构
- `chrome-devtools:mcp1_evaluate_script` - 执行 JavaScript
- `chrome-devtools:mcp1_wait_for` - 等待元素出现
