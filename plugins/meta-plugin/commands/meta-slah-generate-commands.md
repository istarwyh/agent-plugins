---
allowed-tools:Write(*),Read(*),Bash(mkdir:*),Bash(ls:*),Bash(echo:*),Bash(cp:*),Bash(date:*)
description:生成一个支持版本管理的新斜杠命令
version:1.0.0
author:xiaohui
---

# 生成带版本管理的斜杠命令

您正在创建一个内置版本管理的新Slash Comamnd。根据 `$ARGUMENTS` 中的用户需求，生成一个完整的带版本控制的斜杠命令文件。

## 版本管理功能

此命令支持：
- **语义化版本控制** (MAJOR.MINOR.PATCH)
- 更新现有命令时**自动创建备份**
- 在 YAML Frontmatter 中**跟踪版本历史**
- **生成更新日志**

## 指令：

1.  **解析参数**：格式应为 `<command-name>"<description>" [project|user] [version] [additional-requirements]`
    - `command-name`: 斜杠命令的名称（不带 `/`）
    - `description`: 命令的作用
    - `scope`: "project" (`.claude/commands/`) 或 "user" (`~/.claude/commands/`) - 默认为 "user"
    - `version`: 语义化版本（新命令默认为 "1.0.0"）
    - `additional-requirements`: 任何所需的特殊功能

2.  **版本管理流程**：
    - 检查命令文件是否已存在
    - 如果存在：使用当前版本号创建备份
    - 更新版本号（适当递增）
    - 向 Frontmatter 添加更新日志条目

3.  **创建适当的目录结构**：
    - 对于项目命令：`.claude/commands/`
    - 对于用户命令：`~/.claude/commands/`
    - 如果需要，为备份创建 `versions/` 子目录

4.  **生成带增强 YAML Frontmatter 的命令文件**：
    ```yaml
    ---
    allowed-tools: [适当的工具]
    description: [命令描述]
    version: "X.Y.Z"
    created: "YYYY-MM-DD"
    updated: "YYYY-MM-DD"
    changelog:
      - version: "X.Y.Z"
        date: "YYYY-MM-DD"
        changes: ["初始版本" 或具体更改]
    ---
    ```

5.  **备份策略**：
    - 更新前：`cp command-name.md command-name.v[old-version].md`
    - 保留备份文件以便回滚
    - 可选：将备份移动到 `versions/` 子目录

6.  **根据需求考虑以下功能**：
    - Git 操作：包含与 Git 相关的 `allowed-tools`
    - 文件操作：包含 `Read`, `Write`, `Edit` 工具
    - GitHub 操作：包含 `Bash(gh:*)` 工具
    - Web 操作：包含 `WebFetch`, `WebSearch` 工具
    - 目录操作：包含 `LS`, `Glob`, `Grep` 工具

## 示例 allowed-tools 模式：
- `Bash(git:*)` - 用于 Git 命令
- `Bash(gh:*)` - 用于 GitHub CLI 命令
- `Read(*)`, `Write(*)`, `Edit(*)` - 用于文件操作
- `LS(*)`, `Glob(*)`, `Grep(*)` - 用于目录/搜索操作
- `WebFetch(*)`, `WebSearch(*)` - 用于 Web 操作

## 命令参数：$ARGUMENTS

现在使用版本管理创建Slash Command 命令文件，确保它遵循 Claude Code 斜杠命令的最佳实践。
