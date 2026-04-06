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

1. Spawn independent teammates **in parallel** (single message, multiple Agent calls)
2. Dependent teammates also spawn immediately — they self-wait
3. All use `run_in_background: true`

Build prompts using the template in [references/patterns.md](references/patterns.md#teammate-prompt-template). Only inject actually-discovered skills.

**Agent type:** default for code, `"Explore"` for research, `"Plan"` for design.

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
