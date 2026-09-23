#!/usr/bin/env python3
"""Build an Aurora Qt project with a selected sfdk target."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


ARCHES = ("aarch64", "armv7hl", "x86_64")
SDK_CONFIG = Path(".aurora/sdk.json")


class BuildError(Exception):
    pass


def project_sdk_config(project: Path) -> dict:
    path = project / SDK_CONFIG
    if not path.is_file():
        return {}
    try:
        config = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise BuildError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(config, dict) or any(
        key in config and (
            not isinstance(config[key], str)
            or not config[key].strip()
            or not Path(config[key]).is_absolute()
        )
        for key in ("flutter", "sfdk")
    ):
        raise BuildError(f"Invalid SDK paths in {path}")
    return config


def record_sfdk(project: Path, sfdk: Path) -> None:
    path = project / SDK_CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    config = project_sdk_config(project)
    if config.get("sfdk") != str(sfdk):
        config["sfdk"] = str(sfdk)
        path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    ignore = project / ".gitignore"
    lines = ignore.read_text().splitlines() if ignore.is_file() else []
    entry = f"/{SDK_CONFIG.as_posix()}"
    if entry not in lines:
        ignore.write_text("\n".join([*lines, entry]) + "\n")


def sfdk_path(value: str | None, project: Path | None = None) -> Path:
    if value:
        path = Path(value).expanduser().resolve()
    else:
        recorded = project_sdk_config(project).get("sfdk") if project else None
        path = Path(recorded).expanduser().resolve() if recorded else Path.home() / "AuroraOS" / "bin" / "sfdk"
    if path.is_dir():
        path = path / "bin" / "sfdk"
    if not value:
        if not path.is_file():
            found = shutil.which("sfdk")
            hint = f" Found in PATH: {found}." if found else ""
            raise BuildError(f"sfdk not found at {path}.{hint} Supply --sfdk PATH.")
    if not path.is_file() or not os.access(path, os.X_OK):
        raise BuildError(f"sfdk is not an executable file: {path}")
    try:
        result = subprocess.run(
            [str(path), "--version"], capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildError(f"Cannot run sfdk at {path}: {exc}") from exc
    if result.returncode:
        raise BuildError(f"sfdk --version failed: {(result.stderr or result.stdout).strip()}")
    return path


def installed_targets(sfdk: Path) -> list[str]:
    try:
        result = subprocess.run(
            [str(sfdk), "--no-pager", "tools", "target", "list"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildError(f"Cannot list sfdk targets: {exc}") from exc
    if result.returncode:
        raise BuildError(f"sfdk tools target list failed: {(result.stderr or result.stdout).strip()}")
    targets = []
    for line in result.stdout.splitlines():
        match = re.match(r"^([A-Za-z0-9_.-]+)\s{2,}(.*)$", line)
        if match and not re.search(r"\bsnapshot\b", match.group(2)):
            targets.append(match.group(1))
    return targets


def select_target(targets: list[str], target: str | None, arch: str | None) -> str:
    if target:
        if target not in targets:
            raise BuildError(f"Target {target!r} is not installed. Available: {', '.join(targets) or '(none)'}")
        if arch and not target.endswith("-" + arch):
            raise BuildError(f"Target {target!r} does not match architecture {arch!r}.")
        return target
    if arch:
        matches = [name for name in targets if name.endswith("-" + arch)]
    else:
        matches = targets
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise BuildError(f"No installed target matches {arch or 'this request'}. Available: {', '.join(targets) or '(none)'}")
    raise BuildError(f"Choose a target explicitly: {', '.join(matches)}")


def project_path(value: str) -> Path:
    project = Path(value).expanduser().resolve()
    if not project.is_dir():
        raise BuildError(f"Project directory does not exist: {project}")
    specs = sorted((project / "rpm").glob("*.spec"))
    if not specs:
        raise BuildError(f"No RPM spec found in {project / 'rpm'}; sfdk build needs an Aurora package project.")
    return project


def run_logged(command: list[str], cwd: Path, log: Path) -> int:
    print("$ " + " ".join(shlex.quote(arg) for arg in command), flush=True)
    with log.open("w", encoding="utf-8") as output:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as exc:
            raise BuildError(f"Cannot start sfdk: {exc}") from exc
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            output.write(line)
        return process.wait()


def built_rpms(log: Path, build_dir: Path, previous: dict[Path, int]) -> list[Path]:
    packages: set[Path] = set()
    with log.open(encoding="utf-8", errors="replace") as output:
        for line in output:
            if line.startswith("Wrote: ") and line.rstrip().endswith(".rpm"):
                path = Path(line.removeprefix("Wrote: ").strip())
                if not path.is_absolute():
                    path = build_dir / path
                if path.is_file():
                    packages.add(path.resolve())
    if packages:
        return sorted(packages)
    return sorted(
        path for path in (build_dir / "RPMS").glob("*.rpm")
        if path not in previous or path.stat().st_mtime_ns != previous[path]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Aurora Qt project directory")
    parser.add_argument("--sfdk", help="Path to sfdk; overrides the project SDK record or defaults to ~/AuroraOS/bin/sfdk")
    parser.add_argument("--target", help="Exact installed target name")
    parser.add_argument("--arch", choices=ARCHES, help="Architecture if it identifies one target")
    parser.add_argument("--build-dir", help="Shadow build directory; defaults to a sibling of the project")
    parser.add_argument("--specfile", help="SPEC file when the project has multiple rpm/*.spec files")
    parser.add_argument("--debug", action="store_true", help="Build with debug information")
    parser.add_argument("--check", action="store_true", help="Run sfdk check after a successful build")
    parser.add_argument("--list-targets", action="store_true", help="List installed targets and exit")
    args = parser.parse_args()

    try:
        project_candidate = Path(args.project).expanduser().resolve()
        sfdk = sfdk_path(args.sfdk, project_candidate if project_candidate.is_dir() else None)
        targets = installed_targets(sfdk)
        if args.list_targets:
            print("sfdk:", sfdk)
            for item in targets:
                print(item)
            return 0
        target = select_target(targets, args.target, args.arch)
        project = project_path(args.project)
        record_sfdk(project, sfdk)
        specs = sorted((project / "rpm").glob("*.spec"))
        if args.specfile:
            spec = Path(args.specfile).expanduser().resolve()
            if spec not in specs:
                raise BuildError(f"Selected SPEC must be one of {project / 'rpm'}/*.spec")
        elif len(specs) > 1:
            raise BuildError("Multiple RPM spec files found; select one with --specfile: " + ", ".join(str(s) for s in specs))
        else:
            spec = None
        build_dir = (
            Path(args.build_dir).expanduser().resolve()
            if args.build_dir
            else project.parent / f"{project.name}.build.{target}"
        )
        if build_dir == project or project in build_dir.parents:
            raise BuildError("Build directory must be outside the source project.")
        if build_dir.is_file():
            raise BuildError(f"Build directory path is a file: {build_dir}")
        if build_dir.exists() and not (build_dir / ".sfdk").is_dir():
            unexpected = {item.name for item in build_dir.iterdir()} - {"sfdk-build.log", "sfdk-check.log"}
            if unexpected:
                raise BuildError(f"Build directory is nonempty and is not an sfdk build tree: {build_dir}")
        build_dir.mkdir(parents=True, exist_ok=True)
        prefix = [str(sfdk), "-c", f"target={target}"]
        if spec:
            prefix.extend(["--specfile", str(spec)])
        command = prefix + ["build"]
        if args.debug:
            command.append("--enable-debug")
        command.append(str(project))
        print(f"Target: {target}\nProject: {project}\nBuild directory: {build_dir}", flush=True)
        build_log = build_dir / "sfdk-build.log"
        previous_rpms = {path: path.stat().st_mtime_ns for path in (build_dir / "RPMS").glob("*.rpm")}
        code = run_logged(command, build_dir, build_log)
        print(f"Build log: {build_log}")
        if code:
            raise BuildError(f"sfdk build failed with exit code {code}")
        rpms = built_rpms(build_log, build_dir, previous_rpms)
        if rpms:
            print("RPM packages:")
            for rpm in rpms:
                print(rpm)
        else:
            print("Build succeeded, but no newly written RPM was found. Inspect the build log and sfdk output settings.")
        if args.check:
            check_log = build_dir / "sfdk-check.log"
            code = run_logged(prefix + ["check"], build_dir, check_log)
            print(f"Check log: {check_log}")
            if code:
                raise BuildError(f"sfdk check failed with exit code {code}; build RPMs remain available")
        return 0
    except BuildError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
