---
name: oss-skill
description: >
  Trigger when the user asks to upload, download, list, delete, or sync files
  on Alibaba Cloud OSS, or to generate signed URLs for private objects.
  Operates via Python CLI scripts in the scripts/ directory.
---

# Alibaba Cloud OSS Skill

Manage files on Alibaba Cloud OSS through Python helper scripts.
All commands run via `python scripts/run.py <script> [args...]` from the
skill root directory (`skills/oss-skill/`).

## Prerequisites

1. Python >= 3.9
2. Install deps: `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in credentials:
   `OSS_ENDPOINT`, `OSS_BUCKET`, `OSS_ACCESS_KEY_ID`, `OSS_ACCESS_KEY_SECRET`
4. If any env var is missing, prompt the user before proceeding.

## Commands

| Action | Command |
|--------|---------|
| Upload file | `python scripts/run.py upload.py --src ./file.jpg --key remote/path.jpg` |
| Upload directory | `python scripts/run.py upload.py --src ./dir --prefix remote/prefix` |
| List objects | `python scripts/run.py list_objects.py --prefix prefix/ --max 200` |
| Download | `python scripts/run.py download.py --key remote/path.jpg --dest ./local.jpg` |
| Delete single | `python scripts/run.py delete.py --key remote/path.jpg` |
| Delete by prefix | `python scripts/run.py delete.py --prefix remote/temp/` |
| Signed URL | `python scripts/run.py sign_url.py --key remote/path.jpg --expires 3600` |
| Sync directory | `python scripts/run.py sync.py --src ./dir --prefix remote/prefix` |

## Safety Rules

- **Confirm with the user** before any delete or prefix-delete operation.
- Never commit `.env` files.
- Prefer signed URLs over public-read ACL for private content.

## References

See the `references/` directory for:
- `troubleshooting.md` -- common OSS errors and fixes
- `examples.md` -- detailed usage examples and initialization checklist

## Support

If you encounter any issues with this plugin, please report them following our [Support Guide](../../../SUPPORT.md). Your feedback helps improve the community experience!
