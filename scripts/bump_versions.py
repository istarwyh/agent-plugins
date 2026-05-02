from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SEMVER_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")
PLUGIN_MANIFEST_PARTS = (".claude-plugin", "plugin.json")


def bump_patch(version: str) -> str:
  match = SEMVER_PATTERN.match(version)
  if match is None:
    raise ValueError(f"Unsupported version format: {version}")

  major, minor, patch = map(int, match.groups())
  return f"{major}.{minor}.{patch + 1}"


def load_json(path: Path) -> dict[str, object]:
  with path.open("r", encoding="utf-8") as file:
    data = json.load(file)

  if not isinstance(data, dict):
    raise ValueError(f"Expected JSON object in {path}")

  return data


def update_manifest(path: Path) -> bool:
  data = load_json(path)
  version = data.get("version")

  if not isinstance(version, str):
    return False

  data["version"] = bump_patch(version)
  path.write_text(
    f"{json.dumps(data, ensure_ascii=False, indent=2)}\n",
    encoding="utf-8",
  )
  print(f"{path}: {version} -> {data['version']}")
  return True


def get_changed_paths(root: Path, base_ref: str, head_ref: str) -> list[Path]:
  result = subprocess.run(
    ["git", "diff", "--name-only", f"{base_ref}..{head_ref}"],
    cwd=root,
    check=True,
    capture_output=True,
    text=True,
  )

  return [
    Path(line)
    for line in result.stdout.splitlines()
    if line.strip()
  ]


def find_plugin_manifest(path: Path) -> Path | None:
  parts = path.parts

  if len(parts) < 2 or parts[0] != "plugins":
    return None

  return Path(parts[0], parts[1], *PLUGIN_MANIFEST_PARTS)


def find_changed_manifests(root: Path, changed_paths: list[Path]) -> list[Path]:
  manifests = {
    manifest
    for path in changed_paths
    if (manifest := find_plugin_manifest(path)) is not None
  }

  manifests.add(MARKETPLACE_PATH)

  return sorted(path for path in manifests if (root / path).is_file())


def main() -> None:
  root = Path(__file__).resolve().parents[1]
  if len(sys.argv) != 3:
    raise ValueError("Usage: bump_versions.py <base-ref> <head-ref>")

  changed_paths = get_changed_paths(root, sys.argv[1], sys.argv[2])
  manifests = find_changed_manifests(root, changed_paths)

  if not manifests:
    print("No manifests found")
    return

  updated_count = sum(
    1 for manifest in manifests if update_manifest(root / manifest)
  )

  if updated_count == 0:
    raise RuntimeError("No manifest versions were updated")


if __name__ == "__main__":
  main()
