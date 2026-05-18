# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development commands

This repository has no root package manager manifest or root test/build command. Most development commands are either root maintenance scripts or plugin-local Python commands.

### Root maintenance

```bash
# Regenerate README.md's Available Skills catalog from SKILL.md frontmatter
python3 scripts/generate_readme.py

# Bump marketplace/plugin manifest patch versions for changed plugins; used by CI
python3 scripts/bump_versions.py <base-ref> <head-ref>
```

`.githooks/pre-commit` runs `python3 scripts/generate_readme.py` and re-stages `README.md` if the hook is configured locally. The GitHub workflow `.github/workflows/bump-versions.yml` runs `scripts/bump_versions.py` on pushes to `master` and commits manifest version updates.

### Xiaohongshu automation engine

```bash
cd plugins/xiaohongshu-plugin/xiaohongshu-skills
uv sync
uv run ruff check .
uv run ruff format .
uv run pytest
uv run pytest tests/test_file.py::test_name
uv run python scripts/cli.py check-login
```

### Social autopilot skill

```bash
cd plugins/social-autopilot-plugin/skills/social-autopilot
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/run.py setup.py
python scripts/run.py pipeline --dry-run
python scripts/run.py status.py
```

### Other script-backed skills

```bash
# OSS skill dispatcher
cd plugins/oss-plugin/skills/oss-skill
python -m pip install -r requirements.txt
python scripts/run.py <upload.py|download.py|list_objects.py|delete.py|sign_url.py|sync.py> [args...]

# Gemini skill dispatcher; run.py creates/uses the skill-local .venv via setup_environment.py
cd plugins/gemini-plugin/skills/gemini-skill
python scripts/run.py <ask_question.py|generate_image.py|notebook_manager.py|auth_manager.py|cleanup_manager.py> [args...]
```

## Architecture overview

This repo is a Claude Code plugin marketplace. The root `.claude-plugin/marketplace.json` lists installable plugins under `plugins/<plugin-name>`, and each plugin has its own `.claude-plugin/plugin.json` manifest.

A typical plugin is organized around Claude Skills:

- `plugins/<plugin>/skills/<skill>/SKILL.md` contains YAML frontmatter (`name`, `description`) plus the instructions Claude loads when the skill triggers.
- `references/` holds optional detailed docs loaded only when needed.
- `scripts/` holds executable helpers used by the skill rather than content Claude should read eagerly.
- `templates/` or resources are plugin-specific assets; for example social autopilot uses `templates/news_card.html`.

The root `scripts/generate_readme.py` scans top-level `plugins/*/skills/*/SKILL.md` files, reads skill frontmatter, and rewrites the README section between `<!-- SKILLS:START -->` and `<!-- SKILLS:END -->`. It intentionally skips the embedded `xiaohongshu-skills/skills` submodule-like directory.

## Major plugin families

### Xiaohongshu plugin

`plugins/xiaohongshu-plugin/skills/*` are the installed skill entry points such as `/xhs-login`, `/xhs-search`, and `/post-to-xhs`. The heavier automation engine lives in `plugins/xiaohongshu-plugin/xiaohongshu-skills/`, which has its own `CLAUDE.md` with more specific rules.

The Xiaohongshu engine uses a two-layer browser automation architecture:

- `extension/` is the Chrome extension that operates in the user's real browser session.
- `scripts/bridge_server.py` and `scripts/xhs/bridge.py` connect CLI commands to the extension.
- `scripts/cli.py` is the JSON-output CLI entry point; exit codes are `0` success, `1` not logged in, `2` error.
- `scripts/xhs/` contains feature modules such as login, search, feed detail, publish, comments, likes/favorites, selectors, and URL constants.

When changing Xiaohongshu publishing behavior, keep the installed skill docs in `plugins/xiaohongshu-plugin/skills/`, references in `plugins/xiaohongshu-plugin/references/`, and the engine under `xiaohongshu-skills/scripts/xhs/` consistent.

### Social autopilot plugin

`plugins/social-autopilot-plugin/skills/social-autopilot` monitors geek news, builds platform-neutral `content_briefs`, creates platform-specific `post_drafts`, generates news card images, then publishes or prepares drafts by channel. The runtime workspace is `~/social-autopilot/` (`config.json`, `.env`, SQLite DB, drafts, cards), not the repo directory.

The dispatcher is `scripts/run.py`. `pipeline` runs poll news -> generate posts -> generate cards -> publish channels. Channel publishing is in `scripts/publish_channels.py`; Xiaohongshu publishing should reuse `xiaohongshu-plugin` instead of duplicating browser automation.

### Lightweight and utility plugins

Some plugins are mostly instruction-only (`chrome-fetch-plugin`, `swarm-plugin`, `wechat-plugin`, `env-config-plugin`). Script-backed utility plugins keep their dependencies in skill-local `requirements.txt` files and are invoked through skill-local dispatchers, not a shared root package.

## Skill authoring conventions

Use `skill-best-practices.md` and `CONTRIBUTING.md` when adding or revising skills. Important repository conventions:

- Skill names in frontmatter must be lowercase letters, numbers, and hyphens.
- Descriptions should state both what the skill does and when it should trigger; they drive skill discovery and README generation.
- Keep `SKILL.md` concise and link one level down to `references/` for detailed procedures.
- When adding a new plugin or skill, update the plugin manifest, root marketplace, and README catalog; prefer regenerating the README with `python3 scripts/generate_readme.py` rather than editing the generated section by hand.
