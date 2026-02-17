# Examples and Initialization Checklist

## Initialization Checklist (Agent)

1. Check env vars: `OSS_ENDPOINT`, `OSS_BUCKET`, `OSS_ACCESS_KEY_ID`, `OSS_ACCESS_KEY_SECRET`.
2. If missing, ask user to copy `.env.example` to `.env` and fill values.
3. Ensure Python >= 3.9. If deps missing, run `python -m pip install -r requirements.txt`.
4. For destructive actions (delete / prefix delete), confirm with user.

## Upload a Directory

```bash
# 1. Ensure .env is configured
# 2. Upload recursively
python scripts/run.py upload.py --src ./wedding/assets --prefix wedding/assets
# 3. Script reports count and total size uploaded
```

## Generate a Signed URL

```bash
python scripts/run.py sign_url.py --key wedding/assets/photo1.jpg --expires 7200
# Returns a time-limited URL (2 hours) for the private object
```

## Sync Local Folder to OSS

```bash
python scripts/run.py sync.py --src ./assets --prefix wedding/assets
# Skips objects where remote has same size and newer/equal timestamp
```

## List with Prefix Filter

```bash
python scripts/run.py list_objects.py --prefix wedding/ --max 50
```

## Delete by Prefix (Destructive)

```bash
# Always confirm with user first!
python scripts/run.py delete.py --prefix wedding/temp/
```
