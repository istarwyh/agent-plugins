import argparse
from pathlib import Path

from common import OssContext, load_context


def upload_file(ctx: OssContext, src: Path, key: str) -> int:
  ctx.bucket.put_object_from_file(key, str(src))
  return src.stat().st_size


def upload_dir(ctx: OssContext, src: Path, prefix: str) -> tuple[int, int]:
  total = 0
  count = 0
  for path in src.rglob("*"):
    if path.is_file():
      rel = path.relative_to(src)
      key = f"{prefix}/{rel.as_posix()}" if prefix else rel.as_posix()
      total += upload_file(ctx, path, key)
      count += 1
  return count, total


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--src", required=True, help="Local file or directory")
  parser.add_argument("--key", help="OSS object key (for file upload)")
  parser.add_argument("--prefix", help="OSS prefix (for directory upload)")
  return parser.parse_args(args)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  src = Path(opts.src).expanduser()
  if not src.exists():
    raise FileNotFoundError(f"Source not found: {src}")

  if src.is_dir():
    prefix = opts.prefix or src.name
    count, total = upload_dir(ctx, src, prefix)
    print(f"Uploaded {count} files, {total} bytes")
  else:
    key = opts.key or src.name
    size = upload_file(ctx, src, key)
    print(f"Uploaded {key} ({size} bytes)")


if __name__ == "__main__":
  main(sys.argv[1:])
