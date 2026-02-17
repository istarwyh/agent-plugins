import argparse

from common import load_context


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--key", required=True, help="OSS object key")
  parser.add_argument("--expires", type=int, default=3600,
                      help="Expiry seconds")
  return parser.parse_args(args)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  url = ctx.bucket.sign_url("GET", opts.key, opts.expires)
  print(f"Signed URL (expires {opts.expires}s):\n{url}")


if __name__ == "__main__":
  main(sys.argv[1:])
