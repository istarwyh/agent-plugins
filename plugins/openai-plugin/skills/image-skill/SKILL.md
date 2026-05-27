---
name: image-skill
description: Use this skill whenever the user wants to generate an image with the OpenAI CLI, mentions OpenAI-compatible image generation, gpt-image-2, cliproxyapi, sk-local-gemini, or asks to test image generation through a local OpenAI CLI proxy. This skill captures the reliable workflow for creating PNG images, remembering the provider after the first successful generation, and avoiding dumped base64 output.
---

# OpenAI CLI Image Skill

Generate images with the local `openai` CLI and save the returned base64 image to a file.

## Default Provider Memory

Provider choice is sticky after the first successful image generation.

Before asking the user, check for a saved default provider:

```bash
DEFAULT_PROVIDER_FILE="${OPENAI_IMAGE_PROVIDER_FILE:-$HOME/.claude/openai-plugin/image-skill-provider.json}"
test -f "$DEFAULT_PROVIDER_FILE" && cat "$DEFAULT_PROVIDER_FILE"
```

If the file exists and the user did not explicitly request a different provider, use that saved provider as the default. Mention it briefly, for example:

```text
Using the saved default provider: cliproxyapi.
```

If the file does not exist, ask the user which provider to use unless they already specified it.

Recommended short question:

```text
Which provider should I use for this image generation? If you use local cliproxyapi, I will default to sk-local-gemini, http://127.0.0.1:8317/v1, and gpt-image-2.
```

After an image is generated and the output file is verified, write the provider to the default provider file. Do this only after success so a failed provider is not remembered.

For `cliproxyapi`, record the complete local defaults:

```bash
DEFAULT_PROVIDER_FILE="${OPENAI_IMAGE_PROVIDER_FILE:-$HOME/.claude/openai-plugin/image-skill-provider.json}"
mkdir -p "$(dirname "$DEFAULT_PROVIDER_FILE")"
cat > "$DEFAULT_PROVIDER_FILE" <<'JSON'
{
  "provider": "cliproxyapi",
  "api_key": "sk-local-gemini",
  "base_url": "http://127.0.0.1:8317/v1",
  "model": "gpt-image-2",
  "size": "1024x1024"
}
JSON
```

For other providers, prefer storing an environment variable name instead of a raw API key:

```json
{
  "provider": "custom-openai-compatible",
  "api_key_env": "OPENAI_API_KEY",
  "base_url": "https://example.com/v1",
  "model": "image-model-name",
  "size": "1024x1024"
}
```

Do not store a real provider API key on disk unless the user explicitly asks for that. If the user changes provider, overwrite the default provider file after the next successful generation.

## Provider Defaults

### cliproxyapi

Use these defaults:

```text
OPENAI_API_KEY=sk-local-gemini
OPENAI_BASE_URL=http://127.0.0.1:8317/v1
OPENAI_IMAGE_MODEL=gpt-image-2
```

This provider depends on the user having a local OpenAI-compatible CLI proxy API installed and running. If `models list` cannot connect to `http://127.0.0.1:8317/v1`, explain that image generation requires this local proxy before continuing. Ask the user to install and configure it first, and point them to this setup reference for reverse proxying Codex: https://mp.weixin.qq.com/s/HY5jXIUyWl6O8ce3e5pjbQ

Do not try to invent a different local proxy endpoint or credentials. After the user finishes setup, rerun the verification command below before generating an image.

This local proxy has been verified with:

```bash
openai --api-key sk-local-gemini \
  --base-url http://127.0.0.1:8317/v1 \
  models list
```

The image endpoint also works through the OpenAI CLI:

```bash
openai --api-key sk-local-gemini \
  --base-url http://127.0.0.1:8317/v1 \
  images generate \
  --model gpt-image-2 \
  --prompt "A white ceramic coffee cup on a wooden table, morning natural light, minimalist product photography, clean background" \
  --size 1024x1024
```

### Other OpenAI-Compatible Providers

Ask for these values before generating:

- API key or environment variable name
- Base URL ending in `/v1`
- Image model name
- Desired size, if not obvious

Do not invent provider credentials.

## Workflow

1. Confirm `openai` exists:

```bash
which openai && openai --version
```

2. Check the provider and model when using a new provider:

```bash
openai --api-key "$OPENAI_API_KEY" \
  --base-url "$OPENAI_BASE_URL" \
  models list
```

3. Generate and decode the image directly to a file. Avoid printing full JSON because image responses contain very large `b64_json` payloads.

For macOS:

```bash
mkdir -p generated/openai-images
openai --api-key "$OPENAI_API_KEY" \
  --base-url "$OPENAI_BASE_URL" \
  images generate \
  --model "$OPENAI_IMAGE_MODEL" \
  --prompt "$PROMPT" \
  --size "${SIZE:-1024x1024}" \
  --format json \
  --transform 'data.0.b64_json' \
  --raw-output \
  | base64 -D > "generated/openai-images/image.png"
```

For Linux, replace `base64 -D` with `base64 -d`.

4. Verify the saved file:

```bash
file generated/openai-images/image.png
```

5. If visual confirmation is useful, open or view the local PNG and report the saved path to the user.

## Recommended Command For cliproxyapi

Use a timestamped filename to avoid overwriting prior generations:

```bash
mkdir -p generated/openai-images
OUT="generated/openai-images/gpt-image-2-$(date +%Y%m%d-%H%M%S).png"
openai --api-key sk-local-gemini \
  --base-url http://127.0.0.1:8317/v1 \
  images generate \
  --model gpt-image-2 \
  --prompt "$PROMPT" \
  --size "${SIZE:-1024x1024}" \
  --format json \
  --transform 'data.0.b64_json' \
  --raw-output \
  | base64 -D > "$OUT"
file "$OUT"
```

## Output Handling

- Save images under `generated/openai-images/` unless the user gives a path.
- Return a local file link or path after successful generation.
- Do not paste `b64_json` into the response.
- Do not run raw `images generate --format json` without `--transform 'data.0.b64_json' --raw-output` unless debugging a provider issue.

## Troubleshooting

- If `models list` fails, check whether the proxy is running and whether the base URL includes `/v1`.
- If `images generate` returns 404, the provider may not implement `/v1/images/generations`; ask whether it supports image generation through another endpoint.
- If the output file is empty or not a PNG, rerun with `--format json` into a temporary file and inspect only top-level fields, not the full base64 payload.
- If generation is slow, wait for the CLI process to finish; local proxy image generation can take tens of seconds.
