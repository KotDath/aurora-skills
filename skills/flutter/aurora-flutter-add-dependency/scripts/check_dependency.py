#!/usr/bin/env python3
"""Check package presence on Aurora Pub; source review remains a separate step."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CHECKLIST = Path(__file__).with_name("checked-dependencies.yaml")
SECTIONS = {"aurora_pub", "source_checked_outside_aurora_pub"}
AURORA_PACKAGE_API = "https://sdk-repo.omprussia.ru/sdk/flutter/pub/api/packages/"


def checked_names() -> dict[str, str]:
    names: dict[str, str] = {}
    section: str | None = None
    seen_sections: set[str] = set()
    for number, raw in enumerate(CHECKLIST.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and not line.startswith("- "):
            section = line[:-1]
            if section not in SECTIONS or section in seen_sections:
                raise ValueError(f"Invalid section at line {number}: {section}")
            seen_sections.add(section)
        elif line.startswith("- ") and section:
            name = line[2:].strip()
            if not re.fullmatch(r"[a-z_][a-z0-9_]*", name) or name in names:
                raise ValueError(f"Invalid or duplicate package at line {number}: {name}")
            names[name] = section
        else:
            raise ValueError(f"Invalid checklist entry at line {number}: {raw}")
    if seen_sections != SECTIONS:
        raise ValueError(f"Missing checklist section: {SECTIONS - seen_sections}")
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, help="Dart package name to check")
    parser.add_argument("--offline", action="store_true", help="Show historical list evidence only; does not grant admission")
    args = parser.parse_args()
    name = args.package
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        parser.error("Invalid Dart package name")

    section = checked_names().get(name)
    encoded = quote(name, safe="")
    report = {
        "package": name,
        "allowed": None,
        "status": "unverified_offline",
        "aurora_metadata_url": AURORA_PACKAGE_API + encoded,
    }
    if section:
        report["list_section"] = section
    if not args.offline:
        try:
            request = Request(report["aurora_metadata_url"], headers={"Accept": "application/json"})
            with urlopen(request, timeout=20) as response:
                metadata = json.load(response)
            if not isinstance(metadata, dict) or metadata.get("name") != name:
                raise ValueError("Package metadata name mismatch")
            versions = metadata.get("versions", [])
            latest = metadata.get("latest", {})
            if not isinstance(versions, list) or not isinstance(latest, dict):
                raise ValueError("Invalid version metadata")
            available = [v["version"] for v in versions if isinstance(v, dict) and isinstance(v.get("version"), str)]
            if isinstance(latest.get("version"), str) and latest["version"] not in available:
                available.append(latest["version"])
            if not available:
                raise ValueError("No package versions in response")
            report.update(allowed=True, status="available_on_aurora_server", versions=available)
        except HTTPError as exc:
            if exc.code == 404:
                report.update(allowed=False, status="needs_source_review")
            else:
                report.update(status="server_check_failed", error=f"HTTP {exc.code}")
        except (URLError, OSError, ValueError) as exc:
            report.update(status="server_check_failed", error=type(exc).__name__)
    if report["status"] == "needs_source_review":
        report["message"] = "Пакет не найден на сервере Авроры. Использовать можно только после проверки выбранной версии и транзитивных зависимостей: без native-кода и TargetPlatform."
        report["package_url"] = f"https://pub.dev/packages/{encoded}"
        report["source_metadata_url"] = f"https://pub.dev/api/packages/{encoded}"
    elif report["allowed"] is None:
        report["message"] = "Наличие пакета не подтверждено; локальный список не заменяет проверку сервера."
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
