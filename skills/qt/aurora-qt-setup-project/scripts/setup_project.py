#!/usr/bin/env python3
"""Create an Aurora OS Qt application from ApplicationTemplate."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse


TEMPLATE_URL = "https://hub.mos.ru/auroraos/demos/ApplicationTemplate.git"
SOURCE_PACKAGE = "ru.auroraos.ApplicationTemplate"
BRANCHES = {"qmake": "example", "cmake": "cmake-version"}
ICON_SIZES = ("86x86", "108x108", "128x128", "172x172")
COMMON_FILES = (
    ".gitignore",
    "AUTHORS.md",
    "LICENSE.BSD-3-Clause.md",
    "qml/ApplicationTemplate.qml",
    "qml/cover/DefaultCoverPage.qml",
    "qml/icons/ApplicationTemplate.svg",
    "qml/pages/AboutPage.qml",
    "qml/pages/MainPage.qml",
    "rpm/ru.auroraos.ApplicationTemplate.spec",
    "ru.auroraos.ApplicationTemplate.desktop",
    "src/main.cpp",
)
BUILD_FILES = {
    "qmake": (
        "ru.auroraos.ApplicationTemplate.pro",
        "translations/ru.auroraos.ApplicationTemplate.ts",
        "translations/ru.auroraos.ApplicationTemplate-ru.ts",
    ),
    "cmake": (
        "CMakeLists.txt",
        "translations/ApplicationTemplate-en.ts",
        "translations/ApplicationTemplate-ru.ts",
    ),
}


class SetupError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-system", choices=BRANCHES, required=True)
    parser.add_argument("--organization", required=True, help="Reverse-domain ID, e.g. ru.example")
    parser.add_argument("--app-name", required=True, help="Code name, e.g. DotaCompanion")
    parser.add_argument("--output", type=Path, default=Path("."))
    parser.add_argument("--display-name-en")
    parser.add_argument("--display-name-ru")
    parser.add_argument("--summary", help="One-line RPM summary; defaults to the English display name")
    parser.add_argument("--description-en")
    parser.add_argument("--description-ru")
    parser.add_argument("--version", help="RPM version; defaults to 0.1.0")
    parser.add_argument("--url", help="Project URL for the RPM spec")
    parser.add_argument("--template-dir", type=Path, help="Use an existing checkout instead of downloading (offline/testing)")
    return parser.parse_args()


def one_line(value: str, label: str) -> str:
    if not value or value != value.strip() or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise SetupError(f"{label} must be nonempty, trimmed, and one line")
    if "\\" in value:
        raise SetupError(f"{label} cannot contain a backslash")
    return value


def validate(args: argparse.Namespace) -> tuple[str, Path, dict[str, str]]:
    org = one_line(args.organization, "organization")
    app = one_line(args.app_name, "app name")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)+", org):
        raise SetupError("organization must be a reverse-domain identifier such as ru.example")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", app):
        raise SetupError("app name must start with a Latin letter and contain only Latin letters and digits")
    version = args.version or "0.1.0"
    if not re.fullmatch(r"[0-9][A-Za-z0-9._+~]*", version):
        raise SetupError("version must be a valid RPM version without spaces or dashes")
    if args.url:
        one_line(args.url, "url")
        parsed = urlparse(args.url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or " " in args.url:
            raise SetupError("url must be an HTTP or HTTPS URL")

    output = args.output.expanduser().resolve()
    if not output.parent.is_dir():
        raise SetupError(f"output parent does not exist: {output.parent}")
    if output.exists():
        if not output.is_dir():
            raise SetupError(f"output is not a directory: {output}")
        existing = {entry.name for entry in output.iterdir()}
        if existing - {".git"}:
            raise SetupError(f"output is not empty: {output}; only an existing .git entry is allowed")

    en_name = one_line(args.display_name_en or app, "English display name")
    ru_name = one_line(args.display_name_ru or en_name, "Russian display name")
    values = {
        "org": org,
        "app": app,
        "package": f"{org}.{app}",
        "en_name": en_name,
        "ru_name": ru_name,
        "summary": one_line(args.summary or en_name, "summary"),
        "en_description": one_line(args.description_en or f"{en_name} for Aurora OS.", "English description"),
        "ru_description": one_line(args.description_ru or f"{ru_name} для ОС Аврора.", "Russian description"),
        "version": version,
        "url": args.url or "",
    }
    return BRANCHES[args.build_system], output, values


def git_output(*command: str) -> str:
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def template_source(args: argparse.Namespace, branch: str, temp: Path) -> tuple[Path, str]:
    if args.template_dir:
        source = args.template_dir.expanduser().resolve()
        if not source.is_dir():
            raise SetupError(f"template directory does not exist: {source}")
    else:
        source = temp / "template"
        git_output("git", "clone", "--depth", "1", "--single-branch", "--branch", branch, TEMPLATE_URL, str(source))
    try:
        commit = git_output("git", "-C", str(source), "rev-parse", "HEAD")
    except subprocess.CalledProcessError:
        commit = "unknown (local template directory)"
    return source, commit


def mapped_path(path: str, values: dict[str, str]) -> Path:
    return Path(path.replace(SOURCE_PACKAGE, values["package"]).replace("ApplicationTemplate", values["app"]))


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SetupError(f"upstream template changed: expected one {label}, found {count}")
    return text.replace(old, new)


def replace_line(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(key)}[^\n]*$", re.MULTILINE)
    text, count = pattern.subn(lambda _: f"{key}{value}", text)
    if count != 1:
        raise SetupError(f"upstream template changed: expected one line beginning {key!r}, found {count}")
    return text


def xml_description(text: str, description: str) -> str:
    pattern = re.compile(r"(<source>#descriptionText</source>\s*<translation>).*?(</translation>)", re.DOTALL)
    markup = f"<p>{html.escape(description)}</p>"
    text, count = pattern.subn(lambda m: m.group(1) + html.escape(markup) + m.group(2), text)
    if count != 1:
        raise SetupError(f"upstream template changed: expected one description translation, found {count}")
    return text


def transform(relative: str, text: str, values: dict[str, str], build_system: str) -> str:
    package, app, org = values["package"], values["app"], values["org"]
    text = text.replace(SOURCE_PACKAGE, package)
    text = text.replace("ApplicationTemplate", app)
    if relative == "src/main.cpp":
        text = replace_once(text, 'QStringLiteral("ru.auroraos")', f'QStringLiteral("{org}")', "organization in main.cpp")
    if relative.endswith(".desktop"):
        text = replace_line(text, "Name=", values["en_name"])
        text = replace_line(text, "Name[ru]=", values["ru_name"])
        text = replace_line(text, "OrganizationName=", org)
        text = replace_line(text, "ApplicationName=", app)
    if relative.endswith(".spec"):
        text = replace_line(text, "Summary:", f"    {values['summary'].replace('%', '%%')}")
        text = replace_line(text, "Version:", f"    {values['version']}")
        text = replace_once(text, "Aurora OS Application Template.", values["en_description"].replace("%", "%%"), "spec description")
        if values["url"]:
            text = replace_line(text, "URL:", f"        {values['url'].replace('%', '%%')}")
        else:
            text, count = re.subn(r"^URL:[^\n]*\n", "", text, count=1, flags=re.MULTILINE)
            if count != 1:
                raise SetupError("upstream template changed: expected one URL line")
        if build_system == "cmake":
            text = replace_once(text, "BuildRequires:  pkgconfig(Qt5Quick)\n", "BuildRequires:  pkgconfig(Qt5Quick)\nBuildRequires:  ninja\n", "CMake build requirements")
    if relative.endswith(".pro"):
        pattern = re.compile(r"DISTFILES \+= \\\n.*?\n\nAURORAAPP_ICONS", re.DOTALL)
        replacement = "DISTFILES += \\\n    rpm/" + package + ".spec \\\n    AUTHORS.md \\\n    LICENSE.BSD-3-Clause.md \\\n    README.md\n\nAURORAAPP_ICONS"
        text, count = pattern.subn(lambda _: replacement, text)
        if count != 1:
            raise SetupError("upstream template changed: qmake DISTFILES block")
    if relative in ("qml/cover/DefaultCoverPage.qml", "qml/pages/MainPage.qml"):
        text = replace_once(text, 'qsTr("Application Template")', "qsTr(" + json.dumps(values["en_name"], ensure_ascii=False) + ")", "QML application title")
    if relative.endswith(".ts"):
        source = f"<source>{html.escape(values['en_name'])}</source>"
        if text.count("<source>Application Template</source>") != 2:
            raise SetupError("upstream template changed: expected two title translations")
        text = text.replace("<source>Application Template</source>", source)
        language = "ru" if relative.endswith("-ru.ts") else "en"
        if language == "ru":
            if text.count("<translation>Шаблон приложения</translation>") != 2:
                raise SetupError("upstream template changed: Russian title translations")
            text = text.replace("<translation>Шаблон приложения</translation>", f"<translation>{html.escape(values['ru_name'])}</translation>")
        else:
            if text.count("<translation>Application Template</translation>") != 2:
                raise SetupError("upstream template changed: English title translations")
            text = text.replace("<translation>Application Template</translation>", f"<translation>{html.escape(values['en_name'])}</translation>")
        text = xml_description(text, values[f"{language}_description"])
    return text


def write_project(source: Path, stage: Path, build_system: str, values: dict[str, str], branch: str, commit: str) -> None:
    relative_files = list(COMMON_FILES) + list(BUILD_FILES[build_system])
    relative_files += [f"icons/{size}/{SOURCE_PACKAGE}.png" for size in ICON_SIZES]
    for relative in relative_files:
        original = source / relative
        if not original.is_file():
            raise SetupError(f"upstream template changed: missing {relative}")
        target = stage / mapped_path(relative, values)
        target.parent.mkdir(parents=True, exist_ok=True)
        if original.suffix == ".png":
            shutil.copy2(original, target)
        else:
            target.write_text(transform(relative, original.read_text(encoding="utf-8"), values, build_system), encoding="utf-8")
    readme = (
        f"# {values['en_name']}\n\n"
        f"{values['en_description']}\n\n"
        f"Aurora OS Qt/QML application. Build system: {build_system}. Package ID: `{values['package']}`.\n\n"
        "## Template origin\n\n"
        f"Based on [ApplicationTemplate]({TEMPLATE_URL.removesuffix('.git')}) "
        f"branch `{branch}`, commit `{commit}`. Original authors are listed in `AUTHORS.md`; "
        "the source license is in `LICENSE.BSD-3-Clause.md`. "
        "The included Aurora icons are placeholders to replace before publishing.\n"
    )
    (stage / "README.md").write_text(readme, encoding="utf-8")


def check_project(stage: Path, build_system: str, values: dict[str, str]) -> None:
    package, app = values["package"], values["app"]
    expected = [mapped_path(path, values) for path in COMMON_FILES + BUILD_FILES[build_system]]
    expected += [Path(f"icons/{size}/{package}.png") for size in ICON_SIZES]
    expected.append(Path("README.md"))
    for relative in expected:
        if not (stage / relative).is_file():
            raise SetupError(f"generated project is missing {relative}")
    for path in stage.rglob("*"):
        if not path.is_file() or path.name in ("README.md", "AUTHORS.md", "LICENSE.BSD-3-Clause.md") or path.suffix == ".png":
            continue
        content = path.read_text(encoding="utf-8")
        if any(stale in content for stale in ("ru.auroraos", "ApplicationTemplate", "Application Template", "Шаблон приложения")):
            raise SetupError(f"stale template identifier in {path.relative_to(stage)}")
    entry = (stage / f"{package}.desktop").read_text(encoding="utf-8")
    spec = (stage / "rpm" / f"{package}.spec").read_text(encoding="utf-8")
    main = (stage / "src/main.cpp").read_text(encoding="utf-8")
    cover = (stage / "qml/cover/DefaultCoverPage.qml").read_text(encoding="utf-8")
    if f"Icon={package}" not in entry or f"Exec=/usr/bin/{package}" not in entry:
        raise SetupError("desktop file does not refer to the generated package")
    if f"Name:       {package}" not in spec or f'qml/{app}.qml' not in main:
        raise SetupError("spec or QML entry path does not match the generated package")
    if f"../icons/{app}.svg" not in cover:
        raise SetupError("cover icon path does not match the generated icon")


def publish(stage: Path, output: Path) -> None:
    if not output.exists():
        os.replace(stage, output)
    else:
        for child in stage.iterdir():
            if (output / child.name).exists():
                raise SetupError(f"output collision: {output / child.name}")
        for child in stage.iterdir():
            os.replace(child, output / child.name)


def main() -> int:
    try:
        args = parse_args()
        branch, output, values = validate(args)
        with tempfile.TemporaryDirectory(prefix="aurora-template-") as temporary:
            source, commit = template_source(args, branch, Path(temporary))
            with tempfile.TemporaryDirectory(prefix=".aurora-project-", dir=output.parent) as staging:
                stage = Path(staging)
                write_project(source, stage, args.build_system, values, branch, commit)
                check_project(stage, args.build_system, values)
                publish(stage, output)
        warnings = ["Template Aurora icon artwork is still present"]
        if values["org"] == "ru.example":
            warnings.append("ru.example is a temporary organization identifier")
        if any(ch.isspace() or not ch.isascii() for ch in str(output)):
            warnings.append("Aurora SDK project paths should avoid spaces and Cyrillic characters")
        defaults_used = {
            key: values[value_key]
            for key, value_key in (
                ("display_name_en", "en_name"),
                ("display_name_ru", "ru_name"),
                ("summary", "summary"),
                ("description_en", "en_description"),
                ("description_ru", "ru_description"),
                ("version", "version"),
            )
            if getattr(args, key) is None
        }
        print(json.dumps({"output": str(output), "package_id": values["package"], "build_system": args.build_system, "template_branch": branch, "template_commit": commit, "checks": "static checks passed", "defaults_used": defaults_used, "warnings": warnings}, ensure_ascii=False, indent=2))
        return 0
    except (SetupError, subprocess.CalledProcessError, OSError) as error:
        print(f"setup-project: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
