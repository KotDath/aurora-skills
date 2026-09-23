#!/usr/bin/env python3
"""Create an Aurora Flutter app/plugin and remember the local Flutter SDK path."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


SDK_FILE = Path(".aurora/sdk.json")
LEGACY_SDK_FILE = ".aurora-flutter-sdk"
DEFAULT_SFDK = Path.home() / "AuroraOS" / "bin" / "sfdk"
TEMPLATES = ("app", "plugin", "plugin_qt", "plugin_ffi")


def fail(message: str) -> None:
    raise SystemExit(message)


def read_sdk_config(project: Path) -> dict:
    config_path = project / SDK_FILE
    legacy_path = project / LEGACY_SDK_FILE
    config = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text())
        except json.JSONDecodeError:
            fail(f"Invalid JSON in {config_path}")
        if not isinstance(config, dict) or any(
            key in config and (
                not isinstance(config[key], str)
                or not config[key].strip()
                or not Path(config[key]).is_absolute()
            )
            for key in ("flutter", "sfdk")
        ):
            fail(f"Invalid SDK paths in {config_path}")
    if legacy_path.is_file():
        legacy = legacy_path.read_text().strip()
        if config.get("flutter") and Path(config["flutter"]).expanduser().resolve() != Path(legacy).expanduser().resolve():
            fail(f"Conflicting SDK paths in {config_path} and {legacy_path}")
        config.setdefault("flutter", legacy)
    return config


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


def record_sdk(project: Path, sdk: Path, sfdk: Path | None) -> None:
    config_path = project / SDK_FILE
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    config["flutter"] = str(sdk)
    if sfdk:
        config["sfdk"] = str(sfdk)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    legacy_path = project / LEGACY_SDK_FILE
    if legacy_path.is_file():
        legacy_path.unlink()
    ignore = project / ".gitignore"
    old = ignore.read_text() if ignore.exists() else ""
    lines = [line for line in old.splitlines() if line != f"/{LEGACY_SDK_FILE}"]
    if f"/{SDK_FILE.as_posix()}" not in lines:
        lines.append(f"/{SDK_FILE.as_posix()}")
    if lines != old.splitlines():
        ignore.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New project directory or existing Flutter project")
    parser.add_argument("--flutter-sdk", help="Aurora Flutter SDK root or bin/flutter path")
    parser.add_argument("--sfdk", help="Optional Qt SDK root or sfdk executable; defaults to ~/AuroraOS/bin/sfdk when installed")
    parser.add_argument("--template", choices=TEMPLATES, default="app")
    parser.add_argument("--org", default="ru.example")
    parser.add_argument("--project-name")
    parser.add_argument("--description")
    parser.add_argument("--existing", action="store_true", help="Add the Aurora platform to an existing Flutter project")
    parser.add_argument("--record-only", action="store_true", help="Only remember the SDK for an existing project")
    parser.add_argument("--no-pub", action="store_true", help="Skip pub get during creation")
    args = parser.parse_args()

    output = args.output.expanduser().resolve()
    config = read_sdk_config(output)
    recorded_sdk = config.get("flutter")
    if recorded_sdk and args.flutter_sdk:
        supplied = Path(args.flutter_sdk).expanduser().resolve()
        supplied_root = supplied.parent.parent if supplied.name == "flutter" and supplied.is_file() else supplied
        if supplied_root != Path(recorded_sdk).expanduser().resolve():
            fail(f"Requested SDK conflicts with recorded SDK in {output / SDK_FILE}")
    sdk_value = recorded_sdk or args.flutter_sdk
    if not sdk_value:
        fail("Provide --flutter-sdk explicitly; no project Flutter SDK path was found")
    sdk, version = validate_sdk(sdk_value)
    if args.sfdk:
        sfdk = Path(args.sfdk).expanduser().resolve()
        if sfdk.is_dir():
            sfdk = sfdk / "bin" / "sfdk"
        if not sfdk.is_file() or not os.access(sfdk, os.X_OK):
            fail(f"sfdk is not an executable file: {sfdk}")
    elif config.get("sfdk"):
        sfdk = Path(config["sfdk"])
    elif DEFAULT_SFDK.is_file() and os.access(DEFAULT_SFDK, os.X_OK):
        sfdk = DEFAULT_SFDK
    else:
        sfdk = None

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

    record_sdk(output, sdk, sfdk)
    print(json.dumps({"project": str(output), "flutter_sdk": str(sdk),
                      "flutter_version": version.get("flutterVersion"),
                      "template": "existing" if args.existing else args.template,
                      "sdk_file": str(output / SDK_FILE),
                      "sfdk": str(sfdk) if sfdk else None}, ensure_ascii=False))


if __name__ == "__main__":
    main()
