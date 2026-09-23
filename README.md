# aurora-skills

Agent skills for developing applications for Aurora OS.

## Install

```bash
npx skills add KotDath/aurora-skills --skill aurora-qt-setup-project
npx skills add KotDath/aurora-skills --skill aurora-qt-build-project
npx skills add KotDath/aurora-skills --skill aurora-rpm-validate
npx skills add KotDath/aurora-skills --skill aurora-rpm-sign
npx skills add KotDath/aurora-skills --skill aurora-flutter-setup-project
npx skills add KotDath/aurora-skills --skill aurora-flutter-add-dependency
```

For a non-interactive OpenCode project install, add `--agent opencode --yes`.

## Available skills

| Skill | Purpose |
| --- | --- |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Create a Qt/QML project from Aurora OS ApplicationTemplate using qmake or CMake. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Build an existing Aurora Qt project for an installed sfdk target and produce RPM packages. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Validate a built Aurora RPM against its security profile. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Sign a built Aurora RPM, with explicit handling of an existing signature. |
| [`aurora-flutter-setup-project`](skills/flutter/aurora-flutter-setup-project/SKILL.md) | Create an Aurora Flutter app or plugin, or add Aurora support to an existing project; remember the local SDK path. |
| [`aurora-flutter-add-dependency`](skills/flutter/aurora-flutter-add-dependency/SKILL.md) | Check a dependency against the allowlist, then add an allowed package with Aurora Flutter. |

The manually maintained [Flutter Aurora dependency checklist](skills/flutter/aurora-flutter-add-dependency/scripts/checked-dependencies.yaml) sits next to its checker. The checker only looks up package names; for an unknown name it returns links for source review. Packages in Aurora Pub are accepted by project policy. The list contains package names, not version pins.

Example request: “Create an Aurora OS Qt app in this directory. Suggest a name and project settings first.” The skill uses information already present in the request, proposes missing values in conversation, and generates the project after they are settled. Ask it to work “without questions” to use autonomous defaults.
