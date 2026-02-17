import argparse

from common import format_size, load_context


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  parser.add_argument("--prefix", default="", help="Prefix filter")
  parser.add_argument("--max", type=int, default=100, help="Max objects")
  return parser.parse_args(args)


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  marker = ""
  seen = 0
  total = 0
  while seen < opts.max:
    resp = ctx.bucket.list_objects(prefix=opts.prefix, marker=marker)
    for obj in resp.object_list:
      print(f"{obj.key}  {format_size(obj.size)}")
      total += obj.size
      seen += 1
      if seen >= opts.max:
        break
    if not resp.is_truncated:
      break
    marker = resp.next_marker
  print(f"Total objects listed: {seen}, total size: {format_size(total)}")


if __name__ == "__main__":
  main(sys.argv[1:])
