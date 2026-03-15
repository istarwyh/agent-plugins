---
name: publishing-xiaohongshu
description: Creates and publishes high-quality posts to Xiaohongshu (小红书/Little Red Book) with content strategy, aesthetics, and platform best practices. Uses AI Agent + Chrome DevTools MCP for reliable publishing. Use when user wants to publish to Xiaohongshu, 小红书, Little Red Book, or needs help creating engaging Chinese social media content.
---

# Publishing to Xiaohongshu

创作并发布高质量的小红书笔记。

**核心价值**：内容策略 + 美学排版 + 可靠发布

## Quick Start

### Prerequisites

- Chrome 145+ browser
- Chrome DevTools MCP configured
- Xiaohongshu account (logged in)

### Setup

```bash
bash /path/to/xiaohongshu-plugin/scripts/ensure-chrome-debug.sh
```

### Create and publish

请AI帮你创作并发布：

```
请帮我创作一篇关于[主题]的小红书笔记，
面向[目标人群]，风格[风格描述]
```

AI会：
1. 根据内容指南创作标题和正文
2. 优化排版和emoji使用
3. 选择精准话题标签
4. 自动发布到小红书
5. 验证发布成功

## Content Creation Principles

### Title Strategy (≤20字)

**吸引力公式**：数字 + 痛点/好处 + emoji

好的标题：
- ✅ "3个技巧让你的照片更高级 📸"
- ✅ "终于找到了！平价好用的护肤品 💕"
- ✅ "新手必看｜5分钟学会化妆 ✨"

避免：
- ❌ "分享一下我的日常"（太平淡）
- ❌ "今天天气真好"（无价值点）

### Content Structure (≤500字)

**黄金结构**：
```
【开头】吸引注意（1-2行）
    ↓
【主体】核心内容（分点呈现）
    ↓
【结尾】互动引导（话题标签）
```

**开头技巧**：
- 痛点共鸣："姐妹们！是不是也有这个困扰？"
- 惊喜发现："终于找到了！这个宝藏店铺..."
- 直接价值："今天分享3个超实用的技巧"

**主体分点**：
```
✨ 第一点：XXX
• 具体说明
• 实际案例

✨ 第二点：XXX
...
```

**结尾互动**：
```
💬 你们有什么好方法吗？评论区见！
❤️ 觉得有用记得点赞收藏哦

#话题1 #话题2 #话题3
```

### Formatting Aesthetics

**换行原则**：
- 每1-2句话换行
- 分点内容必须换行
- 段落间空一行

**Emoji使用**：
- 📌 重点标记
- ✨ 亮点突出
- ⚠️ 注意事项
- 💡 小贴士
- ❤️ 推荐强调

### Hashtag Strategy

**3类标签组合**（3-6个）：
1. 热门话题（1-2个）
2. 精准定位（2-3个）
3. 长尾标签（1-2个）

## Publishing Workflow

**创作流程**：
1. 理解主题和目标人群
2. 根据 [CONTENT_GUIDE.md](CONTENT_GUIDE.md) 创作内容
3. 优化标题、排版、标签
4. 进行内容质量自检
5. 发布到小红书

**技术流程**：
- 使用视觉反馈（截图）
- 智能决策适应页面变化
- 详见 [WORKFLOW.md](WORKFLOW.md)

**性能**：50-70秒/篇，>95%成功率

## Content Quality Checklist

发布前检查：

```
内容质量检查：
- [ ] 标题是否吸引人？（≤20字）
- [ ] 开头是否抓住注意力？
- [ ] 内容是否有实用价值？
- [ ] 排版是否清晰易读？
- [ ] emoji使用是否恰当？
- [ ] 是否有互动引导？
- [ ] 话题标签是否精准？（3-6个）
- [ ] 总字数是否≤500字？
```

## MCP Tools

### Screenshot Best Practices

**重要**：使用截图工具时遵循以下原则以避免文件过大：

1. **优先使用文本快照**：`take_snapshot`（文本）优于 `take_screenshot`（图片）
2. **必须截图时的设置**：
   - 使用 `filePath` 保存到磁盘（如 `/tmp/screenshot.png`）
   - 格式：`jpeg`，质量：`50`
   - 针对特定元素：使用 `uid` 参数而非全页面
3. **查看截图**：使用 `Read` 工具查看保存的文件，不要内联到上下文

示例：
```javascript
// ✅ 正确：保存到文件
mcp1_take_screenshot({
  filePath: "/tmp/screenshot.png",
  format: "jpeg",
  quality: 50,
  uid: "specific-element-uid"
})

// ❌ 错误：直接返回图片数据（可能超过20MB）
mcp1_take_screenshot({ fullPage: true })
```

### Available Tools

- `chrome-devtools:mcp1_navigate_page`
- `chrome-devtools:mcp1_take_screenshot`
- `chrome-devtools:mcp1_take_snapshot`（推荐）
- `chrome-devtools:mcp1_evaluate_script`

## Resources

- **[CONTENT_GUIDE.md](CONTENT_GUIDE.md)** - 内容创作指南（美学、运营、技巧）
- **[WORKFLOW.md](WORKFLOW.md)** - 技术发布流程（10步SOP）

## Support

If you encounter any issues with this plugin, please report them following our [Support Guide](../../../SUPPORT.md). Your feedback helps improve the community experience!

## Notes

- 首次登录需要扫码
- 保持Chrome窗口开启
- 内容需符合小红书平台规则

---

**理念**：真诚分享 > 刻意营销
