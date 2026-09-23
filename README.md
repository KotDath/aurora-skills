# aurora-skills

Agent skills for developing applications for Aurora OS.

## Install

```bash
npx skills add KotDath/aurora-skills --skill aurora-qt-setup-project
npx skills add KotDath/aurora-skills --skill aurora-qt-build-project
npx skills add KotDath/aurora-skills --skill aurora-rpm-validate
npx skills add KotDath/aurora-skills --skill aurora-rpm-sign
```

For a non-interactive OpenCode project install, add `--agent opencode --yes`.

## Available skills

| Skill | Purpose |
| --- | --- |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Create a Qt/QML project from Aurora OS ApplicationTemplate using qmake or CMake. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Build an existing Aurora Qt project for an installed sfdk target and produce RPM packages. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Validate a built Aurora RPM against its security profile. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Sign a built Aurora RPM, with explicit handling of an existing signature. |

The [Flutter Aurora 3.41.4 empirical package list](data/flutter/empirical-pure-packages-3.41.4.yaml) records exact package versions and their inspected runtime dependency closures. It is based on source inspection, not device testing.

Example request: “Create an Aurora OS Qt app in this directory. Suggest a name and project settings first.” The skill uses information already present in the request, proposes missing values in conversation, and generates the project after they are settled. Ask it to work “without questions” to use autonomous defaults.
