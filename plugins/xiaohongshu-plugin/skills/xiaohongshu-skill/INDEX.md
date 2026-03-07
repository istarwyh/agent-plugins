# Publishing to Xiaohongshu - Documentation Index

创作并发布高质量小红书笔记的完整指南。

## Start Here

1. **新手入门** → 阅读 [SKILL.md](SKILL.md) (3分钟)
2. **学习创作** → 学习 [CONTENT_GUIDE.md](CONTENT_GUIDE.md) (掌握美学和运营)
3. **技术流程** → 查看 [WORKFLOW.md](WORKFLOW.md) (10步SOP)
4. **立即开始** → 让AI帮你创作第一篇笔记

## Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [SKILL.md](SKILL.md) | 快速开始和核心原则 | 首次使用 (3分钟) |
| [CONTENT_GUIDE.md](CONTENT_GUIDE.md) | 内容创作指南（美学、运营、技巧） | 学习创作技巧 |
| [WORKFLOW.md](WORKFLOW.md) | 技术发布流程（10步SOP） | 理解技术实现 |
| [README.md](README.md) | 项目概述和使用场景 | 了解整体价值 |

## Quick Start

### Setup
```bash
bash /path/to/xiaohongshu-plugin/scripts/ensure-chrome-debug.sh
```

### Create and Publish

让AI帮你创作：
```
请帮我创作一篇关于[主题]的小红书笔记，
面向[目标人群]，风格[风格描述]
```

示例：
```
请帮我创作一篇关于"提升工作效率"的小红书笔记，
面向职场新人，风格轻松实用
```

## Key Files

### Documentation
- `SKILL.md` - 快速开始和核心原则
- `CONTENT_GUIDE.md` - 内容创作指南（美学、运营、技巧）
- `WORKFLOW.md` - 技术发布流程（10步SOP）
- `README.md` - 项目概述

### Scripts
- `../../scripts/ensure-chrome-debug.sh` - 启动Chrome调试模式

## Common Questions

**Q: 这个skill和普通发布工具有什么区别？**
A: 不仅自动发布，更重要的是提供内容创作指导，包括标题策略、排版美学、话题标签等。

**Q: 如何保证内容质量？**
A: 内置8项质量检查清单，自动验证字数、结构、emoji、标签等。

**Q: 需要准备什么？**
A: 只需告诉AI你的主题、目标人群和风格，AI会帮你创作完整内容。

**Q: 发布成功率如何？**
A: >95%，基于AI视觉反馈，每步都有截图验证。

**Q: 内容格式要求？**
A: 标题≤20字，正文≤500字，支持emoji、换行、话题标签。

## Architecture

**内容层**：
- 美学指导（标题、排版、emoji）
- 运营策略（标签、时间、类型）
- 质量保证（8项检查清单）

**技术层**：
- AI Agent智能决策
- Chrome DevTools MCP浏览器控制
- 视觉反馈（截图）确保可靠性
- 自适应工作流处理页面变化

## File Organization

Progressive disclosure：
- **SKILL.md** - 核心原则和快速开始
- **CONTENT_GUIDE.md** - 完整创作指南（美学、运营）
- **WORKFLOW.md** - 技术实现细节（10步SOP）

分层设计，按需阅读，高效学习。

## Next Steps

1. 📖 阅读 [SKILL.md](SKILL.md) - 了解核心价值
2. 🎨 学习 [CONTENT_GUIDE.md](CONTENT_GUIDE.md) - 掌握创作技巧
3. 🚀 启动Chrome：`bash ensure-chrome-debug.sh`
4. ✍️ 让AI帮你创作第一篇高质量笔记
5. 🔧 查看 [WORKFLOW.md](WORKFLOW.md) - 理解技术实现

## Support

- **快速开始**: 查看 [SKILL.md](SKILL.md)
- **创作指导**: 学习 [CONTENT_GUIDE.md](CONTENT_GUIDE.md)
- **技术细节**: 参考 [WORKFLOW.md](WORKFLOW.md)
- **问题调试**: AI Agent每步都有截图反馈

---

**Version:** 3.0 (Content-focused with aesthetics & strategy)

**定位**: 内容创作助手 + 自动化发布工具

**理念**: 真诚分享 > 刻意营销
