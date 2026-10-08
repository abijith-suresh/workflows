"""Execute the reusable workflow's shell steps against temporary callers."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = yaml.load(
    (ROOT / ".github/workflows/browser-tests.yml").read_text(), Loader=yaml.BaseLoader
)
JOB = WORKFLOW["jobs"]["browser-tests"]
STEPS = {step["name"]: step for step in JOB["steps"]}


class BrowserWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.caller = Path(self.temp.name)
        self.log = self.caller / "commands.jsonl"
        self.env_file = self.caller / "github-env"
        self.bin = self.caller / "bin"
        self.bin.mkdir()
        self.env = {
            **os.environ,
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "PACKAGE_MANAGER": "bun",
            "BROWSERS": "chromium firefox webkit",
            "GITHUB_ENV": str(self.env_file),
            "COMMAND_LOG": str(self.log),
        }
        # Record argv, and optionally simulate an install/build/test failure.
        self.stub = """#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
with open(os.environ['COMMAND_LOG'], 'a') as log:
    log.write(json.dumps([Path(sys.argv[0]).name, *sys.argv[1:]]) + '\\n')
sys.exit(int(os.environ.get('COMMAND_EXIT', '0')))
"""
        for tool in ("bun", "npm"):
            path = self.bin / tool
            path.write_text(self.stub)
            path.chmod(0o755)

    def run_step(self, name):
        return subprocess.run(
            ["bash", "-eo", "pipefail", "-c", STEPS[name]["run"]],
            cwd=self.caller, env=self.env, capture_output=True, text=True,
        )

    def assert_step(self, name, success=True):
        result = self.run_step(name)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def commands(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_default_inputs_and_permissions(self):
        inputs = WORKFLOW["on"]["workflow_call"]["inputs"]
        self.assertEqual(inputs["package-manager"]["default"], "bun")
        self.assertEqual(inputs["browsers"]["default"], "chromium firefox webkit")
        self.assertEqual(WORKFLOW["permissions"], {})
        self.assertEqual(JOB["permissions"], {"contents": "read"})
        self.assertEqual(JOB["runs-on"], "ubuntu-24.04")
        self.assertEqual(JOB["timeout-minutes"], "15")
        self.assertEqual(
            STEPS["Check out caller repository"]["with"]["persist-credentials"], "false"
        )

    def test_browser_selection(self):
        for selection in ("chromium", "firefox webkit", "chromium\nfirefox\twebkit"):
            with self.subTest(selection=selection):
                self.env["BROWSERS"] = selection
                self.assert_step("Validate browser inputs")

    def test_invalid_browser_inputs(self):
        for selection in ("", " \t\n", "chrome", "--help", "chromium;touch marker", "$(touch marker)"):
            with self.subTest(selection=selection):
                self.env["BROWSERS"] = selection
                self.assert_step("Validate browser inputs", success=False)
                self.assertFalse((self.caller / "marker").exists())
        self.env["BROWSERS"] = "chromium"
        self.env["PACKAGE_MANAGER"] = "pnpm"
        self.assert_step("Validate browser inputs", success=False)

    def test_root_runtime_versions(self):
        for manager, config, expected in (
            ("bun", '[tools]\nbun = "1.4.1"\n', "bun_version=1.4.1\n"),
            ("bun", '[tools]\nbun = "1.4.1"\nnode = "24.20.0"\n',
             "bun_version=1.4.1\nnode_version=24.20.0\n"),
            ("npm", "[tools]\nnode = '24.20.0' # pinned\nnpm = '11.16.0'\n",
             "node_version=24.20.0\nnpm_version=11.16.0\n"),
        ):
            with self.subTest(manager=manager, config=config):
                self.env["PACKAGE_MANAGER"] = manager
                (self.caller / "mise.toml").write_text(config)
                self.env_file.unlink(missing_ok=True)
                self.assert_step("Validate root versions in mise.toml")
                self.assertEqual(self.env_file.read_text(), expected)

    def test_missing_or_invalid_versions(self):
        self.assert_step("Validate root versions in mise.toml", success=False)
        for manager, config in (
            ("bun", '[tools]\nbun = "latest"\n'),
            ("bun", '[tools]\nbun = "1.4"\n'),
            ("bun", '[other]\nbun = "1.4.1"\n'),
            ("bun", '[tools]\nbun = "1.4.1"\nbun = "1.4.2"\n'),
            ("bun", '[tools]\nbun = "1.4.1"\nnode = "lts"\n'),
            ("npm", '[tools]\nnode = "24.20.0"\n'),
            ("npm", '[tools]\nnode = "24.20.0"\nnpm = "11"\n'),
        ):
            with self.subTest(manager=manager, config=config):
                self.env["PACKAGE_MANAGER"] = manager
                (self.caller / "mise.toml").write_text(config)
                self.assert_step("Validate root versions in mise.toml", success=False)

    def test_frozen_installs_and_root_script(self):
        for manager, install in (("bun", ["bun", "install", "--frozen-lockfile"]),
                                 ("npm", ["npm", "ci"])):
            with self.subTest(manager=manager):
                self.env["PACKAGE_MANAGER"] = manager
                self.log.unlink(missing_ok=True)
                self.assert_step("Install dependencies")
                self.assert_step("Check browser behavior")
                self.assertEqual(self.commands(), [install, [manager, "run", "test:browser"]])
                self.env["COMMAND_EXIT"] = "42"
                for step in ("Install dependencies", "Check browser behavior"):
                    self.assertEqual(self.run_step(step).returncode, 42)
                del self.env["COMMAND_EXIT"]

    def test_exact_npm_install(self):
        self.env["NPM_VERSION"] = "11.16.0"
        self.assert_step("Install exact npm version")
        self.assertEqual(self.commands(), [["npm", "install", "--global", "npm@11.16.0"]])

    def test_locked_playwright_cli_and_failure(self):
        self.assert_step("Install browsers and system dependencies", success=False)
        self.assertFalse(self.log.exists(), "Missing CLI must not download an unlocked package")
        cli = self.caller / "node_modules/.bin/playwright"
        cli.parent.mkdir(parents=True)
        cli.write_text(self.stub)
        cli.chmod(0o755)
        self.env["BROWSERS"] = "firefox\nwebkit"
        self.assert_step("Install browsers and system dependencies")
        self.assertEqual(self.commands(), [["playwright", "install", "--with-deps", "firefox", "webkit"]])
        self.env["COMMAND_EXIT"] = "42"
        self.assertEqual(self.run_step("Install browsers and system dependencies").returncode, 42)

    def test_setup_conditions_and_failure_artifacts(self):
        self.assertEqual(STEPS["Set up Bun from root mise.toml"]["if"], "inputs.package-manager == 'bun'")
        self.assertEqual(STEPS["Set up Node.js from root mise.toml"]["if"], "env.node_version != ''")
        self.assertEqual(STEPS["Install exact npm version"]["if"], "inputs.package-manager == 'npm'")
        artifact = STEPS["Upload browser failure artifacts"]
        self.assertEqual(artifact["if"], "failure() && !cancelled()")
        self.assertEqual(artifact["with"]["path"].splitlines(), ["test-results/", "playwright-report/"])
        self.assertEqual(artifact["with"]["if-no-files-found"], "ignore")
        self.assertEqual(artifact["with"]["name"], "${{ inputs.artifact-name }}")
        self.assertEqual(artifact["with"]["retention-days"], "7")


if __name__ == "__main__":
    unittest.main()
