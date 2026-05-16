# Decomposition Patterns, Role Skills, and Teammate Templates

Use this reference when running `swarm-skill` to choose teammates, inject discovered skills, and drive closed-loop iterations.

## Role → Skill Matching

Only inject skills that were actually discovered from the session skill list or `scripts/discover_skills.sh`. BMAD skills are recommended when installed, but never required.

| Role | Preferred discovered skills | Purpose |
|------|-----------------------------|---------|
| committer | `commit-then-push`, names containing commit/push/git/pr | commit, run hooks, push, open PR |
| tester | `e2e-test`, `simplify`, `bmad-tea-testarch-test-design`, `bmad-tea-testarch-test-review`, names containing test/e2e/validate/simplify | test design, execution, quality checks |
| reviewer | `bmad-review-adversarial-general`, `bmad-review-edge-case-hunter`, `code-review:code-review`, `bmad-editorial-review-prose`, `bmad-editorial-review-structure`, `review`, `security-review`, names containing review/audit/edge-case/editorial | adversarial design/code review, edge-case review, prose/structure review |
| researcher | `bmad-bmm-technical-research`, names containing research/search/explore | technical research |
| architect | `bmad-bmm-create-architecture`, `bmad-bmm-quick-spec`, names containing architecture/spec/design/plan | architecture or technical design |
| doc-writer | `bmad-index-docs`, names containing doc/documentation/writing | documentation updates |
| developer | usually none | direct implementation with base tools |

If no mapped skill exists for a non-developer role, inject a concise dynamic instruction block instead:

```markdown
## Role instructions
No dedicated role skill is installed, so perform this role directly:
- Work adversarially: look for correctness, edge cases, missing tests, and project convention violations.
- Produce concrete findings with severity: BLOCKER, WARNING, SUGGESTION.
- Include exact files/lines where possible and a short recommended fix.
```

For missing BMAD skills, tell the user once that they can install them with `npx bmad-method install`, but continue if they decline or do not respond. If the user has another equivalent skill installed, use that instead of BMAD.

When a role has multiple matching skills, inject the most relevant 1-2 skills only. Too many injected skills distract the teammate.

## Common Decomposition Patterns

| Pattern | When to use | Teammates | Dependency |
|---------|-------------|-----------|------------|
| Full closed loop | Default for typical feature/refactor/module work | architect → design-reviewer → developer → code-reviewer → tester | gated chain |
| Dev + Test | Small feature with clear implementation | developer → tester | tester blocked unless acceptance strategy |
| Dev + Docs | Code change needs docs | developer + doc-writer → reviewer | docs often parallel |
| Research + Implement | Unknown library/approach | researcher → architect/developer | implementation blocked by research |
| Multi-module | Independent modules | module-a + module-b + reviewer/tester | modules parallel |
| Dev + Review | Quality-critical code | developer → reviewer | reviewer blocked by developer |
| Full delivery | User asked for commit/PR | dev/review/test → committer | committer blocked by all |

## Teammate Prompt Template

```markdown
你是 {role}。请查看任务列表，认领并完成你的任务。

## 背景
{The teammate cannot see the main conversation. Include the user request, current phase, and why this task exists.}

## 任务
{Concrete goal and expected artifacts. Include file paths when known.}

## 验收标准
- {criterion 1}
- {criterion 2}
- 完成后标记任务为 completed。

## 依赖关系
{State blockedBy tasks or say none. If blocked, wait until dependencies are completed before doing dependent work.}

## 项目规范
{Relevant CLAUDE.md instructions. Include: no unnecessary abstractions, no unwarranted comments, security-safe code, ask on ambiguity. For Python commands use `.venv/bin/python`, not bare python/python3.}

## 可用的 Skill（通过 Skill 工具调用）
{For non-developer roles only. Include only discovered skills. If none, include dynamic role instructions instead.}
```

Developer teammates can omit the Skill section unless a task-specific skill is clearly useful. Non-developer teammates should not omit it; use discovered skills or dynamic instructions.

## Spawn Checklist

Before any Agent calls, output the checklist visibly:

```markdown
Checklist:
- [x] Skill injection: {role} → {discovered skill(s) or dynamic role instructions}
- [x] Self-contained context: {files, goal, acceptance criteria included}
- [x] Project conventions: CLAUDE.md requirements embedded
- [x] Agent type: {needs file writes? default/general-purpose; read-only? Explore; planning-only? Plan}
- [x] Permissions: {local only / external or git push needs user confirmation}
```

Then spawn teammates. Independent Agent calls should be in one message and all should set `run_in_background: true`.

## Team Lead Operating Modes

| Phase | Team Lead behavior | What to avoid |
|-------|--------------------|---------------|
| Decompose / create / spawn | Act proactively: define tasks, dependencies, prompts, and skills | Waiting for the user to design the team |
| Monitor / review / fix loops | Act responsively: inspect teammate output, make decisions, route corrections | Doing implementation work directly in the main session |
| Validate / deliver | Act proactively: verify, summarize, optionally create committer | Declaring done without tests or documented limitations |

Ask the user only when the issue is ambiguous, scope-changing, business-specific, or externally risky. Otherwise drive the loop to the gate condition.

## Closed-Loop Gates

### Design Phase

1. Architect writes or updates the design artifact.
2. Reviewer reviews the latest design artifact.
3. Team Lead evaluates findings:
   - Accept real BLOCKER/WARNING findings.
   - Downgrade or reject findings that conflict with user scope or project constraints.
   - Ask the user only when the decision is ambiguous or scope-changing.
4. Accepted findings must be written back to the design artifact.
5. Review the updated design again.
6. Exit only when the reviewer finds no new accepted BLOCKER/WARNING.

Do not create developer tasks or edit source code before this gate passes.

Design gate anti-patterns:

- Reviewer finds a BLOCKER, then Team Lead immediately asks developer to handle it in code.
- Findings are copied into a chat/task but not merged into the design artifact.
- Team Lead skips another review because the design fix seems obvious.
- Team Lead mentally moves into implementation mode before the design gate passes.

### Implementation Phase

1. Developer implements strictly from the latest design artifact.
2. Code reviewer reviews the latest code.
3. Team Lead accepts/rejects findings.
4. Developer fixes accepted findings.
5. Review again.
6. Exit only when no new accepted code issues remain.

### Test Phase

1. Tester runs the chosen test strategy.
2. If tests fail, Team Lead diagnoses whether failure is code, test, environment, or requirement mismatch.
3. Developer or tester fixes the accepted issue.
4. Run tests again.
5. Exit only when required tests pass or the user explicitly accepts a documented limitation.

## Monitoring Edge Cases

- **Blocked teammate**: verify the dependency task status. Do not manually unblock by ignoring the dependency; complete or correct the upstream task.
- **Idle teammate**: if the teammate completed its work, clean up when the harness provides shutdown tools. If no cleanup tool exists, simply report completion.
- **Interrupted teammate**: continue it with explicit context if continuation is available; otherwise spawn a replacement teammate with the latest artifacts and decisions.
- **Conflicting edits**: Team Lead decides the authoritative version and routes correction work to the appropriate teammate.
- **Unclear finding severity**: ask the user instead of silently downgrading or skipping the issue.

## Tester Strategy

Choose the tester strategy based on the task.

### Strategy A: Requirement-driven / black-box / acceptance first

Use when there is a PRD, design document, API contract, CLI contract, or the user asks for e2e/acceptance testing.

- Tester can start in parallel with developer if there is a stable requirement/design artifact.
- Focus on behavior and contract, not implementation details.
- Test skeletons may fail before implementation exists; that is expected.

Task wording:

```markdown
根据以下需求/设计文档设计并编写验收测试：
- 需求/设计文档：{path}
- 测试类型：acceptance/integration/e2e
- 测试框架：{framework}
- Mock 边界：{what to mock vs real dependencies}

先列出测试用例清单，再编写测试。开发完成后运行全部测试并确保通过。
```

### Strategy B: Implementation-driven / white-box / unit first

Use when there is no independent requirement artifact and tests must be based on code internals.

- Tester should be blocked by developer.
- Focus on branches, boundaries, error paths, and mocks.

Task wording:

```markdown
等开发任务完成后，阅读源码并编写单元测试：
- 源文件：{paths}
- 测试框架：{framework}
- Mock 边界：{dependencies to patch}
- 覆盖要求：{cases}

先读源码理解实现，再设计并编写测试。
```

Use two testers when both acceptance behavior and internal unit coverage are important.

## Committer Prompt

Only create a committer teammate when the user asks for commit/push/PR or approves it. Pushing, opening PRs, commenting externally, or publishing content changes shared state and requires user confirmation.

If the Agent tool supports permission modes in the current environment, use the safest interactive/default mode for committer work. If the schema does not expose such a parameter, do not invent one; express the confirmation requirement in the prompt instead.

With a discovered commit skill:

```markdown
你是代码提交专员。请查看任务列表，认领并完成你的任务。

## 可用的 Skill（通过 Skill 工具调用）
- `/{commit-skill}`：提交、pre-commit、push、PR 相关流程。调用方式：Skill 工具，skill="{commit-skill}"

所有开发/审查/测试任务完成后，调用该 skill 完成交付。涉及 push 或 PR 前必须获得用户确认。
完成后标记任务为 completed。
```

Without a commit skill:

```markdown
你是代码提交专员。所有开发/审查/测试任务完成后：
1. 检查 git status、diff、log。
2. 只 stage 相关文件。
3. 创建新的 commit，不 amend，不跳过 hooks。
4. push 或 PR 前询问用户确认。
完成后标记任务为 completed。
```

## Full Agent Call Example

```markdown
Checklist:
- [x] Skill injection: architect → dynamic architecture instructions because no architecture skill was discovered
- [x] Self-contained context: user request, target files, design artifact path, and acceptance criteria included
- [x] Project conventions: CLAUDE.md requirements embedded
- [x] Agent type: writes design file → default/general-purpose
- [x] Permissions: local file writes only → default
```

```js
Agent({
  description: "Design feature approach",
  prompt: "你是 architect。请查看任务列表，认领并完成你的任务。\n\n## 背景\n...\n\n完成后标记任务为 completed。",
  run_in_background: true
})
```
