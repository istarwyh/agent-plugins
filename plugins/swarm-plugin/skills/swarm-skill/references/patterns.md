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
