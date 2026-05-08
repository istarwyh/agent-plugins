---
name: env-config
description: >
  Claude Code 环境变量配置向导。通过交互式问答，根据用户的身份和使用场景，
  推荐合适的环境变量配置，并使用 update-config 应用到 settings.json。
  当用户提到"环境变量"、"env"、"配置"、"设置"、"proxy"、"代理"、
  "模型切换"、"token"、"缓存"、"成本"、"CI"、"自动化"等关键词时触发。
  也适用于用户说"帮我配一下 Claude Code"、"优化一下设置"等场景。
---

# Claude Code 环境变量配置向导

## 你的角色

你是一个友好的配置顾问。用户不需要记住任何环境变量——你来问，用户来选，你来配。

## 工作流程

### Step 1: 识别用户场景

用 `AskUserQuestion` 询问用户的身份和使用场景：

**问题 1: 你的使用场景是什么？**
- 🏠 本地直连 Anthropic API（最常见）
- 🌐 通过 API 代理/中转使用（如 OpenRouter、自建网关）
- ☁️ 通过 AWS Bedrock 或 Google Vertex AI 使用
- 🔧 CI/CD 或自动化脚本中使用

**问题 2: 你最关心什么？**
- 💰 成本控制（减少 token 消耗、优化缓存）
- ⚡ 稳定性（禁用更新、减少干扰）
- 🚀 性能（大输出、长任务）
- 🤔 我不确定，你推荐就好

### Step 2: 根据场景推荐配置

根据用户选择，从下面的 YAML 配置目录中筛选推荐。**只推荐用户需要的变量**，不要一股脑全列出来。

### Step 3: 确认并应用

向用户展示推荐的配置（简洁格式），询问确认：
- ✅ 就用这些，帮我配上
- ✏️ 我想调整几个
- ⏭️ 跳过，不需要配置

确认后，调用 `update-config` skill 将环境变量写入 settings.json。

---

## 环境变量配置目录（YAML）

以下是完整的环境变量目录。按类别组织，每个变量包含名称、描述、默认值和适用场景标签。

```yaml
# ============================================================
# Claude Code 环境变量配置目录
# 版本: 2026-05-08
# ============================================================

categories:

  # ----------------------------------------------------------
  - name: "认证与 API"
    description: "连接 Anthropic API 的基本配置"
    variables:
      - name: ANTHROPIC_API_KEY
        description: "Anthropic API 密钥（主要认证方式）"
        example: "sk-ant-..."
        tags: [所有场景]
        priority: required

      - name: ANTHROPIC_BASE_URL
        description: "覆盖 API 请求地址（用于代理/网关）"
        example: "https://your-gateway.example.com"
        tags: [代理用户]
        priority: conditional

      - name: ANTHROPIC_AUTH_TOKEN
        description: "Bearer token 认证（配合代理使用）"
        example: "sk-local-token"
        tags: [代理用户]
        priority: conditional

      - name: CLAUDE_API_KEY
        description: "API 密钥的别名（不常用，优先用 ANTHROPIC_API_KEY）"
        example: "sk-ant-..."
        tags: [所有场景]
        priority: optional

  # ----------------------------------------------------------
  - name: "模型选择"
    description: "覆盖 Claude Code 使用的默认模型"
    variables:
      - name: ANTHROPIC_MODEL
        description: "覆盖所有请求的模型（全局生效）"
        example: "claude-sonnet-4-20250514"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: ANTHROPIC_SMALL_FAST_MODEL
        description: "轻量任务用的模型（摘要、分类等内部任务）"
        example: "claude-haiku-3.5"
        tags: [高级用户]
        priority: optional

      - name: ANTHROPIC_DEFAULT_OPUS_MODEL
        description: "覆盖 Opus 层级模型（深度推理任务）"
        example: "claude-opus-4-20250514"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: ANTHROPIC_DEFAULT_SONNET_MODEL
        description: "覆盖 Sonnet 层级模型（主力编码任务）"
        example: "claude-sonnet-4-20250514"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: ANTHROPIC_DEFAULT_HAIKU_MODEL
        description: "覆盖 Haiku 层级模型（轻量快速任务）"
        example: "claude-haiku-3.5-20241022"
        tags: [代理用户, 高级用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "云厂商路由"
    description: "通过 AWS Bedrock 或 Google Vertex AI 使用 Claude"
    variables:
      - name: CLAUDE_CODE_USE_BEDROCK
        description: "设为 1 走 AWS Bedrock"
        example: "1"
        tags: [云厂商用户]
        priority: conditional

      - name: CLAUDE_CODE_USE_VERTEX
        description: "设为 1 走 Google Vertex AI"
        example: "1"
        tags: [云厂商用户]
        priority: conditional

      - name: AWS_REGION
        description: "AWS 区域"
        example: "us-east-1"
        tags: [云厂商用户]
        priority: conditional

      - name: AWS_PROFILE
        description: "AWS CLI 配置文件"
        example: "my-profile"
        tags: [云厂商用户]
        priority: conditional

      - name: CLOUD_ML_REGION
        description: "Google Cloud 区域"
        example: "us-east5"
        tags: [云厂商用户]
        priority: conditional

      - name: ANTHROPIC_VERTEX_PROJECT_ID
        description: "GCP 项目 ID"
        example: "my-project"
        tags: [云厂商用户]
        priority: conditional

  # ----------------------------------------------------------
  - name: "输出与 Token 控制"
    description: "控制响应长度和思考深度"
    variables:
      - name: CLAUDE_CODE_MAX_OUTPUT_TOKENS
        description: "单次最大输出 token 数（复杂任务建议调高）"
        default: "模型默认"
        example: "50000"
        tags: [所有场景]
        priority: recommended

      - name: MAX_THINKING_TOKENS
        description: "深度思考的 token 上限"
        default: "31999"
        example: "10000"
        tags: [高级用户, 成本控制]
        priority: optional

      - name: CLAUDE_CODE_MAX_TURNS
        description: "agentic 循环最大轮数（CI 模式下限制防止无限循环）"
        default: "无限"
        example: "50"
        tags: [CI/自动化]
        priority: conditional

  # ----------------------------------------------------------
  - name: "Bash 工具"
    description: "控制 Bash 命令的执行行为"
    variables:
      - name: BASH_DEFAULT_TIMEOUT_MS
        description: "Bash 命令默认超时（毫秒）"
        default: "120000（2 分钟）"
        example: "300000"
        tags: [高级用户, CI/自动化]
        priority: optional

      - name: BASH_MAX_TIMEOUT_MS
        description: "Bash 命令最大超时上限"
        example: "600000"
        tags: [高级用户]
        priority: optional

      - name: BASH_MAX_OUTPUT_LENGTH
        description: "Bash 输出最大处理长度"
        example: "100000"
        tags: [高级用户]
        priority: optional

      - name: CLAUDE_BASH_MAINTAIN_PROJECT_WORKING_DIRECTORY
        description: "Bash 工具在命令间保持项目工作目录"
        example: "true"
        tags: [高级用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "MCP 配置"
    description: "Model Context Protocol 服务器连接配置"
    variables:
      - name: MCP_TIMEOUT
        description: "MCP 服务器连接超时（秒）"
        example: "30"
        tags: [高级用户]
        priority: optional

      - name: MCP_TOOL_TIMEOUT
        description: "MCP 工具调用超时（秒）"
        example: "60"
        tags: [高级用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "缓存与成本"
    description: "控制 prompt caching 和请求开销"
    variables:
      - name: DISABLE_PROMPT_CACHING
        description: "禁用 prompt caching（调试时使用）"
        example: "1"
        tags: [高级用户, 成本控制]
        priority: optional

      - name: CLAUDE_CODE_ATTRIBUTION_HEADER
        description: "设为 0 可保留代理场景下的缓存命中（代理用户必加）"
        example: "0"
        tags: [代理用户]
        priority: conditional

  # ----------------------------------------------------------
  - name: "行为开关"
    description: "控制 Claude Code 的运行行为"
    variables:
      - name: DISABLE_AUTOUPDATER
        description: "禁用自动更新检查（避免工作中断）"
        example: "1"
        tags: [所有场景]
        priority: recommended

      - name: CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
        description: "禁用遥测和非必要网络请求"
        example: "1"
        tags: [所有场景, 成本控制]
        priority: recommended

      - name: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
        description: "启用实验性 Agent Teams 功能（需要 iTerm2 + it2）"
        example: "1"
        tags: [高级用户]
        priority: optional

      - name: CLAUDE_PACKAGE_MANAGER
        description: "覆盖包管理器检测（npm/pnpm/yarn/bun）"
        example: "pnpm"
        tags: [所有场景]
        priority: optional

      - name: CLAUDE_CODE_GIT_DIFF_IGNORE
        description: "git diff 忽略的文件模式（减少噪声）"
        example: "*.lock"
        tags: [高级用户]
        priority: optional

      - name: CLAUDE_CODE_API_KEY_HELPER
        description: "动态获取 API key 的脚本路径（用于密钥轮换）"
        example: "/path/to/key-script.sh"
        tags: [高级用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "网络代理"
    description: "HTTP/HTTPS 代理配置"
    variables:
      - name: HTTP_PROXY
        description: "HTTP 代理地址"
        example: "http://proxy:8080"
        tags: [代理用户, 云厂商用户]
        priority: conditional

      - name: HTTPS_PROXY
        description: "HTTPS 代理地址"
        example: "http://proxy:8080"
        tags: [代理用户, 云厂商用户]
        priority: conditional

      - name: NO_PROXY
        description: "不走代理的地址列表"
        example: "127.0.0.1,localhost"
        tags: [代理用户, 云厂商用户]
        priority: conditional

  # ----------------------------------------------------------
  - name: "调试"
    description: "调试和日志配置"
    variables:
      - name: DEBUG
        description: "调试日志命名空间（claude:* 为全量日志）"
        example: "claude:*"
        tags: [高级用户]
        priority: optional
```

---

## 场景推荐规则

根据用户选择的场景，按以下规则筛选推荐：

### 场景 A: 本地直连 Anthropic API

推荐配置：
```bash
ANTHROPIC_API_KEY=<用户填写>
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

可选建议：
- 如果用户在意成本 → 加 `MAX_THINKING_TOKENS=10000`
- 如果用户用 pnpm/yarn → 加 `CLAUDE_PACKAGE_MANAGER=pnpm`

### 场景 B: 通过 API 代理使用

推荐配置：
```bash
ANTHROPIC_API_KEY=<用户填写>
ANTHROPIC_BASE_URL=<代理地址>
ANTHROPIC_AUTH_TOKEN=<代理 token>
CLAUDE_CODE_ATTRIBUTION_HEADER=0
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

可选建议：
- 如果代理支持模型切换 → 加 `ANTHROPIC_MODEL=<模型名>`
- 如果需要覆盖三个层级 → 加 `ANTHROPIC_DEFAULT_OPUS_MODEL` / `SONNET` / `HAIKU`

### 场景 C: 通过 AWS Bedrock / Google Vertex AI

推荐配置（Bedrock）：
```bash
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

推荐配置（Vertex）：
```bash
CLAUDE_CODE_USE_VERTEX=1
CLOUD_ML_REGION=us-east5
ANTHROPIC_VERTEX_PROJECT_ID=<项目 ID>
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

### 场景 D: CI/CD 自动化

推荐配置：
```bash
ANTHROPIC_API_KEY=<从 CI secrets 读取>
CLAUDE_CODE_MAX_TURNS=50
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

可选建议：
- 如果任务复杂 → 加 `CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000`
- 如果需要长命令 → 加 `BASH_DEFAULT_TIMEOUT_MS=300000`

---

## 输出格式

向用户展示推荐配置时，用简洁的表格格式：

```
根据你的情况，我推荐以下配置：

| 变量 | 值 | 说明 |
|------|-----|------|
| ANTHROPIC_API_KEY | (需要你填写) | API 认证 |
| DISABLE_AUTOUPDATER | 1 | 禁用自动更新 |
| CLAUDE_CODE_MAX_OUTPUT_TOKENS | 50000 | 防止长输出被截断 |
| CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC | 1 | 减少网络开销 |

这些会写入 ~/.claude/settings.json 的 env 字段。
```

## 关于"不需要配置"

如果用户选择不配置，尊重他们的选择。简单说明：
- Claude Code 有合理的默认值，大多数场景开箱即用
- 随时可以通过 `/env-config` 重新配置
- 唯一必须的是 `ANTHROPIC_API_KEY`（如果还没设置的话）
