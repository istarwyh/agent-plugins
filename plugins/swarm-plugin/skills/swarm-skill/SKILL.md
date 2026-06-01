---
name: swarm-skill
description: >
  Decompose complex development tasks into a parallel Agent Team, create self-contained
  teammate tasks, coordinate closed-loop review/test iterations, and summarize delivery.
  Use whenever the user describes a multi-step development task such as implementing a
  feature with tests, refactoring multiple modules, researching then implementing, or
  explicitly asks for team/swarm/parallel/拆分/并行/分工. Do not use for single-step tasks
  like fixing a typo, reading one file, or answering a simple question.
---

# Swarm — 智能任务拆分与并行执行

把复杂任务拆成多个 teammate 并行完成，由你作为 Team Lead 监控、决策、驱动闭环收敛并交付结果。

## 0. Prerequisites

Run `scripts/check_env.sh` first. The script self-learns successful readiness: after a full check passes once, it records `~/.claude/swarm-skill/agent-teams-ready` and later invocations return ready from that cache by default instead of repeating the environment check. Use `scripts/check_env.sh --force` only when the user asks to troubleshoot, Claude Code was upgraded/downgraded, Agent Teams behavior looks unavailable, or the cached result is suspected to be stale.

Handle by exit code:

- **Exit 0**: Agent Teams is ready. Continue. If output starts with `OK:CACHE`, do not perform extra environment/settings checks unless there is a concrete failure later.
- **Exit 1**: Claude Code version is too low. Tell the user to run `claude update`. Stop.
- **Exit 2**: Agent Teams is not enabled. Read `~/.claude/settings.json`, add `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `env` object, preserve existing config, write back, then tell the user to restart Claude Code. Stop.

BMAD skills are an optional accelerator, not a hard dependency:

- If BMAD skills are present, inject the relevant BMAD skill names into teammate prompts.
- If BMAD is absent, tell the user they can install it with `npx bmad-method install` for stronger architect/reviewer/tester roles.
- If the user does not want to install BMAD now, continue anyway by dynamically writing high-quality teammate instructions for the role.
- If the user has other equivalent skills installed, prefer those instead of BMAD.

## 1. Skill Discovery

Build the available skill inventory from both sources:

1. **Session skills**: parse the current `<system-reminder>` skill list.
2. **Filesystem commands**: run `scripts/discover_skills.sh` to scan `~/.claude/commands/` and `.claude/commands/`.

Only inject skills that actually exist. Never assume a skill is installed just because it appears in examples.

Read `references/patterns.md` when you need role-to-skill matching, prompt templates, tester strategy, or review-loop details.

## 2. Core Workflow

```
用户需求 → 需求理解门禁 → 分析拆分 → 创建 Team + Tasks → 启动 Teammates → 监控协调 → 汇总交付
```

Before creating a team, creating tasks, or spawning teammates, run a visible requirement-understanding gate:

1. Restate the understood goal, scope, expected deliverables, and known constraints in 2-4 concise bullets.
2. Reflect on whether anything is unclear, underspecified, or internally inconsistent, including acceptance criteria, target files/modules, business rules, permissions, test expectations, and delivery format.
3. If there is any real ambiguity, ask targeted questions immediately and stop before decomposition or execution. Prefer 1-4 concrete questions over a broad "please confirm".
4. If the requirement is clear enough to act on, say so briefly and proceed into decomposition. Do not ask generic confirmation questions just to slow down; the point is to surface uncertainty before the swarm starts doing work.

For typical development work, default to the full closed-loop pipeline:

```
需求理解/澄清
  ↓
设计阶段: architect → reviewer → update design → review again until clean
  ↓
实现阶段: developer → code reviewer → fix code → review again until clean
  ↓
测试阶段: tester → fix failures → test again until passing
  ↓
交付: summarize, optionally commit/push/PR if user requested
```

Each phase has a gate. Do not enter the next phase until the gate is clean:

| Transition | Gate |
|------------|------|
| Design → Implementation | reviewer finds no new accepted BLOCKER/WARNING in the latest design artifact |
| Implementation → Test | code review finds no new accepted issue in the latest code |
| Test → Delivery | all required tests pass |

Design artifacts are the single source of truth. If design review finds a problem, update the design artifact and review the updated design again. Do not treat design findings as an implementation TODO list.

The closed-loop pipeline says **what** phases must happen and when they can exit. The Phase 1-9 sections say **how** to execute those phases with tasks, teammates, monitoring, and delivery.

Common gate violations to avoid:

- Do not turn reviewer findings into an implementation TODO list while leaving the design artifact stale.
- Do not enter implementation after a design BLOCKER/WARNING until the design artifact is updated and reviewed again.
- Do not skip re-review because the fix looks small.
- After receiving review findings, remember you are still inside the current phase loop until the gate passes.
- Do not ask the user whether to enter the next phase when the gate itself defines readiness.

## 3. Team Lead Responsibilities

You are the Team Lead.

| Phase | Responsibility | Mode |
|-------|----------------|------|
| Analysis / task creation / spawn | Decompose, create tasks, write prompts, spawn teammates | Proactive |
| Monitoring / review loops | Wait for teammate output, evaluate findings, coordinate fixes | Responsive |
| Validation / delivery | Verify tests, summarize outputs, clean up | Proactive |

Key decision rules:

- Before decomposition or execution, make your understanding visible and ask targeted clarification questions if any requirement is unclear.
- Do **not** directly implement the user's requested code in the main session; delegate implementation to teammates.
- Evaluate reviewer findings independently. Accept, reject, downgrade, or upgrade findings with reasons.
- Resolve conflicts between teammates.
- Ask the user when a decision is genuinely ambiguous, scope-changing, business-specific, or requires external authorization.
- Do not guess, skip, or silently choose on uncertain technical choices, business logic, or finding severity downgrades.
- Drive each phase to convergence; the exit condition is clean review/tests, not Team Lead intuition.

## 4. Decompose

Split when work is parallelizable, requires distinct expertise, or forms a useful pipeline. Do not split tightly coupled single-file edits or tiny changes.

Good default teammate count is 2-4. More than 5 usually costs more coordination than it saves.

Common patterns:

| Pattern | Teammates | Dependency |
|---------|-----------|------------|
| Full development loop | architect → design-reviewer → developer → code-reviewer → tester | gated chain |
| Dev + Test | developer → tester | tester blocked by developer unless using acceptance-test strategy |
| Research + Implement | researcher → developer | developer blocked by researcher |
| Multi-module | module-a + module-b + reviewer/tester | modules parallel, review/test after |
| Docs sync | developer + doc-writer → reviewer | docs can often run parallel |

## 5. Create Team and Tasks

If Agent Teams tools are available, create a team first, then create one Task per teammate. If only Task tools are available in the current harness, use the available Task tools and Agent teammates without a separate TeamCreate call.

Each Task must be self-contained:

- Goal and expected artifact.
- Relevant file paths and project context.
- Completion criteria.
- Dependencies via `addBlockedBy`.
- Project conventions from CLAUDE.md.
- For Python projects, tell teammates to use `.venv/bin/python` instead of bare `python`/`python3`.

## 6. Spawn Teammates

You **MUST** use the `Agent` tool to spawn teammates. All teammates use `run_in_background: true`.

Spawn all independent teammates in a single assistant message with multiple Agent calls. Dependent teammates may also be spawned immediately; they should wait on blocked tasks.

Before every spawn, write this visible checklist in the response text:

```markdown
Checklist:
- [x] Skill injection: {role} → {discovered skill or dynamic instructions}
- [x] Self-contained context: {files, goal, acceptance criteria included}
- [x] Project conventions: CLAUDE.md requirements embedded
- [x] Agent type: {needs file writes? general-purpose : Explore/Plan}
- [x] Permissions: {default local / needs user confirmation for external or git push}
```

Agent type selection:

| Need | Agent type |
|------|------------|
| Writes or edits files, including design/review docs | default/general-purpose |
| Read-only search or codebase exploration | `subagent_type: "Explore"` |
| Planning only and no file output | `subagent_type: "Plan"` |

If unsure, use default/general-purpose.

Use the template and mapping in `references/patterns.md` to write prompts. Non-developer teammates should receive either discovered role skills or explicit dynamic role instructions.

## 7. Monitor and Iterate

When teammates complete:

1. Inspect their output.
2. Decide whether the phase gate passes.
3. If not, create/update the needed task and send the responsible teammate a correction prompt if the harness supports continuing agents; otherwise spawn a new teammate with the correction context.
4. Repeat until the phase gate passes.

When teammates are blocked, idle, or interrupted:

- If blocked, check whether the blocking task is truly incomplete; unblock only by completing or correcting the dependency.
- If idle after completion, clean up or leave it alone depending on available harness controls.
- If interrupted, resume with explicit context if the harness supports continuation; otherwise spawn a replacement teammate.
- If the harness lacks team shutdown or message-continuation tools, document the state and proceed with available Task/Agent tools.

Review loop:

- Reviewer findings are inputs to Team Lead decision-making, not automatic commands.
- Accepted design findings must be written back to the design artifact before another design review.
- Accepted code findings must be fixed by developer before another code review.
- Accepted test failures must be fixed and tested again.

If a teammate fails, diagnose the cause and provide corrective instructions. If teammates conflict on the same file, resolve the conflict explicitly.

## 8. Commit / Push / PR

Only commit, push, or create a PR if the user requested it or explicitly approves it.

For delivery with git:

- Create a committer teammate blocked by all dev/review/test tasks.
- Inject an available commit/push skill if discovered.
- If no commit skill exists, instruct the committer to follow the repository's git workflow and ask before push.
- External or shared-state actions require user confirmation.
- If an Agent permission mode feature exists, use the safest interactive/default mode for committers; do not assume a tool parameter exists unless it is available in the current schema.

## 9. Deliver

At the end:

1. Run or verify the relevant tests.
2. Summarize each teammate's output.
3. Note any limitations, skipped optional skills, or user decisions.
4. Clean up idle teammates/team if the harness provides cleanup tools.

Use this summary format:

```markdown
所有任务完成。

| Teammate | 任务 | 产出 |
|----------|------|------|
| architect | 设计方案 | ... |
| developer | 实现代码 | ... |
| tester | 测试验证 | ... |

验证：...
注意事项：...
```
