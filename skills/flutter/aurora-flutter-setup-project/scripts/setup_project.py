#!/usr/bin/env python3
"""Create an Aurora Flutter app/plugin and remember the local Flutter SDK path."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


SDK_FILE = ".aurora-flutter-sdk"
TEMPLATES = ("app", "plugin", "plugin_qt", "plugin_ffi")


def fail(message: str) -> None:
    raise SystemExit(message)


def find_recorded_sdk(project: Path) -> str | None:
    for directory in (project, *project.parents):
        path = directory / SDK_FILE
        if path.is_file():
            return path.read_text().strip()
    return None


def validate_sdk(value: str) -> tuple[Path, dict]:
    sdk = Path(value).expanduser().resolve()
    flutter = sdk if sdk.name == "flutter" and sdk.is_file() else sdk / "bin" / "flutter"
    if not flutter.is_file() or not os.access(flutter, os.X_OK):
        fail(f"Aurora Flutter executable not found: {flutter}")
    sdk = flutter.parent.parent
    result = subprocess.run([str(flutter), "--version", "--machine"], capture_output=True, text=True)
    if result.returncode:
        fail(result.stderr.strip() or f"Failed to identify Flutter at {flutter}")
    try:
        version = json.loads(result.stdout)
    except json.JSONDecodeError:
        fail(f"Flutter did not return machine-readable version data: {flutter}")
    if "aurora" not in str(version.get("channel", "")).lower():
        fail(f"Flutter at {flutter} is not an Aurora fork (channel: {version.get('channel')})")
    return sdk, version


def record_sdk(project: Path, sdk: Path) -> None:
    (project / SDK_FILE).write_text(str(sdk) + "\n")
    ignore = project / ".gitignore"
    old = ignore.read_text() if ignore.exists() else ""
    lines = old.splitlines()
    if f"/{SDK_FILE}" not in lines:
        separator = "" if not old or old.endswith("\n") else "\n"
        ignore.write_text(old + separator + f"/{SDK_FILE}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New project directory or existing Flutter project")
    parser.add_argument("--flutter-sdk", help="Aurora Flutter SDK root or bin/flutter path")
    parser.add_argument("--template", choices=TEMPLATES, default="app")
    parser.add_argument("--org", default="ru.example")
    parser.add_argument("--project-name")
    parser.add_argument("--description")
    parser.add_argument("--existing", action="store_true", help="Add the Aurora platform to an existing Flutter project")
    parser.add_argument("--record-only", action="store_true", help="Only remember the SDK for an existing project")
    parser.add_argument("--no-pub", action="store_true", help="Skip pub get during creation")
    args = parser.parse_args()

    output = args.output.expanduser().resolve()
    sdk_value = args.flutter_sdk or os.environ.get("AURORA_FLUTTER_ROOT") or find_recorded_sdk(output)
    if not sdk_value:
        fail("Provide --flutter-sdk or AURORA_FLUTTER_ROOT; no recorded SDK path was found")
    sdk, version = validate_sdk(sdk_value)

    if args.record_only and not args.existing:
        fail("--record-only requires --existing")
    if args.existing or args.record_only:
        if not (output / "pubspec.yaml").is_file():
            fail(f"Not a Flutter project (pubspec.yaml missing): {output}")
    elif output.exists() and any(output.iterdir()):
        fail(f"Destination is not empty: {output}")
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+", args.org):
        fail("--org must be a reverse-domain identifier such as ru.example")
    if args.project_name and not re.fullmatch(r"[a-z][a-z0-9_]*", args.project_name):
        fail("--project-name must be a Dart package name")

    if not args.record_only:
        command = [str(sdk / "bin" / "flutter"), "create", "--platforms=aurora"]
        if args.existing:
            pubspec = (output / "pubspec.yaml").read_text()
            template = "plugin" if re.search(r"(?m)^[ \t]{2}plugin\s*:", pubspec) else "app"
            command.append(f"--template={template}")
        else:
            command.extend([f"--template={args.template}", f"--org={args.org}"])
            if args.project_name:
                command.append(f"--project-name={args.project_name}")
            if args.description:
                command.append(f"--description={args.description}")
        if args.no_pub:
            command.append("--no-pub")
        command.append("." if args.existing else str(output))
        result = subprocess.run(command, cwd=output if args.existing else None)
        if result.returncode:
            fail(f"Aurora Flutter create failed with exit code {result.returncode}")

    record_sdk(output, sdk)
    print(json.dumps({"project": str(output), "flutter_sdk": str(sdk),
                      "flutter_version": version.get("flutterVersion"),
                      "template": "existing" if args.existing else args.template,
                      "sdk_file": str(output / SDK_FILE)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
