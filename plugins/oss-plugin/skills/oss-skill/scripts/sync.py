import argparse
import sys
from pathlib import Path

import oss2

from common import load_context


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--src", required=True, help="Local directory to sync")
  parser.add_argument("--prefix", default="", help="OSS prefix destination")
  return parser.parse_args(args)


def should_skip(bucket: oss2.Bucket, key: str, size: int, mtime: float) -> bool:
  try:
    meta = bucket.head_object(key)
  except oss2.exceptions.NoSuchKey:
    return False
  remote_size = meta.content_length
  remote_mtime = meta.last_modified  # seconds since epoch (UTC)
  return remote_size == size and remote_mtime >= int(mtime)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  src_dir = Path(opts.src).expanduser()
  if not src_dir.is_dir():
    raise NotADirectoryError(f"Source must be a directory: {src_dir}")

  prefix = opts.prefix.rstrip("/")
  total = 0
  uploaded = 0
  skipped = 0

  for path in src_dir.rglob("*"):
    if not path.is_file():
      continue
    rel = path.relative_to(src_dir)
    key = f"{prefix}/{rel.as_posix()}" if prefix else rel.as_posix()
    size = path.stat().st_size
    mtime = path.stat().st_mtime
    total += 1

    if should_skip(ctx.bucket, key, size, mtime):
      skipped += 1
      continue

    ctx.bucket.put_object_from_file(key, str(path))
    uploaded += 1

  print(f"Sync complete. scanned={total}, uploaded={uploaded}, skipped={skipped}")


if __name__ == "__main__":
  main(sys.argv[1:])
