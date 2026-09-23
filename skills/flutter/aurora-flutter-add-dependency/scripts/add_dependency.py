#!/usr/bin/env python3
"""Add a dependency with Aurora Flutter and report its acceptance source."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


SDK_FILE = ".aurora-flutter-sdk"
REGISTRY = "https://sdk-repo.omprussia.ru/sdk/flutter/pub/api/packages/"
CHECKLIST = Path(__file__).resolve().parents[1] / "references" / "checked-dependencies.yaml"


def fail(message: str) -> None:
    raise SystemExit(message)


def checked_names() -> dict[str, set[str]]:
    sections: dict[str, set[str]] = {}
    current: str | None = None
    for raw in CHECKLIST.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            current = line[:-1]
            sections[current] = set()
        elif line.startswith("- ") and current:
            sections[current].add(line[2:].strip())
        else:
            fail(f"Unexpected checklist line: {raw}")
    if set(sections) != {"aurora_pub", "source_checked_outside_aurora_pub"}:
        fail(f"Unexpected checklist sections in {CHECKLIST}")
    return sections


def flutter_binary(project: Path, value: str | None) -> tuple[Path, dict]:
    if not value:
        value = os.environ.get("AURORA_FLUTTER_ROOT")
    if not value:
        for directory in (project, *project.parents):
            marker = directory / SDK_FILE
            if marker.is_file():
                value = marker.read_text().strip()
                break
    if not value:
        fail("No Aurora Flutter SDK path; pass --flutter-sdk or set up the project first")
    sdk = Path(value).expanduser().resolve()
    flutter = sdk if sdk.name == "flutter" and sdk.is_file() else sdk / "bin" / "flutter"
    if not flutter.is_file():
        fail(f"Aurora Flutter executable not found: {flutter}")
    proc = subprocess.run([str(flutter), "--version", "--machine"], capture_output=True, text=True)
    if proc.returncode:
        fail(proc.stderr.strip() or "Could not identify Aurora Flutter")
    try:
        info = json.loads(proc.stdout)
    except json.JSONDecodeError:
        fail("Flutter did not return machine-readable version data")
    if "aurora" not in str(info.get("channel", "")).lower():
        fail(f"Selected Flutter is not an Aurora fork: {flutter}")
    return flutter, info


def registry_package(name: str) -> tuple[bool | None, dict | None]:
    try:
        request = urllib.request.Request(REGISTRY + name, headers={"User-Agent": "aurora-skills/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            return True, json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False, None
        return None, None
    except (OSError, ValueError):
        return None, None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--flutter-sdk")
    parser.add_argument("--version", help="Optional pub version constraint; omit to let Aurora Flutter choose")
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--check-only", action="store_true", help="Classify without changing the project")
    parser.add_argument("--allow-unreviewed", action="store_true", help="Explicitly add a package absent from both sources")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    if not (project / "pubspec.yaml").is_file():
        fail(f"Not a Flutter project: {project}")
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", args.package):
        fail("Invalid Dart package name")
    flutter, sdk_info = flutter_binary(project, args.flutter_sdk)
    names = checked_names()
    live, metadata = registry_package(args.package)
    in_registry_snapshot = args.package in names["aurora_pub"]
    in_source_checked = args.package in names["source_checked_outside_aurora_pub"]
    if live is True or in_registry_snapshot:
        decision = "aurora_pub"
    elif in_source_checked:
        decision = "source_checked"
    else:
        decision = "unreviewed"
    report: dict = {
        "package": args.package,
        "decision": decision,
        "aurora_pub_live": live,
        "aurora_pub_snapshot": in_registry_snapshot,
        "source_checked_snapshot": in_source_checked,
        "flutter_version": sdk_info.get("flutterVersion"),
        "flutter_executable": str(flutter),
    }
    if metadata:
        report["aurora_specific"] = metadata.get("auroraSpecific", False)
        report["aurora_latest"] = metadata.get("latest", {}).get("version")
    if args.check_only:
        print(json.dumps(report, ensure_ascii=False))
        return
    if decision == "unreviewed" and not args.allow_unreviewed:
        fail(f"{args.package} is not in the checked list or Aurora Pub; inspect its sources first")

    target = args.package if not args.version else f"{args.package}:{args.version}"
    if args.dev:
        target = f"dev:{target}"
    command = [str(flutter), "pub", "add", target]
    proc = subprocess.run(command, cwd=project)
    if proc.returncode:
        fail(f"flutter pub add failed with exit code {proc.returncode}")

    deps = subprocess.run([str(flutter), "pub", "deps", "--json"], cwd=project,
                          capture_output=True, text=True)
    if deps.returncode:
        fail(deps.stderr.strip() or "flutter pub deps --json failed")
    graph = json.loads(deps.stdout)
    packages = {package["name"]: package for package in graph["packages"]}
    node = packages.get(args.package)
    if not node:
        fail(f"Added package missing from dependency graph: {args.package}")
    report["resolved_version"] = node["version"]
    closure: set[str] = set()
    pending = [args.package]
    while pending:
        current = pending.pop()
        if current in closure:
            continue
        closure.add(current)
        if current in packages:
            pending.extend(packages[current].get("dependencies", []))
    report["resolved_dependencies"] = []
    for name in sorted(closure):
        package = packages.get(name)
        if not package:
            fail(f"Missing dependency in resolved graph: {name}")
        if package.get("source") == "sdk":
            package_decision = "sdk"
        elif name in names["aurora_pub"]:
            package_decision = "aurora_pub"
        elif name in names["source_checked_outside_aurora_pub"]:
            package_decision = "source_checked"
        else:
            found, _ = registry_package(name)
            package_decision = "aurora_pub" if found is True else "unreviewed"
        report["resolved_dependencies"].append({
            "name": name, "version": package["version"], "decision": package_decision
        })
    report["unreviewed_dependencies"] = [
        package["name"] for package in report["resolved_dependencies"]
        if package["decision"] == "unreviewed"
    ]
    report["source_review_required"] = [
        package["name"] for package in report["resolved_dependencies"]
        if package["decision"] == "source_checked"
    ]
    report["dependency_tree_listed"] = not report["unreviewed_dependencies"]
    report["aurora_pub_policy_accepted"] = decision == "aurora_pub"
    report["lock_file"] = str(project / "aurora_pubspec.lock")
    config_path = project / ".dart_tool" / "package_config.json"
    if config_path.is_file():
        config = json.loads(config_path.read_text())
        configured = next((p for p in config.get("packages", []) if p.get("name") == args.package), None)
        if configured:
            report["resolved_source_uri"] = configured.get("rootUri")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
