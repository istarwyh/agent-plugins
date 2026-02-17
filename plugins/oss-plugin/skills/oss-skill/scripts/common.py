import os
from dataclasses import dataclass
from pathlib import Path

import oss2
from dotenv import load_dotenv

REQUIRED_VARS = [
  "OSS_ENDPOINT",
  "OSS_BUCKET",
  "OSS_ACCESS_KEY_ID",
  "OSS_ACCESS_KEY_SECRET",
]

@dataclass
class OssContext:
  bucket: oss2.Bucket


def load_context() -> OssContext:
  env_path = Path(__file__).resolve().parent.parent / ".env"
  load_dotenv(env_path, override=False)
  missing = [k for k in REQUIRED_VARS if not os.getenv(k)]
  if missing:
    raise RuntimeError(
      "Missing env vars: " + ", ".join(missing) +
      ". Copy .env.example to .env and fill values."
    )
  auth = oss2.Auth(
    os.getenv("OSS_ACCESS_KEY_ID"),
    os.getenv("OSS_ACCESS_KEY_SECRET"),
  )
  bucket = oss2.Bucket(auth, os.getenv("OSS_ENDPOINT"), os.getenv("OSS_BUCKET"))
  return OssContext(bucket=bucket)


def format_size(size: int) -> str:
  units = ["B", "KB", "MB", "GB"]
  val = float(size)
  idx = 0
  while val >= 1024 and idx < len(units) - 1:
    val /= 1024
    idx += 1
  return f"{val:.1f} {units[idx]}"
