import argparse
import sys
from pathlib import Path

from common import OssContext, load_context, public_url


def ensure_available(ctx: OssContext, keys: list[str], overwrite: bool) -> None:
  if overwrite:
    return
  existing = [key for key in keys if ctx.bucket.object_exists(key)]
  if existing:
    objects = ", ".join(existing)
    raise FileExistsError(
      f"Refusing to overwrite existing OSS object(s): {objects}. "
      "Pass --overwrite only when the user explicitly requested replacement."
    )


def object_url(ctx: OssContext, key: str, mode: str, expires: int) -> str | None:
  if mode == "none":
    return None
  configured_public_url = public_url(key)
  if mode == "public":
    if configured_public_url is None:
      raise RuntimeError(
        "--url-mode public requires OSS_PUBLIC_BASE_URL in the environment or .env"
      )
    return configured_public_url
  if mode == "auto" and configured_public_url is not None:
    return configured_public_url
  return ctx.bucket.sign_url("GET", key, expires)


def upload_file(ctx: OssContext, src: Path, key: str) -> int:
  ctx.bucket.put_object_from_file(key, str(src))
  return src.stat().st_size


def directory_entries(src: Path, prefix: str) -> list[tuple[Path, str]]:
  return [
    (
      path,
      f"{prefix}/{path.relative_to(src).as_posix()}"
      if prefix else path.relative_to(src).as_posix(),
    )
    for path in src.rglob("*")
    if path.is_file()
  ]


def upload_dir(
  ctx: OssContext,
  src: Path,
  prefix: str,
  overwrite: bool,
) -> tuple[list[tuple[str, int]], int]:
  keyed_files = directory_entries(src, prefix)
  ensure_available(ctx, [key for _, key in keyed_files], overwrite)

  total = 0
  uploaded = []
  for path, key in keyed_files:
    size = upload_file(ctx, path, key)
    total += size
    uploaded.append((key, size))
  return uploaded, total


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--src", required=True, help="Local file or directory")
  parser.add_argument("--key", help="OSS object key (for file upload)")
  parser.add_argument("--prefix", help="OSS prefix (for directory upload)")
  parser.add_argument(
    "--overwrite",
    action="store_true",
    help="Replace existing objects; use only after explicit user approval",
  )
  parser.add_argument(
    "--url-mode",
    choices=("none", "auto", "public", "signed"),
    default="none",
    help="Return no URL, a configured public URL, or a signed URL",
  )
  parser.add_argument(
    "--expires",
    type=int,
    default=3600,
    help="Signed URL expiry in seconds",
  )
  return parser.parse_args(args)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  src = Path(opts.src).expanduser()
  if not src.exists():
    raise FileNotFoundError(f"Source not found: {src}")

  if src.is_dir():
    prefix = opts.prefix or src.name
    keyed_files = directory_entries(src, prefix)
    if opts.url_mode == "public" and keyed_files and public_url(keyed_files[0][1]) is None:
      raise RuntimeError(
        "--url-mode public requires OSS_PUBLIC_BASE_URL in the environment or .env"
      )
    uploaded, total = upload_dir(ctx, src, prefix, opts.overwrite)
    print(f"Uploaded {len(uploaded)} files, {total} bytes")
    for key, size in uploaded:
      print(f"Object key: {key} ({size} bytes)")
      url = object_url(ctx, key, opts.url_mode, opts.expires)
      if url:
        print(f"URL: {url}")
  else:
    key = opts.key or src.name
    if opts.url_mode == "public" and public_url(key) is None:
      raise RuntimeError(
        "--url-mode public requires OSS_PUBLIC_BASE_URL in the environment or .env"
      )
    ensure_available(ctx, [key], opts.overwrite)
    size = upload_file(ctx, src, key)
    print(f"Uploaded {key} ({size} bytes)")
    url = object_url(ctx, key, opts.url_mode, opts.expires)
    if url:
      print(f"URL: {url}")


if __name__ == "__main__":
  main(sys.argv[1:])
