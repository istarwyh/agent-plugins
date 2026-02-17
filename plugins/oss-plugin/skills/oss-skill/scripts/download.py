import argparse
from pathlib import Path

from common import load_context


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--key", required=True, help="OSS object key")
  parser.add_argument("--dest", help="Local destination path")
  return parser.parse_args(args)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  dest = Path(opts.dest or Path(opts.key).name).expanduser()
  dest.parent.mkdir(parents=True, exist_ok=True)
  ctx.bucket.get_object_to_file(opts.key, str(dest))
  print(f"Downloaded {opts.key} -> {dest}")


if __name__ == "__main__":
  main(sys.argv[1:])
