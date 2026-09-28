import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "upload.py"

common = types.ModuleType("common")
common.OssContext = object
common.load_context = Mock()
common.public_url = Mock(return_value=None)
sys.modules["common"] = common

spec = importlib.util.spec_from_file_location("oss_upload", SCRIPT)
upload = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(upload)


class UploadTests(unittest.TestCase):
  def test_existing_object_is_rejected_without_overwrite(self):
    ctx = types.SimpleNamespace(bucket=Mock())
    ctx.bucket.object_exists.side_effect = lambda key: key == "taken.png"

    with self.assertRaisesRegex(FileExistsError, "taken.png"):
      upload.ensure_available(ctx, ["new.png", "taken.png"], overwrite=False)

    ctx.bucket.put_object_from_file.assert_not_called()

  def test_explicit_overwrite_skips_existence_check(self):
    ctx = types.SimpleNamespace(bucket=Mock())

    upload.ensure_available(ctx, ["taken.png"], overwrite=True)

    ctx.bucket.object_exists.assert_not_called()

  def test_directory_preflight_happens_before_any_upload(self):
    ctx = types.SimpleNamespace(bucket=Mock())
    ctx.bucket.object_exists.side_effect = [False, True]

    with tempfile.TemporaryDirectory() as temp_dir:
      root = Path(temp_dir)
      (root / "one.png").write_bytes(b"one")
      (root / "two.png").write_bytes(b"two")

      with self.assertRaises(FileExistsError):
        upload.upload_dir(ctx, root, "lesson", overwrite=False)

    ctx.bucket.put_object_from_file.assert_not_called()

  def test_auto_url_prefers_configured_public_base(self):
    ctx = types.SimpleNamespace(bucket=Mock())

    with patch.object(upload, "public_url", return_value="https://cdn.example/a%20b.png"):
      url = upload.object_url(ctx, "a b.png", "auto", 3600)

    self.assertEqual(url, "https://cdn.example/a%20b.png")
    ctx.bucket.sign_url.assert_not_called()

  def test_auto_url_falls_back_to_signed_url(self):
    ctx = types.SimpleNamespace(bucket=Mock())
    ctx.bucket.sign_url.return_value = "https://signed.example/object"

    with patch.object(upload, "public_url", return_value=None):
      url = upload.object_url(ctx, "object.png", "auto", 7200)

    self.assertEqual(url, "https://signed.example/object")
    ctx.bucket.sign_url.assert_called_once_with("GET", "object.png", 7200)

  def test_public_url_mode_is_validated_before_file_upload(self):
    ctx = types.SimpleNamespace(bucket=Mock())

    with tempfile.TemporaryDirectory() as temp_dir:
      image = Path(temp_dir) / "image.png"
      image.write_bytes(b"png")
      with (
        patch.object(upload, "load_context", return_value=ctx),
        patch.object(upload, "public_url", return_value=None),
        self.assertRaisesRegex(RuntimeError, "OSS_PUBLIC_BASE_URL"),
      ):
        upload.main(["--src", str(image), "--url-mode", "public"])

    ctx.bucket.put_object_from_file.assert_not_called()


if __name__ == "__main__":
  unittest.main()
