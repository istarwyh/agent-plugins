# Troubleshooting

Common errors when working with Alibaba Cloud OSS:

| Error | Cause | Fix |
|-------|-------|-----|
| AccessDenied | Wrong AccessKey or insufficient bucket ACL | Check AccessKey credentials; confirm endpoint matches bucket region |
| NoSuchBucket | Bucket name or endpoint mismatch | Verify `OSS_BUCKET` and `OSS_ENDPOINT` in `.env` |
| SignatureDoesNotMatch | Whitespace in credentials | Remove leading/trailing whitespace from AccessKey values |
| RequestTimeTooSkewed | System clock drift | Sync system clock (`ntpdate` or equivalent) |
| ModuleNotFoundError | Missing Python dependencies | Run `python -m pip install -r requirements.txt` |
