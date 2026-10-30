"""Verify setup handoffs and SDK changes without running or downloading an SDK."""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" / "flutter" /
          "aurora-flutter-setup-project" / "scripts" / "setup_project.py")
SPEC = importlib.util.spec_from_file_location("flutter_setup", SCRIPT)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class FlutterSetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aurora-setup-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "pubspec.yaml").write_text("name: sample_app\n")
        (self.project / "lib").mkdir()
        (self.project / "lib" / "main.dart").write_text("void main() {}\n")
        self.sdk = self.make_sdk("flutter_old")
        self.new_sdk = self.make_sdk("flutter_new")
        self.sfdk = self.root / "sfdk"
        self.sfdk.write_text("#!/bin/sh\nexit 0\n")
        self.sfdk.chmod(0o755)
        self.commands = []
        self.channel = "flutter-aurora-test"

    def make_sdk(self, name):
        sdk = self.root / name
        (sdk / "bin").mkdir(parents=True)
        executable = sdk / "bin" / "flutter"
        executable.write_text("#!/bin/sh\nexit 0\n")
        executable.chmod(0o755)
        return sdk

    def sdk_command(self, command, **kwargs):
        self.commands.append(command)
        if command[1:] == ["--version", "--machine"]:
            data = {"channel": self.channel, "flutterVersion": "test"}
            return subprocess.CompletedProcess(command, 0, json.dumps(data), "")
        self.assertEqual(command[1], "create")
        output = Path(kwargs["cwd"]) if command[-1] == "." else Path(command[-1])
        output.mkdir(parents=True, exist_ok=True)
        pubspec = output / "pubspec.yaml"
        if not pubspec.exists():
            pubspec.write_text("name: sample_app\n")
        return subprocess.CompletedProcess(command, 0)

    def run_setup(self, *arguments, project=None):
        command = [str(SCRIPT), "--output", str(project or self.project), *map(str, arguments)]
        output = io.StringIO()
        with patch.object(sys, "argv", command), patch.object(setup.subprocess, "run", side_effect=self.sdk_command), contextlib.redirect_stdout(output):
            setup.main()
        return json.loads(output.getvalue())

    def write_config(self, **values):
        path = self.project / ".aurora" / "sdk.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(values) + "\n")
        return path

    def create_commands(self):
        return [command for command in self.commands if command[1] == "create"]

    def test_record_only_preserves_application_and_other_settings(self):
        psdk = str(self.root / "independent_psdk")
        config = self.write_config(sfdk=str(self.sfdk), psdk=psdk, custom={"keep": True})
        pubspec = (self.project / "pubspec.yaml").read_bytes()
        main = (self.project / "lib/main.dart").read_bytes()
        (self.project / ".gitignore").write_text("build/\n")
        result = self.run_setup("--existing", "--record-only", "--flutter-sdk", self.sdk)
        data = json.loads(config.read_text())
        self.assertEqual(data, {"flutter": str(self.sdk), "sfdk": str(self.sfdk), "psdk": psdk, "custom": {"keep": True}})
        self.assertEqual((self.project / "pubspec.yaml").read_bytes(), pubspec)
        self.assertEqual((self.project / "lib/main.dart").read_bytes(), main)
        self.assertFalse((self.project / "aurora").exists())
        self.assertEqual(self.create_commands(), [])
        self.assertEqual(result["template"], "record-only")
        self.assertEqual((self.project / ".gitignore").read_text(), "build/\n/.aurora/sdk.json\n")
        self.run_setup("--existing", "--record-only")
        self.assertEqual((self.project / ".gitignore").read_text().count("/.aurora/sdk.json"), 1)

    def test_conflicting_sdk_requires_explicit_replacement(self):
        config = self.write_config(flutter=str(self.sdk), custom="keep")
        original = config.read_bytes()
        with self.assertRaisesRegex(SystemExit, "conflicts"):
            self.run_setup("--existing", "--record-only", "--flutter-sdk", self.new_sdk)
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(self.commands, [])
        self.run_setup("--existing", "--record-only", "--flutter-sdk", self.new_sdk, "--replace-sdk")
        self.assertEqual(json.loads(config.read_text()), {"flutter": str(self.new_sdk), "custom": "keep"})
        self.assertEqual(self.create_commands(), [])

    def test_invalid_replacement_leaves_record_unchanged(self):
        config = self.write_config(flutter=str(self.sdk))
        original = config.read_bytes()
        with self.assertRaisesRegex(SystemExit, "not found"):
            self.run_setup("--existing", "--record-only", "--flutter-sdk", self.root / "missing", "--replace-sdk")
        self.assertEqual(config.read_bytes(), original)

    def test_stock_flutter_replacement_is_rejected(self):
        config = self.write_config(flutter=str(self.sdk))
        original = config.read_bytes()
        self.channel = "stable"
        with self.assertRaisesRegex(SystemExit, "not an Aurora fork"):
            self.run_setup("--existing", "--record-only", "--flutter-sdk", self.new_sdk, "--replace-sdk")
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(self.create_commands(), [])

    def test_explicit_replacement_migrates_legacy_marker(self):
        marker = self.project / ".aurora-flutter-sdk"
        marker.write_text(str(self.sdk) + "\n")
        (self.project / ".gitignore").write_text("build/\n/.aurora-flutter-sdk\n")
        self.run_setup("--existing", "--record-only", "--flutter-sdk", self.new_sdk, "--replace-sdk")
        config = json.loads((self.project / ".aurora/sdk.json").read_text())
        self.assertEqual(config["flutter"], str(self.new_sdk))
        self.assertFalse(marker.exists())
        self.assertEqual((self.project / ".gitignore").read_text(), "build/\n/.aurora/sdk.json\n")
        self.assertEqual(self.create_commands(), [])

    def test_replace_sdk_requires_an_explicit_path(self):
        self.write_config(flutter=str(self.sdk))
        with self.assertRaisesRegex(SystemExit, "requires --flutter-sdk"):
            self.run_setup("--existing", "--record-only", "--replace-sdk")
        self.assertEqual(self.commands, [])

    def test_existing_plugin_respects_selected_implementation(self):
        (self.project / "pubspec.yaml").write_text("name: sample_plugin\nflutter:\n  plugin:\n    platforms: {}\n")
        for implementation in ("plugin", "plugin_qt", "plugin_ffi"):
            with self.subTest(template=implementation):
                self.commands.clear()
                result = self.run_setup("--existing", "--flutter-sdk", self.sdk,
                                        "--template", implementation, "--no-pub")
                command, = self.create_commands()
                self.assertIn("--template=" + implementation, command)
                self.assertIn("--no-pub", command)
                self.assertEqual(result["template"], implementation)

    def test_existing_project_kind_is_inferred_without_template(self):
        result = self.run_setup("--existing", "--flutter-sdk", self.sdk, "--no-pub")
        self.assertEqual(result["template"], "app")
        (self.project / "pubspec.yaml").write_text("name: sample_plugin\nflutter:\n  plugin:\n    platforms: {}\n")
        result = self.run_setup("--existing", "--no-pub")
        self.assertEqual(result["template"], "plugin")

    def test_plugin_detection_uses_yaml_structure(self):
        variants = [
            "name: sample_plugin\nflutter:\n    plugin:\n        platforms: {}\n",
            "name: sample_plugin\nflutter: {plugin: {platforms: {}}}\n",
        ]
        for text in variants:
            with self.subTest(pubspec=text):
                (self.project / "pubspec.yaml").write_text(text)
                result = self.run_setup("--existing", "--flutter-sdk", self.sdk,
                                        "--template", "plugin_ffi", "--no-pub")
                self.assertEqual(result["template"], "plugin_ffi")

    def test_existing_app_cannot_be_converted_to_plugin_by_template_flag(self):
        with self.assertRaisesRegex(SystemExit, "must match"):
            self.run_setup("--existing", "--flutter-sdk", self.sdk, "--template", "plugin_ffi")
        self.assertEqual(self.create_commands(), [])
        self.assertFalse((self.project / ".aurora").exists())

    def test_new_project_allows_git_metadata_but_rejects_other_files(self):
        output = self.root / "new_project"
        (output / ".git").mkdir(parents=True)
        result = self.run_setup("--flutter-sdk", self.sdk, "--no-pub", project=output)
        self.assertEqual(result["template"], "app")
        self.assertTrue((output / ".git").is_dir())
        self.assertTrue((output / "pubspec.yaml").is_file())
        self.commands.clear()
        with self.assertRaisesRegex(SystemExit, "not empty"):
            self.run_setup("--flutter-sdk", self.sdk, project=output)
        self.assertEqual(self.create_commands(), [])

    def test_missing_unrelated_sfdk_does_not_block_flutter_and_malformed_json_is_preserved(self):
        config = self.write_config(flutter=str(self.sdk), sfdk=str(self.root / "missing_sfdk"))
        original = json.loads(config.read_text())
        self.run_setup("--existing", "--record-only")
        self.assertEqual(json.loads(config.read_text()), original)
        config.write_text("{broken")
        with self.assertRaisesRegex(SystemExit, "Invalid JSON"):
            self.run_setup("--existing", "--record-only", "--flutter-sdk", self.sdk)
        self.assertEqual(config.read_text(), "{broken")


if __name__ == "__main__":
    unittest.main()
