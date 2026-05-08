---
name: configuring-env
description: >
  提供 Claude Code 环境变量配置向导。通过交互式问答，根据用户的身份和使用场景，
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
- 🤖 使用非 Anthropic 模型（DeepSeek、Qwen、Moonshot 等，通过中转站）
- ☁️ 通过 AWS Bedrock 或 Google Vertex AI 使用
- 🔧 CI/CD 或自动化脚本中使用

**问题 2: 你最关心什么？**
- 💰 成本控制（减少 token 消耗、优化缓存）
- ⚡ 稳定性（连接稳定、禁用干扰）
- 🚀 性能（大输出、长任务）
- 🤔 我不确定，你推荐就好

### Step 2: 根据场景推荐配置

根据用户选择，从下面的 YAML 配置目录中筛选推荐。**只推荐用户需要的变量**，不要一股脑全列出来。

特别注意：如果用户使用非 Anthropic 模型（DeepSeek/Qwen/Moonshot 等），**必须**包含兼容性变量（thinking 相关），否则会报错。

### Step 3: 确认并应用

向用户展示推荐的配置（简洁格式），询问确认：
- ✅ 就用这些，帮我配上
- ✏️ 我想调整几个
- ⏭️ 跳过，不需要配置

确认后，调用系统内置的 `update-config` skill 将环境变量写入 settings.json（该 skill 为 Claude Code 内置，无需额外安装）。

---

## 环境变量配置目录（YAML）

以下是完整的环境变量目录。按类别组织，每个变量包含名称、描述、默认值和适用场景标签。

```yaml
# ============================================================
# Claude Code 环境变量配置目录
# 版本: 2.0.0
# 面向中国大陆用户优化
# ============================================================

categories:

  # ----------------------------------------------------------
  - name: "认证与 API"
    description: "连接 Anthropic API 的基本配置"
    variables:
      - name: ANTHROPIC_API_KEY
        description: "API 密钥。从 Anthropic 官方或中转站获取"
        example: "sk-ant-..."
        tags: [所有场景]
        priority: required

      - name: ANTHROPIC_BASE_URL
        description: "API 端点地址。中国大陆用户通常需要通过中转站访问"
        example: "https://api.deepseek.com/anthropic"
        tags: [代理用户, 非Anthropic模型]
        priority: conditional
        note: "必须是 Anthropic Messages API 兼容端点。部分中转站使用 /anthropic 路径前缀"

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
        description: "覆盖所有请求的主模型 ID"
        example: "deepseek-chat"
        tags: [代理用户, 非Anthropic模型, 高级用户]
        priority: conditional
        note: "必须是你的 API 端点支持的模型 ID。不同中转站格式不同"

      - name: MODEL
        description: "模型别名。与 ANTHROPIC_MODEL 二选一，后者优先"
        example: "deepseek-chat"
        tags: [代理用户, 非Anthropic模型]
        priority: optional

      - name: ANTHROPIC_SMALL_FAST_MODEL
        description: "轻量任务用的模型（token 估算、思考摘要等内部任务）"
        example: "deepseek-chat"
        tags: [代理用户, 非Anthropic模型, 成本控制]
        priority: recommended
        note: "非 Anthropic 用户建议设为便宜模型（如 deepseek-chat），节省后台任务开销"

      - name: ANTHROPIC_DEFAULT_OPUS_MODEL
        description: "覆盖 Opus 层级模型（深度推理任务）"
        example: "claude-opus-4-6"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: ANTHROPIC_DEFAULT_SONNET_MODEL
        description: "覆盖 Sonnet 层级模型（主力编码任务）"
        example: "claude-sonnet-4-6"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: ANTHROPIC_DEFAULT_HAIKU_MODEL
        description: "覆盖 Haiku 层级模型（轻量快速任务）"
        example: "claude-haiku-4-5-20251001"
        tags: [代理用户, 高级用户]
        priority: optional

      - name: CLAUDE_CODE_SUBAGENT_MODEL
        description: "覆盖子 agent 使用的模型。主模型用强模型、子 agent 用便宜模型可节省成本"
        example: "deepseek-chat"
        tags: [成本控制, 高级用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "非 Anthropic 模型兼容"
    description: "使用 DeepSeek/Qwen/Moonshot 等非 Anthropic 模型时必须设置的兼容性变量"
    variables:
      - name: CLAUDE_CODE_DISABLE_THINKING
        description: "关闭扩展思考功能。非 Anthropic 模型不支持 thinking 协议，不设会报错"
        example: "1"
        tags: [非Anthropic模型]
        priority: required
        note: "DeepSeek、Qwen、Moonshot 等模型均不支持 Anthropic thinking 协议"

      - name: CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING
        description: "关闭自适应思考切换。非 Anthropic 模型不支持此功能"
        example: "1"
        tags: [非Anthropic模型]
        priority: required

      - name: DISABLE_INTERLEAVED_THINKING
        description: "关闭交错思考（interleaved thinking）。这是 Claude Code 高效使用工具的核心机制，但非 Anthropic 模型不支持"
        example: "1"
        tags: [非Anthropic模型]
        priority: required
        note: "不关闭会发送无效的 beta header，导致请求失败"

      - name: DISABLE_PROMPT_CACHING
        description: "禁用 prompt caching。大多数中转站不支持 Anthropic 缓存协议"
        example: "1"
        tags: [非Anthropic模型, 代理用户]
        priority: conditional
        note: "不关闭会在请求中包含无效的 cache_control 字段，可能导致报错"

  # ----------------------------------------------------------
  - name: "推理与思考"
    description: "控制模型的推理力度和思考深度"
    variables:
      - name: CLAUDE_CODE_EFFORT_LEVEL
        description: "控制模型推理力度。优先级: 环境变量 > 会话 /effort > 模型默认"
        example: "medium"
        tags: [所有场景, 成本控制]
        priority: optional
        note: "可选值: low（轻量/快/省token）、medium、high（深度推理）、max、unset/auto"

      - name: MAX_THINKING_TOKENS
        description: "扩展思考的 token 预算。越多推理越深，但消耗越大"
        example: "10000"
        tags: [高级用户, 成本控制]
        priority: optional
        note: "日常 10000 够用，复杂任务可调到 20000。非 Anthropic 模型无需设置"

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
    description: "控制响应长度和上下文"
    variables:
      - name: CLAUDE_CODE_MAX_OUTPUT_TOKENS
        description: "单次最大输出 token 数（复杂任务建议调高）"
        default: "模型默认"
        example: "50000"
        tags: [所有场景]
        priority: recommended

      - name: CLAUDE_CODE_MAX_CONTEXT_TOKENS
        description: "手动设置上下文窗口 token 上限。当中转站报告的上下文窗口大小不准确时使用"
        example: "64000"
        tags: [代理用户, 非Anthropic模型]
        priority: optional

      - name: CLAUDE_CODE_MAX_TURNS
        description: "agentic 循环最大轮数（CI 模式下限制防止无限循环）"
        default: "无限"
        example: "50"
        tags: [CI/自动化]
        priority: conditional

  # ----------------------------------------------------------
  - name: "上下文压缩"
    description: "控制对话历史的自动压缩行为"
    variables:
      - name: DISABLE_AUTO_COMPACT
        description: "关闭自动上下文压缩。关闭后上下文满时可能导致请求失败"
        example: "1"
        tags: [高级用户]
        priority: optional
        note: "手动 /compact 命令仍可用"

      - name: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE
        description: "覆盖自动压缩触发阈值（百分比 0-100）。只能降低阈值（更早触发）"
        example: "50"
        tags: [高级用户]
        priority: optional
        note: "上下文窗口较小的模型可能需要更早触发压缩"

  # ----------------------------------------------------------
  - name: "网络代理"
    description: "HTTP/HTTPS 代理和连接配置"
    variables:
      - name: HTTP_PROXY
        description: "HTTP 代理地址"
        example: "http://127.0.0.1:7890"
        tags: [代理用户, 云厂商用户]
        priority: conditional

      - name: HTTPS_PROXY
        description: "HTTPS 代理地址"
        example: "http://127.0.0.1:7890"
        tags: [代理用户, 云厂商用户]
        priority: conditional

      - name: NO_PROXY
        description: "不走代理的地址列表，逗号分隔"
        example: "localhost,127.0.0.1"
        tags: [代理用户, 云厂商用户]
        priority: conditional

      - name: CLAUDE_CODE_PROXY_RESOLVES_HOSTS
        description: "让代理服务器负责 DNS 解析（SOCKS5 或透明代理时需要开启）"
        example: "1"
        tags: [代理用户]
        priority: optional

      - name: API_TIMEOUT_MS
        description: "API 请求总超时时间（毫秒）。通过代理连接时延迟较高，建议调大"
        example: "120000"
        tags: [代理用户, 非Anthropic模型]
        priority: recommended
        note: "建议 120000（2 分钟）或更高"

      - name: SSL_CERT_FILE
        description: "自定义 CA 证书文件路径。代理使用自签名证书或企业内网 CA 时需要"
        example: "/path/to/ca-bundle.crt"
        tags: [代理用户]
        priority: optional

  # ----------------------------------------------------------
  - name: "网络稳定性"
    description: "应对不稳定网络环境的配置"
    variables:
      - name: CLAUDE_CODE_MAX_RETRIES
        description: "API 请求失败后的最大重试次数。代理线路不稳定时调大"
        example: "5"
        tags: [代理用户, 非Anthropic模型]
        priority: recommended

      - name: CLAUDE_STREAM_IDLE_TIMEOUT_MS
        description: "流式响应空闲超时（毫秒）。超时后连接被强制终止，防止无限挂起"
        default: "90000"
        example: "120000"
        tags: [代理用户]
        priority: optional
        note: "需配合 CLAUDE_ENABLE_STREAM_WATCHDOG=1 使用。代理线路质量差时调大"

      - name: CLAUDE_ENABLE_STREAM_WATCHDOG
        description: "启用流式响应看门狗。开启后 CLAUDE_STREAM_IDLE_TIMEOUT_MS 才生效"
        example: "1"
        tags: [代理用户]
        priority: optional

      - name: CLAUDE_CODE_RESUME_INTERRUPTED_TURN
        description: "中断后自动恢复对话。网络不稳定时避免会话丢失"
        example: "1"
        tags: [代理用户, CI/自动化]
        priority: optional

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
    description: "控制 prompt caching 和费用相关"
    variables:
      - name: CLAUDE_CODE_ATTRIBUTION_HEADER
        description: "设为 0 关闭归属头。中转站不识别此头或因此头限流时使用"
        example: "0"
        tags: [代理用户, 非Anthropic模型]
        priority: conditional
        note: "归属头包含 cc_version（含指纹），某些中转站可能据此限流"

      - name: DISABLE_COST_WARNINGS
        description: "隐藏 token 费用警告。中转站定价与 Anthropic 官方不同时费用不准确"
        example: "1"
        tags: [代理用户, 非Anthropic模型]
        priority: recommended

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
        description: "关闭非必要网络请求（分析、市场检查等）。在 GFW 后可减少连接失败"
        example: "1"
        tags: [所有场景]
        priority: recommended

      - name: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
        description: "启用实验性 Agent Teams 功能（多 agent 协作）"
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
  - name: "界面与交互"
    description: "终端渲染和输出风格"
    variables:
      - name: CLAUDE_CODE_NO_FLICKER
        description: "开启全屏渲染模式，消除闪烁，支持鼠标滚轮浏览历史"
        example: "1"
        tags: [所有场景]
        priority: optional
        note: "在 tmux -CC（iTerm2 集成模式）下自动禁用"

      - name: CLAUDE_CODE_BRIEF
        description: "精简输出模式，适合快速查看结果"
        example: "1"
        tags: [所有场景]
        priority: optional

      - name: CLAUDE_CODE_SYNTAX_HIGHLIGHT
        description: "控制代码语法高亮。关闭可略微减少渲染开销"
        example: "0"
        tags: [高级用户]
        priority: optional

      - name: CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY
        description: "关闭使用反馈调查弹窗"
        example: "1"
        tags: [所有场景]
        priority: optional

  # ----------------------------------------------------------
  - name: "遥测与隐私"
    description: "控制数据上报和隐私"
    variables:
      - name: DISABLE_TELEMETRY
        description: "关闭所有遥测数据上报"
        example: "1"
        tags: [所有场景]
        priority: recommended

  # ----------------------------------------------------------
  - name: "配置目录"
    description: "自定义配置路径"
    variables:
      - name: CLAUDE_CONFIG_DIR
        description: "自定义 Claude Code 配置目录（默认 ~/.claude）"
        example: "/custom/path/.claude"
        tags: [高级用户]
        priority: optional

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

根据用户选择的场景，按以下规则筛选推荐。

### 场景 A: 本地直连 Anthropic API

推荐配置：
```bash
ANTHROPIC_API_KEY=<用户填写>
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
```

可选建议：
- 如果用户在意成本 → 加 `MAX_THINKING_TOKENS=10000`、`CLAUDE_CODE_EFFORT_LEVEL=low`
- 如果用户用 pnpm/yarn → 加 `CLAUDE_PACKAGE_MANAGER=pnpm`
- 如果终端闪烁 → 加 `CLAUDE_CODE_NO_FLICKER=1`

### 场景 B: 通过 API 代理使用（Anthropic 模型）

推荐配置：
```bash
ANTHROPIC_API_KEY=<用户填写>
ANTHROPIC_BASE_URL=<代理地址>
CLAUDE_CODE_ATTRIBUTION_HEADER=0
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
DISABLE_COST_WARNINGS=1
API_TIMEOUT_MS=120000
CLAUDE_CODE_MAX_RETRIES=5
```

可选建议：
- 如果代理支持模型切换 → 加 `ANTHROPIC_MODEL=<模型名>`
- 如果代理不支持缓存 → 加 `DISABLE_PROMPT_CACHING=1`
- 如果用 SOCKS5 代理 → 加 `CLAUDE_CODE_PROXY_RESOLVES_HOSTS=1`
- 如果代理用自签名证书 → 加 `SSL_CERT_FILE=<证书路径>`
- 如果需要覆盖三个层级 → 加 `ANTHROPIC_DEFAULT_OPUS_MODEL` / `SONNET` / `HAIKU`
- 如果网络不稳定 → 加 `CLAUDE_STREAM_IDLE_TIMEOUT_MS=120000`、`CLAUDE_ENABLE_STREAM_WATCHDOG=1`、`CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1`

### 场景 C: 使用非 Anthropic 模型（DeepSeek/Qwen/Moonshot 等）

这是中国大陆用户最常见的场景。**必须**包含兼容性变量，否则会报错。

推荐配置：
```bash
ANTHROPIC_API_KEY=<用户填写>
ANTHROPIC_BASE_URL=<中转站地址，如 https://api.deepseek.com/anthropic>
ANTHROPIC_MODEL=<模型名，如 deepseek-chat>
ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat

# ── 兼容性（必须）──
CLAUDE_CODE_DISABLE_THINKING=1
CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1
DISABLE_INTERLEAVED_THINKING=1
DISABLE_PROMPT_CACHING=1

# ── 稳定性 ──
CLAUDE_CODE_ATTRIBUTION_HEADER=0
DISABLE_COST_WARNINGS=1
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
API_TIMEOUT_MS=120000
CLAUDE_CODE_MAX_RETRIES=5
CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000
```

可选建议：
- 如果想省成本 → 加 `CLAUDE_CODE_EFFORT_LEVEL=low`、`CLAUDE_CODE_SUBAGENT_MODEL=<便宜模型>`
- 如果中转站报告的上下文窗口不准 → 加 `CLAUDE_CODE_MAX_CONTEXT_TOKENS=<实际值>`
- 如果用 SOCKS5 代理 → 加 `CLAUDE_CODE_PROXY_RESOLVES_HOSTS=1`
- 如果网络不稳定 → 加 `CLAUDE_STREAM_IDLE_TIMEOUT_MS=120000`、`CLAUDE_ENABLE_STREAM_WATCHDOG=1`、`CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1`

**常见中转站参考配置：**

DeepSeek:
```bash
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_MODEL=deepseek-chat
ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
```

Moonshot (Kimi):
```bash
ANTHROPIC_BASE_URL=https://api.moonshot.cn/anthropic
ANTHROPIC_MODEL=moonshot-v1-8k
ANTHROPIC_SMALL_FAST_MODEL=moonshot-v1-8k
```

### 场景 D: 通过 AWS Bedrock / Google Vertex AI

推荐配置（Bedrock）：
```bash
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
```

推荐配置（Vertex）：
```bash
CLAUDE_CODE_USE_VERTEX=1
CLOUD_ML_REGION=us-east5
ANTHROPIC_VERTEX_PROJECT_ID=<项目 ID>
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
```

### 场景 E: CI/CD 自动化

推荐配置：
```bash
ANTHROPIC_API_KEY=<从 CI secrets 读取>
CLAUDE_CODE_MAX_TURNS=50
DISABLE_AUTOUPDATER=1
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
DISABLE_TELEMETRY=1
```

可选建议：
- 如果任务复杂 → 加 `CLAUDE_CODE_MAX_OUTPUT_TOKENS=50000`
- 如果需要长命令 → 加 `BASH_DEFAULT_TIMEOUT_MS=300000`
- 如果网络不稳定 → 加 `CLAUDE_CODE_RESUME_INTERRUPTED_TURN=1`

---

## 输出格式

向用户展示推荐配置时，用简洁的表格格式：

```
根据你的情况，我推荐以下配置：

| 变量 | 值 | 说明 |
|------|-----|------|
| ANTHROPIC_API_KEY | (需要你填写) | API 认证 |
| ANTHROPIC_BASE_URL | https://api.deepseek.com/anthropic | DeepSeek 中转站 |
| ANTHROPIC_MODEL | deepseek-chat | 主模型 |
| CLAUDE_CODE_DISABLE_THINKING | 1 | DeepSeek 不支持 thinking |
| CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING | 1 | 关闭自适应思考 |
| DISABLE_INTERLEAVED_THINKING | 1 | 关闭交错思考 |
| DISABLE_PROMPT_CACHING | 1 | 中转站不支持缓存 |
| CLAUDE_CODE_ATTRIBUTION_HEADER | 0 | 避免限流 |
| DISABLE_COST_WARNINGS | 1 | 中转站定价不同 |
| DISABLE_AUTOUPDATER | 1 | 禁用自动更新 |
| CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC | 1 | 减少网络开销 |
| DISABLE_TELEMETRY | 1 | 关闭遥测 |
| API_TIMEOUT_MS | 120000 | 代理延迟较高 |
| CLAUDE_CODE_MAX_RETRIES | 5 | 不稳定时多重试 |
| CLAUDE_CODE_MAX_OUTPUT_TOKENS | 50000 | 防止长输出被截断 |

这些会写入 ~/.claude/settings.json 的 env 字段。
```

## 关于"不需要配置"

如果用户选择不配置，尊重他们的选择。简单说明：
- Claude Code 有合理的默认值，大多数场景开箱即用
- 随时可以通过 `/configuring-env` 重新配置
- 唯一必须的是 `ANTHROPIC_API_KEY`（如果还没设置的话）
- 如果使用非 Anthropic 模型，兼容性变量（thinking 相关）是必须的，否则会报错
