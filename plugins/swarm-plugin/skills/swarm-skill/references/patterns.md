# Decomposition Patterns & Teammate Templates

## Common Decomposition Patterns

| Pattern | When to use | Teammates | Dependency |
|---------|------------|-----------|------------|
| Dev + Test | New feature, CLI, API | developer → tester | tester blockedBy developer |
| Dev + Docs | Code change needs doc sync | developer + doc-writer | parallel |
| Research + Implement | Unknown library/approach | researcher → developer | developer blockedBy researcher |
| Design + Implement | Needs architecture first | architect → developer | developer blockedBy architect |
| Multi-module | Independent modules | module-a + module-b + ... | parallel |
| Dev + Review | Quality-critical code | developer → reviewer | reviewer blockedBy developer |
| Full pipeline | End-to-end delivery | developer → tester → committer | chain |

## Skill Matching

Match discovered skills to roles by keyword relevance:

| Role | Match keywords in skill name/description |
|------|------------------------------------------|
| tester | test, e2e, simplify, validate, webapp-testing |
| doc-writer | doc, documentation, writing |
| reviewer | review, lint, simplify, audit |
| committer | commit, push, git, pr |
| architect | spec, design, plan, research |
| developer | (usually no skill injection needed — uses base tools) |

If no skill matches a role, omit the skill section entirely. Teammates work fine with base tools.

## Teammate Prompt Template

```
你是 {role}。查看任务列表，认领并完成你的任务。

{key context from user's request}

{project conventions from CLAUDE.md, if present}

{ONLY if matching skills found:}
可用 Skills（通过 Skill 工具调用）：
- `/{skill}`: {purpose}
按需选用，不要重复造轮子。

完成后标记任务为 completed。
```

## Committer Prompt (with commit skill)

```
你是提交专员。所有开发/测试任务完成后，
用 Skill 工具调用 `/{commit-skill}` 提交代码。
完成后标记任务为 completed。
```

## Committer Prompt (without commit skill)

```
你是提交专员。所有开发/测试任务完成后：
1. git status → git add → git commit（合理的 message）
2. 询问用户是否 push
完成后标记任务为 completed。
```

## Full Agent Call Example

Below is a complete example showing the flow from decomposition to spawning teammates. This illustrates the exact Agent tool calls you must make.

**Scenario:** User asks to "implement a new CLI command with tests and update the docs."

### Step 1: Decompose (in main session)

Split into 3 subtasks:
- `developer`: implement the CLI command in `src/commands/new-cmd.ts`
- `tester`: write tests in `tests/commands/new-cmd.test.ts`
- `doc-writer`: update `README.md` with usage examples

### Step 2: Create Team & Tasks (in main session)

```
TeamCreate({ team_name: "cli-feature", description: "Implement new CLI command" })

TaskCreate({ subject: "Implement CLI command", description: "...", owner: "developer" })
TaskCreate({ subject: "Write tests", description: "...", owner: "tester" })
TaskCreate({ subject: "Update docs", description: "...", owner: "doc-writer" })

// Set dependency: tester waits for developer
TaskUpdate({ taskId: "<test-task-id>", addBlockedBy: ["<dev-task-id>"] })
```

### Step 3: Spawn Teammates (in a SINGLE message)

You MUST send all three Agent calls in one response to spawn them in parallel:

```
// These three calls go in ONE message — parallel tool use

Agent({
  description: "Implement CLI command",
  prompt: "你是 developer。查看任务列表，认领并完成你的任务。\n\n实现一个新的 CLI 命令...\n\n完成后标记任务为 completed。",
  run_in_background: true
})

Agent({
  description: "Write tests for CLI command",
  prompt: "你是 tester。查看任务列表，认领并完成你的任务。\n\n为 CLI 命令编写测试...\n\n完成后标记任务为 completed。",
  run_in_background: true
})

Agent({
  description: "Update documentation",
  prompt: "你是 doc-writer。查看任务列表，认领并完成你的任务。\n\n更新 README...\n\n完成后标记任务为 completed。",
  run_in_background: true
})
```

**Key points:**
- All three `Agent()` calls appear in a single assistant message (parallel tool use)
- `run_in_background: true` on every call — teammates run concurrently
- The tester will self-wait because of `addBlockedBy` — no need to delay its spawn
- Do NOT implement anything in the main session yourself
