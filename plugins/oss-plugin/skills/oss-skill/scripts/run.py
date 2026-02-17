import importlib
import sys
from pathlib import Path

SCRIPTS = {
  "upload.py": "upload",
  "download.py": "download",
  "list_objects.py": "list_objects",
  "delete.py": "delete",
  "sign_url.py": "sign_url",
  "sync.py": "sync",
}


def main():
  if len(sys.argv) < 2:
    print("Usage: python scripts/run.py <script> [args...]")
    sys.exit(1)

  script = sys.argv[1]
  mod_name = SCRIPTS.get(script) or SCRIPTS.get(f"{script}.py")
  if not mod_name:
    print("Unknown script. Choose from:")
    for key in SCRIPTS:
      print(f"  {key}")
    sys.exit(1)

  sys.path.append(str(Path(__file__).resolve().parent))
  module = importlib.import_module(mod_name)
  module.main(sys.argv[2:])

if __name__ == "__main__":
  main()
