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
- 内容必须 ≤ 500 字符
- 保留换行格式（使用 `<p>` 标签）
- 支持 emoji 和话题标签

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const editor = document.querySelector('.tiptap.ProseMirror');
if (!editor) return { success: false };

const content = `你的内容
支持换行
支持emoji 🎯
支持话题 #标签`;

editor.focus();
editor.innerHTML = '';

// 按行创建段落
const lines = content.split('\n');
lines.forEach(line => {
  const p = document.createElement('p');
  p.textContent = line || '\u200B'; // 空行用零宽字符
  editor.appendChild(p);
});

editor.dispatchEvent(new Event('input', { bubbles: true }));
editor.dispatchEvent(new Event('change', { bubbles: true }));

return { success: true, contentLength: content.length };
```

**验证**：使用 `chrome-devtools:mcp1_take_screenshot` 确认内容已填充

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
const titleInput = document.querySelector('input[placeholder*="标题"]') || 
                   document.querySelectorAll('input[type="text"]')[0];

if (titleInput) {
  titleInput.focus();
  titleInput.value = '你的标题（≤20字）';
  titleInput.dispatchEvent(new Event('input', { bubbles: true }));
  titleInput.dispatchEvent(new Event('change', { bubbles: true }));
  return { titleFilled: true, title: titleInput.value };
}
```

**验证**：确认标题字数显示正常（不超过20字）

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
- 页面显示"发布成功"提示（绿色对勾）
- URL 包含 `published=true` 参数
- 5秒后自动跳转到笔记页面

### 第十步：验证发布成功

**执行操作**：
```javascript
// 使用 chrome-devtools:mcp1_evaluate_script
const url = window.location.href;
return {
  published: url.includes('published=true'),
  currentUrl: url
};
```

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
