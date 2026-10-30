"""Conan scaffold and RPM-bootstrap checks; no SDK or network required."""

import argparse
import ast
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/qt/aurora-qt-setup-project"
SCRIPT = SKILL / "scripts/setup_project.py"
FIXTURE = Path(__file__).parent / "fixtures/qt-cmake"
SPEC = importlib.util.spec_from_file_location("qt_setup", SCRIPT)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class ConanScaffoldTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aurora-conan-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        self.values = {"package": "com.example.AudioTool", "app": "AudioTool", "org": "com.example",
                       "en_name": "Audio Tool", "ru_name": "Аудио", "summary": "Audio tool",
                       "en_description": "An audio tool.", "ru_description": "Аудио.",
                       "version": "0.1.0", "url": ""}
        for fixture, relative in (("CMakeLists.txt", "CMakeLists.txt"), ("application.spec", "rpm/com.example.AudioTool.spec")):
            destination = self.stage / relative
            destination.parent.mkdir(exist_ok=True)
            original = "CMakeLists.txt" if fixture == "CMakeLists.txt" else "rpm/ru.auroraos.ApplicationTemplate.spec"
            destination.write_text(setup.transform(original, (FIXTURE / fixture).read_text(), self.values, "cmake"))
        (self.stage / "README.md").write_text("# Audio Tool\n")

    def test_scaffold_has_empty_recipe_and_matching_rpm_cmake_integration(self):
        setup.add_conan(self.stage, self.values, "2.22.0")
        recipe = ast.parse((self.stage / "conanfile.py").read_text())
        application = next(node for node in recipe.body if isinstance(node, ast.ClassDef))
        requires = next(node.value for node in application.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "requires" for target in node.targets))
        self.assertEqual(ast.literal_eval(requires), ())
        spec = (self.stage / "rpm/com.example.AudioTool.spec").read_text()
        self.assertIn("%build\n%conan_install\n%conan_cmake", spec)
        self.assertIn("%install\n%ninja_install\n%conan_deploy_libraries", spec)
        self.assertIn("%define _cmake_skip_rpath %{nil}", spec)
        self.assertNotIn("%define __requires_exclude ", spec)
        self.assertNotIn("onnxruntime", spec)
        self.assertNotIn("BuildRequires:  conan", spec)
        cmake = (self.stage / "CMakeLists.txt").read_text()
        self.assertIn("project(com.example.AudioTool CXX)", cmake)
        self.assertIn('set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}/lib")', cmake)
        for relative in setup.CONAN_FILES:
            self.assertTrue((self.stage / relative).is_file(), relative)
            self.assertIn(relative, cmake)
        self.assertEqual((self.stage / "rpm/version.config").read_text(), "conan_version=2.22.0\n")
        self.assertTrue(os.access(self.stage / "rpm/load-conan.sh", os.X_OK))

    def test_explicit_distribution_version_is_pinned(self):
        setup.add_conan(self.stage, self.values, "2.23.0")
        self.assertEqual((self.stage / "rpm/version.config").read_text(), "conan_version=2.23.0\n")

    def test_invalid_modes_fail_before_generating_or_downloading(self):
        for arguments in (("--build-system", "qmake", "--conan"),
                          ("--build-system", "cmake", "--conan-version", "2.22.0"),
                          ("--build-system", "cmake", "--conan", "--conan-version", "2.21.0")):
            with self.subTest(arguments=arguments):
                command = [str(SCRIPT), *arguments, "--organization", "com.example", "--app-name", "Demo", "--output", str(self.root / "output")]
                with patch.object(sys, "argv", command), patch.object(setup, "template_source") as source, contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(setup.main(), 1)
                    source.assert_not_called()
                self.assertFalse((self.root / "output").exists())

    def test_changed_template_does_not_publish_partial_output(self):
        output = self.root / "output"
        def write_changed_template(source, stage, *args):
            shutil.copytree(self.stage, stage, dirs_exist_ok=True)
            cmake = stage / "CMakeLists.txt"
            cmake.write_text(cmake.read_text().replace("set(CMAKE_SKIP_RPATH FALSE)", ""))
        command = [str(SCRIPT), "--build-system", "cmake", "--conan", "--organization", "com.example", "--app-name", "AudioTool", "--output", str(output)]
        with patch.object(sys, "argv", command), patch.object(setup, "sdk_tool", return_value=None), patch.object(setup, "template_source", return_value=(FIXTURE, "test")), patch.object(setup, "write_project", side_effect=write_changed_template), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(setup.main(), 1)
        self.assertFalse(output.exists())
        self.assertFalse(list(self.root.glob(".aurora-project-*")))


class ConanBootstrapTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aurora-bootstrap-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.rpm = self.root / "rpm"
        shutil.copytree(setup.CONAN_ASSETS / "rpm", self.rpm)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.tool("uname", "printf 'x86_64\\n'")
        self.tool("awk", "printf '5.2.1\\n'")
        self.env = {**os.environ, "SAILFISH_SDK_SRC1_MOUNT_POINT": str(self.root),
                    "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", "")}
        self.macros = self.root / ".cache/AuroraTools/5/conan/2.22.0/x86_64/rpm-macros"

    def tool(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(0o755)

    def run_bootstrap(self):
        return subprocess.run(["bash", str(self.rpm / "load-conan.sh")], env=self.env, cwd=self.root, capture_output=True, text=True)

    def test_cached_distribution_emits_only_its_rpm_configuration(self):
        self.macros.parent.mkdir(parents=True)
        self.macros.write_text("# fixture\n")
        (self.macros.parent / ".bootstrap-complete").touch()
        self.tool("curl", "exit 99")
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [f"%define __workspace_dir {self.root}", "%define __conan_version 2.22.0", f"%{{load:{self.macros}}}"])

    def test_failed_download_emits_an_rpm_error_instead_of_loading(self):
        self.tool("curl", "exit 22")
        result = self.run_bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("%{error:Failed to download Conan distribution}", result.stdout)
        self.assertNotIn("%{load:", result.stdout)
        self.assertFalse(self.macros.exists())

    def test_missing_configuration_fails_before_download(self):
        (self.rpm / "version.config").unlink()
        self.tool("curl", "exit 99")
        result = self.run_bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("%{error:Missing rpm/version.config}", result.stdout)
        self.assertFalse(self.macros.parent.exists())

    def test_failed_extraction_cannot_publish_a_partial_macros_cache(self):
        self.tool("curl", "exit 0")
        self.tool("tar", 'printf "# partial\\n" > "$4/rpm-macros"\nexit 2')
        for _ in range(2):
            result = self.run_bootstrap()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Failed to extract Conan distribution", result.stdout)
            self.assertNotIn("%{load:", result.stdout)
            self.assertFalse(self.macros.exists())
            self.assertFalse((self.macros.parent / ".bootstrap-complete").exists())


if __name__ == "__main__":
    unittest.main()
