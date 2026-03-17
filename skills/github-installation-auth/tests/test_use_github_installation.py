import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "use_github_installation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("use_github_installation", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class GithubInstallationSkillScriptTest(unittest.TestCase):
    def test_resolve_agent_config_reads_default_json_config(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_directory:
            config_path = Path(temp_directory) / "config.json"
            config_path.write_text(json.dumps({
                "agent_api_url": "http://host.docker.internal:3000/agent/v1",
                "token": "thread-secret",
            }), encoding="utf-8")

            with patch.dict(os.environ, {
                "COMPANYHELM_AGENT_CONFIG_PATH": str(config_path),
            }, clear=False):
                self.assertEqual(
                    module.resolve_agent_config(),
                    ("http://host.docker.internal:3000/agent/v1", "thread-secret"),
                )

    def test_print_installations_formats_human_output(self):
        module = load_module()
        payload = {
            "installations": [
                {
                    "installationId": "123",
                    "repositories": [
                        "CompanyHelm/companyhelm-api",
                        "CompanyHelm/companyhelm-runner",
                    ],
                },
            ],
        }

        with patch("builtins.print") as print_mock:
            module.print_installations(payload, json_output=False)

        printed_lines = [args[0] if args else "" for args, _kwargs in print_mock.call_args_list]
        self.assertIn("Installation 123", printed_lines)
        self.assertIn("  Repositories:", printed_lines)
        self.assertIn("    - CompanyHelm/companyhelm-api", printed_lines)
        self.assertIn("    - CompanyHelm/companyhelm-runner", printed_lines)

    def test_configure_installation_auth_sets_gh_and_git_helpers(self):
        module = load_module()
        recorded_calls = []

        def fake_run(args, **kwargs):
            recorded_calls.append((args, kwargs))
            return subprocess.CompletedProcess(args=args, returncode=0, stdout="")

        with patch.object(module, "agent_request", return_value={
            "installationId": "123",
            "accessToken": "ghs_test_installation_token",
            "accessTokenExpiration": "2026-03-17T06:30:00.000Z",
            "repositories": ["CompanyHelm/companyhelm-runner"],
        }), patch.object(module.shutil, "which", return_value="/usr/bin/gh"), patch.object(subprocess, "run", side_effect=fake_run):
            payload = module.configure_installation_auth("123")

        self.assertEqual(payload["installationId"], "123")
        self.assertTrue(any(call[0] == ["gh", "auth", "login", "--hostname", "github.com", "--with-token"] for call in recorded_calls))
        self.assertTrue(any(call[0] == ["gh", "auth", "setup-git"] for call in recorded_calls))
        self.assertTrue(any(call[0][:4] == ["git", "config", "--global", "--replace-all"] for call in recorded_calls))
        self.assertTrue(any(call[0][:4] == ["git", "config", "--global", "--add"] for call in recorded_calls))


if __name__ == "__main__":
    unittest.main()
