#!/usr/bin/env python3
"""Quick, offline fact-check of a Flutter dependency against the checked list."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote


CHECKLIST = Path(__file__).with_name("checked-dependencies.yaml")
SECTIONS = {"aurora_pub", "source_checked_outside_aurora_pub"}


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
    args = parser.parse_args()
    name = args.package
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        parser.error("Invalid Dart package name")

    section = checked_names().get(name)
    report: dict[str, str | bool] = {
        "package": name,
        "allowed": section is not None,
        "status": "checked" if section else "needs_source_review",
    }
    if section:
        report["list_section"] = section
    else:
        encoded = quote(name, safe="")
        report["message"] = "Не уверен: проверь исходники пакета и его транзитивных зависимостей."
        report["package_url"] = f"https://pub.dev/packages/{encoded}"
        report["source_metadata_url"] = f"https://pub.dev/api/packages/{encoded}"
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
