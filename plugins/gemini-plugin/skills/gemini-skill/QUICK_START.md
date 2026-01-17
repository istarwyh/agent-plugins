# Quick Start Guide - NotebookLM & Gemini Skill

快速上手指南：在 Claude Code 中使用 NotebookLM 和 Gemini

## 一次性设置

### 1. 认证（首次使用）

```bash
python scripts/run.py auth_manager.py setup
```

浏览器会自动打开，请登录您的 Google 账号。认证完成后，NotebookLM 和 Gemini 都可以使用。

### 2. 验证认证状态

```bash
python scripts/run.py auth_manager.py status
```

## 使用 Gemini（快速开始）

**最简单的方式 - 无需配置，直接查询：**

```bash
python scripts/run.py ask_gemini.py --question "你的问题"
```

### 文本查询示例

```bash
# 通用知识问题
python scripts/run.py ask_gemini.py --question "什么是人工智能？"

# 创意写作
python scripts/run.py ask_gemini.py --question "帮我写一首关于春天的诗"

# 代码生成
python scripts/run.py ask_gemini.py --question "用 Python 写一个快速排序算法"

# 调试模式（显示浏览器）
python scripts/run.py ask_gemini.py --question "..." --show-browser
```

### 图片生成示例

```bash
# 生成图片
python scripts/run.py generate_image.py --prompt "画一个可爱的雪人"

# 指定输出目录
python scripts/run.py generate_image.py --prompt "A futuristic city" --output ./my_images

# 生成艺术作品
python scripts/run.py generate_image.py --prompt "Abstract art with vibrant colors"

# 调试模式
python scripts/run.py generate_image.py --prompt "..." --show-browser
```

**图片保存位置：**
- 默认保存在当前目录
- 使用 `--output` 指定其他目录
- 文件名格式：`gemini_image_1_[timestamp].png`

## 使用 NotebookLM（文档查询）

### 1. 直接使用 URL 查询（无需添加到库）

```bash
python scripts/run.py ask_question.py \
  --question "你的问题" \
  --notebook-url "https://notebooklm.google.com/notebook/xxx"
```

### 2. 添加到库后查询

```bash
# 添加笔记本
python scripts/run.py notebook_manager.py add \
  --url "https://notebooklm.google.com/notebook/xxx" \
  --name "我的文档" \
  --description "项目技术文档" \
  --topics "技术,API,架构"

# 查看所有笔记本
python scripts/run.py notebook_manager.py list

# 激活笔记本（设为默认）
python scripts/run.py notebook_manager.py activate --id notebook-id

# 查询（使用激活的笔记本）
python scripts/run.py ask_question.py --question "你的问题"
```

## 两者的区别

| 特性 | Gemini | NotebookLM |
|------|--------|------------|
| 需要文档 | ❌ 不需要 | ✅ 需要上传文档 |
| 知识来源 | 通用知识 | 仅限上传的文档 |
| 适用场景 | 通用问答、创意、代码 | 专业文档查询 |
| 响应速度 | 快 | 较慢（需加载文档） |
| 答案来源 | 广泛 | 有引用和来源 |
| 幻觉风险 | 较高 | 极低（仅基于文档） |

## 选择建议

**使用 Gemini 当：**
- 需要通用知识或创意帮助
- 没有特定文档依赖
- 需要快速响应
- 代码生成、写作、翻译等

**使用 NotebookLM 当：**
- 查询特定文档内容
- 需要引用和来源
- 专业知识研究
- 需要高准确度的文档摘要

## 常见问题

### Q: 认证失败怎么办？
A: 确保网络连接正常，重试：
```bash
python scripts/run.py auth_manager.py reauth
```

### Q: 超时错误？
A: 已设置 5 分钟超时，如果网络很慢，可以使用 `--show-browser` 查看进度

### Q: 如何清除所有数据？
A:
```bash
python scripts/run.py cleanup_manager.py --confirm
```

## 在 Claude Code 中使用

当您在 Claude Code 中提到 "Gemini" 或 "NotebookLM" 时，skill 会自动激活。

**示例对话：**

```
你: 问问 Gemini 什么是量子计算
Claude: [自动调用 ask_gemini.py 并返回结果]

你: 查询我的 NotebookLM 笔记本关于 API 的内容
Claude: [调用 ask_question.py 查询您的文档]
```

## 高级用法

查看完整文档：
- `skill.md` - 完整使用说明
- `references/api_reference.md` - API 参考
- `references/troubleshooting.md` - 故障排查
- `references/usage_patterns.md` - 使用模式

## 快速命令参考

```bash
# Gemini 文本查询
python scripts/run.py ask_gemini.py --question "..."

# Gemini 图片生成
python scripts/run.py generate_image.py --prompt "..." [--output DIR]

# NotebookLM（直接 URL）
python scripts/run.py ask_question.py --question "..." --notebook-url "..."

# 认证管理
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py setup
python scripts/run.py auth_manager.py reauth

# 笔记本管理
python scripts/run.py notebook_manager.py list
python scripts/run.py notebook_manager.py add --url ... --name ... --description ... --topics ...
python scripts/run.py notebook_manager.py activate --id ...
```

---

**提示：** 所有命令都必须使用 `python scripts/run.py [脚本名]` 的格式，这样才能正确加载虚拟环境！
