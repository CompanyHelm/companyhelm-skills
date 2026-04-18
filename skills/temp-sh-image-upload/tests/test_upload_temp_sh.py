import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "upload_temp_sh.py"


def load_module():
    spec = importlib.util.spec_from_file_location("upload_temp_sh", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TempShImageUploadSkillScriptTest(unittest.TestCase):
    def test_validate_file_accepts_image_extensions(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_directory:
            file_path = Path(temp_directory) / "shot.png"
            file_path.write_bytes(b"fake-png")
            module.validate_file(file_path, allow_non_image=False)

    def test_validate_file_rejects_non_image_extensions(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_directory:
            file_path = Path(temp_directory) / "notes.txt"
            file_path.write_text("hello", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "does not look like an image"):
                module.validate_file(file_path, allow_non_image=False)

    def test_build_markdown_formats_image_link(self):
        module = load_module()
        self.assertEqual(
            module.build_markdown("https://temp.sh/example.png", "screenshot"),
            "![screenshot](https://temp.sh/example.png)",
        )

    def test_comment_on_pr_uses_gh_cli(self):
        module = load_module()
        with patch.object(module, "run") as run_mock:
            module.comment_on_pr("123", "![shot](https://temp.sh/example.png)", "CompanyHelm/companyhelm")

        run_mock.assert_called_once_with(
            [
                "gh",
                "pr",
                "comment",
                "123",
                "--repo",
                "CompanyHelm/companyhelm",
                "--body",
                "![shot](https://temp.sh/example.png)",
            ]
        )


if __name__ == "__main__":
    unittest.main()
