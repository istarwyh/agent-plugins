---
name: swarm-skill
description: >
  Decompose complex tasks into parallel subtasks and coordinate an Agent Team of teammates
  to complete them concurrently. Use when the user describes a multi-part development task
  or explicitly requests task splitting, parallelization, or uses keywords like
  team, swarm, parallel, 拆分, 并行, 分工. Not for single-step tasks
  (typo fix, single file edit, answering a question).
---

# Swarm — Task Decomposition & Parallel Execution

## Environment Check

Run `scripts/check_env.sh` first. Handle by exit code:

- **Exit 0**: Ready. Proceed to skill discovery.
- **Exit 1**: Version too low. Tell user to run `claude update`. **Stop.**
- **Exit 2**: Agent Teams not enabled. Read `~/.claude/settings.json`, add `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` to the `"env"` object (create if absent, preserve existing config), write back. Tell user to **restart Claude Code**. **Stop.**

## Skill Discovery

Build the available skill inventory from two sources:

1. **Session skills**: Parse the `<system-reminder>` in current context for listed skills (name + description).
2. **Filesystem commands**: Run `scripts/discover_skills.sh` to scan `~/.claude/commands/` and `.claude/commands/`.

Merge into a flat list. Only use skills that actually appear — never assume.

> Teammates auto-load the same skills as the lead. No extra config needed.

## Workflow

```
Check env → Discover skills → Decompose → Create team + tasks → Spawn teammates → Monitor → Deliver
```

### 1. Decompose

Analyze the user's request. Split into subtasks that can run in parallel or pipeline.

**Split when:** parallelizable, different expertise, or pipelineable.
**Don't split:** tightly coupled edits, single-file changes, heavy shared context.

See [references/patterns.md](references/patterns.md) for decomposition patterns and role-to-skill matching.

### 2. Create Team & Tasks

Create an Agent Team, then create Tasks. Each Task must be self-contained: clear goal, file paths, completion criteria, project conventions (from CLAUDE.md).

Use `addBlockedBy` for dependencies — blocked teammates wait automatically.

### 3. Spawn Teammates

You **MUST** use the `Agent` tool to spawn teammates. You **MUST NOT** implement code directly in the main session — all implementation work **MUST** be delegated to Agent teammates.

**How to spawn — concrete tool call:**

```
Agent({
  description: "Short summary of this teammate's job",
  prompt: "Full prompt using the template from references/patterns.md",
  run_in_background: true
})
```

**Parallelism rules:**

1. Spawn all independent teammates in a **single message** (multiple Agent tool calls in one response). Do NOT spawn them one by one.
2. Dependent teammates also spawn immediately — they self-wait via `addBlockedBy`.
3. All teammates **MUST** use `run_in_background: true`.

Build prompts using the template in [references/patterns.md](references/patterns.md#teammate-prompt-template). Only inject actually-discovered skills.

**Agent type:** default (omit `subagent_type`) for code, `"Explore"` for research, `"Plan"` for design.

See [references/patterns.md](references/patterns.md#full-agent-call-example) for a complete end-to-end example.

### 4. Monitor & Coordinate

- Verify output on completion; SendMessage corrections if needed
- Resolve conflicts if two teammates edit the same file
- On failure: analyze cause, guide retry via SendMessage

### 5. Commit (optional)

Create a **committer** teammate `addBlockedBy` all dev/test tasks.
Inject commit skill if discovered; otherwise use git directly.
See [references/patterns.md](references/patterns.md#committer-prompt-with-commit-skill) for prompt templates.

### 6. Deliver

1. Run tests to verify changes
2. Summarize each teammate's output to the user
3. Shut down teammates and clean up the team
