---
name: meta-skill
description: Generate slash commands with semantic versioning, automatic backups, and changelog tracking. Use when the user wants to create, update, or version-manage Claude Code slash commands.
---

# Slash Command Generator with Version Management

Generate versioned slash command files for Claude Code with automatic backup and changelog tracking.

## Argument Format

`$ARGUMENTS` follows: `<command-name> "<description>" [project|user] [version] [additional-requirements]`

- `command-name`: Name without `/`
- `description`: What the command does
- `scope`: `project` (`.claude/commands/`) or `user` (`~/.claude/commands/`). Default: `user`
- `version`: Semver string. Default: `1.0.0`
- `additional-requirements`: Special features needed

## Workflow

1. **Parse** `$ARGUMENTS` per the format above.
2. **Check if command exists**:
   - If yes: back up as `<name>.v<old-version>.md`, increment version, add changelog entry.
   - If no: create as `v1.0.0`.
3. **Create directory** if missing. Use `versions/` subdirectory for backups if needed.
4. **Generate file** with this YAML frontmatter:
   ```yaml
   ---
   allowed-tools: [appropriate tools]
   description: [command description]
   version: "X.Y.Z"
   created: "YYYY-MM-DD"
   updated: "YYYY-MM-DD"
   changelog:
     - version: "X.Y.Z"
       date: "YYYY-MM-DD"
       changes: ["Initial version" or specific changes]
   ---
   ```
5. **Select allowed-tools** based on requirements:
   - Git: `Bash(git:*)`
   - GitHub CLI: `Bash(gh:*)`
   - Files: `Read(*)`, `Write(*)`, `Edit(*)`
   - Search: `Glob(*)`, `Grep(*)`
   - Web: `WebFetch(*)`, `WebSearch(*)`

## Command Parameters: $ARGUMENTS

## Support

If you encounter any issues with this plugin, please report them following our [Support Guide](../../../SUPPORT.md). Your feedback helps improve the community experience!
