import argparse

from common import load_context


def parse_args(args: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--key", help="Single object key to delete")
  group.add_argument("--prefix", help="Delete all under this prefix")
  return parser.parse_args(args)


def delete_prefix(ctx, prefix: str):
  marker = ""
  deleted = 0
  while True:
    resp = ctx.bucket.list_objects(prefix=prefix, marker=marker)
    keys = [obj.key for obj in resp.object_list]
    if not keys:
      break
    ctx.bucket.batch_delete_objects(keys)
    deleted += len(keys)
    print(f"Deleted batch: {len(keys)} objects")
    if not resp.is_truncated:
      break
    marker = resp.next_marker
  print(f"Deleted total: {deleted}")


def main(args: list[str]):
  opts = parse_args(args)
  ctx = load_context()
  if opts.key:
    ctx.bucket.delete_object(opts.key)
    print(f"Deleted {opts.key}")
  else:
    delete_prefix(ctx, opts.prefix)


if __name__ == "__main__":
  main(sys.argv[1:])
