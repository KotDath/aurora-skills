[RU](README.ru.md) | [**EN**](README.md)

# aurora-skills

Agent skills for developing applications for Aurora OS, plus a utility skill for reporting agent issues.

## Install

### With `npx skills`

Run the command from the project where you want the skills. To install **all skills for all supported agents** without prompts:

```bash
npx skills add KotDath/aurora-skills --all
```

To install all skills while choosing the target agents interactively, or to install one specific skill:

```bash
npx skills add KotDath/aurora-skills --skill '*'
npx skills add KotDath/aurora-skills --skill aurora-qt-setup-project
```

Replace `aurora-qt-setup-project` with any name from the table below. Add `--copy` to copy files instead of creating links, or `--global` to install for your user across projects.

### By copying files

Clone the repository and copy the **whole skill directory**, including its `scripts/` and `references/` when present. Project-local `.agents/skills/` is discovered by Codex, Pi, OMP, and OpenCode.

```bash
git clone https://github.com/KotDath/aurora-skills.git
cd aurora-skills
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"

# All skills:
cp -R skills/*/* "$PROJECT/.agents/skills/"
```

To copy just one skill instead, replace the last command with `cp -R skills/qt/aurora-qt-setup-project "$PROJECT/.agents/skills/"` (or another skill directory from the table).

For installation across projects, use `~/.agents/skills/` as the destination instead.

## Skills

| Skill | Purpose |
| --- | --- |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Create a Qt/QML application from Aurora OS ApplicationTemplate with qmake or CMake. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Build an Aurora Qt project with `sfdk` and produce RPM packages. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Validate an Aurora RPM against its security profile. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Sign an Aurora RPM with a developer key and certificate. |
| [`aurora-flutter-setup-project`](skills/flutter/aurora-flutter-setup-project/SKILL.md) | Create an Aurora Flutter app or plugin, or add Aurora support to an existing project. |
| [`aurora-flutter-add-dependency`](skills/flutter/aurora-flutter-add-dependency/SKILL.md) | Check a dependency against the curated list and add it with Aurora Flutter. |
| [`report-issue`](skills/util/report-issue/SKILL.md) | Collect an issue ZIP with the current agent session and descendant subagent sessions. |

The Flutter [checked dependency list](skills/flutter/aurora-flutter-add-dependency/scripts/checked-dependencies.yaml) is maintained manually next to its checker. It records package names without version pins; listed Aurora Pub packages are accepted by project policy.

Generated projects store local SDK paths in Git-ignored `.aurora/sdk.json`. The Aurora Flutter SDK path is explicitly chosen; `sfdk` defaults to `~/AuroraOS/bin/sfdk` when available.
