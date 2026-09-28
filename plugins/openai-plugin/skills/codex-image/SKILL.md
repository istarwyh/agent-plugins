---
name: codex-image
description: Generate images through Codex CLI's built-in image_gen tool with gpt-image-2 and Codex OAuth, optionally uploading successful local results to Alibaba Cloud OSS. Use this skill when the user asks for /codex-image, Codex image generation, gpt-image-2 through Codex OAuth, local image files from Claude Code, or an image-generation flow that explicitly ends with OSS or image-hosting upload.
argument-hint: "[--size <WxH>] [--quality low|medium|high|auto] [--out <path>] [-n <count>] [--upload oss] [--oss-prefix <prefix>] <image prompt>"
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
  - Skill
---

# Codex Image Generation

Generate images with OpenAI's `gpt-image-2` model through Codex CLI. This workflow uses Codex OAuth from `codex login`, so it does not require an OpenAI API key.

## How It Works

```text
User prompt
  -> Claude Code skill
    -> codex exec with workspace-write permission
      -> Codex built-in image_gen tool
        -> ~/.codex/generated_images/<session>/
          -> copied to the requested project path
```

Codex OAuth tokens cannot be used as direct OpenAI REST API keys. Use `codex exec`; it handles authentication internally and exposes the built-in `image_gen` tool.

## Inputs

Parse these arguments from the slash-command input:

| Flag | Values | Default | Meaning |
|------|--------|---------|---------|
| `--size` | `1024x1024`, `1024x1536`, `1536x1024`, `auto` | `1024x1024` | Image dimensions |
| `--quality` | `low`, `medium`, `high`, `auto` | `auto` | Generation quality |
| `--out` | directory path | project root | Directory where images should be saved |
| `-n` | `1` to `10` | `1` | Number of images to generate |
| `--upload` | `oss` | unset | Upload verified images to Alibaba Cloud OSS |
| `--oss-prefix` | OSS key prefix | derived from `--out` | Prefix for uploaded object keys |

All remaining text is the image prompt. If the prompt is empty, ask the user what image to generate before running Codex.

## Workflow

1. Verify Codex CLI is installed:

```bash
which codex 2>/dev/null && codex --version 2>/dev/null || echo "NOT_FOUND"
```

If the result is `NOT_FOUND`, stop and tell the user:

```text
Codex CLI is not installed. Run `npm install -g @openai/codex`, then run `codex login`.
```

2. Verify Codex OAuth login:

```bash
codex login status 2>&1
```

If the user is not logged in, stop and tell the user:

```text
Codex login is required. Run `codex login` in your terminal, then retry this image generation request.
```

3. Resolve output paths.

Use the current Git repository root when available, otherwise use the current directory:

```bash
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
OUT_DIR="$PROJECT_ROOT"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
FILENAME="codex-image-${TIMESTAMP}"
```

If `--out` is provided, resolve it relative to the current directory unless it is already absolute. Create the output directory before generation. Use timestamped filenames and never overwrite existing files:

```text
codex-image-<timestamp>.png
codex-image-<timestamp>-1.png
codex-image-<timestamp>-2.png
```

4. Generate with `codex exec`.

Pass a precise instruction to Codex and let Codex use its built-in `image_gen` tool. Use a 2-minute timeout by default.

```bash
codex exec "Perform these tasks:
1. Use the built-in image_gen tool to generate image files.
2. Prompt: '${PROMPT}'
3. Size: ${SIZE}
4. Quality: ${QUALITY}
5. Count: ${COUNT}
6. Copy each generated image to '${OUT_DIR}'.
7. Use '${FILENAME}.png' for one image. For multiple images, use '${FILENAME}-1.png', '${FILENAME}-2.png', and so on.
8. Do not overwrite an existing file.
9. Print the saved file path and byte size for each image." \
  -C "${PROJECT_ROOT}" \
  -s workspace-write \
  -c 'model_reasoning_effort="medium"' \
  --skip-git-repo-check
```

5. Verify every saved image.

```bash
file "${OUT_DIR}/${FILENAME}.png"
```

For multiple images, verify every suffixed file.

6. Always display every generated PNG inline.

Use the `Read` tool on each generated PNG so the user sees the image inside Claude Code before you summarize anything.

7. If and only if the user explicitly requested OSS/image-hosting upload or
   supplied `--upload oss`, invoke `oss-plugin:oss-skill` with the `Skill` tool.
   Upload each verified local PNG with its filename under `--oss-prefix`. When
   no prefix was supplied, derive a relative, slash-separated prefix from
   `--out`; use `generated/openai-images` when no meaningful relative path is
   available.

   Ask the OSS skill to use its upload command with `--url-mode auto`. Do not
   pass `--overwrite` unless the user explicitly requested replacement. Never
   include OSS credentials in the prompt, transcript, or provider memory.

   If `oss-plugin:oss-skill` is unavailable, its `.env` is incomplete, or an
   upload fails, keep the local generation successful. Report the local files
   and a concise upload error with the setup or retry action.

8. Report concise metadata only after all PNG files have been displayed and any
   requested upload attempt has finished.

## Output Format

After successful generation, verify each PNG with `file`, display each PNG with the `Read` tool, then summarize the result in this shape:

```text
Image generated
Prompt: <prompt used>
Model: gpt-image-2 via Codex CLI
Size: <size>
Quality: <quality>
Count: <count>
Auth: Codex OAuth
Saved files:
- <path> (<byte size>)
OSS uploads: <uploaded count>/<count> (only when requested)
- <local path> -> <object key> -> <public or signed URL>
```

Do not return shell commands, Codex transcripts, generated code, raw JSON, image bytes, or base64 unless debugging a failure.

## Troubleshooting

| Problem | Response |
|---------|----------|
| Codex CLI missing | Ask the user to run `npm install -g @openai/codex`, then `codex login`. |
| OAuth expired or missing | Ask the user to run `codex login` again. |
| No access to `gpt-image-2` | Tell the user to check whether their OpenAI account has image generation access. |
| Timeout | Suggest retrying with `--quality low` or a smaller count. |
| Rate limit | Tell the user to wait and retry later. |
| Trust or workspace error | Keep `--skip-git-repo-check`; if it still fails, ask the user to trust the project in Codex configuration. |
| REST API 401 with OAuth token | Do not retry via REST. OAuth is expected to work through `codex exec`, not direct API calls. |
| OSS skill missing | Keep local results and tell the user to install `oss-plugin`. |
| OSS configuration missing | Keep local results and list only the missing variable names reported by `oss-skill`. |
| OSS object exists | Keep local results; choose a new key or ask whether replacement is intended. |

## Rules

- Use Codex CLI and Codex OAuth for this skill; do not ask for or store OpenAI API keys.
- Do not call the OpenAI REST API with Codex OAuth tokens.
- Do not paste generated image bytes or base64 into the response.
- Do not return shell commands, Codex transcripts, generated code, or raw JSON unless debugging a failure.
- Always verify and then display every generated PNG with the `Read` tool before reporting completion.
- Do not overwrite existing files.
- Save images to the project root by default unless the user gives `--out`.
- Never upload unless the user explicitly requests OSS/image-hosting upload.
- Delegate uploads to `oss-plugin:oss-skill`; do not duplicate its credential or SDK logic.
- Treat OSS upload as best-effort after local generation, never as a reason to discard local results.
- Keep responses concise and include the local file paths after success.
