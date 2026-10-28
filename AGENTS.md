# aurora-skills

This repository contains skills.sh-compatible agent skills for Aurora OS development: Qt and Flutter project setup, SDK/PSDK installation, Qt builds, Flutter dependencies, RPM signing and validation, plus an agent issue-reporting utility. Each skill lives in `skills/<category>/<skill-name>/` with its entry point in `SKILL.md` and any supporting resources alongside it.

## Choosing which skills to install

Start with [`setup-aurora-skills`](skills/setup/setup-aurora-skills/SKILL.md). Load it by name if installed; otherwise read its linked `SKILL.md` from this repository. It inspects the user's intended project, asks only about missing choices, and identifies the relevant specialized skills. Use the user's project directory for this interview. When maintaining this skill collection, edit the collection rather than running project onboarding on this repository.

Reuse known answers and recommend the skills needed for the requested workflow. SDK and PSDK can be selected separately or together. If the task already names a specific operation, go directly to its skill instead of requiring the interview.

To install the interview skill:

```bash
npx skills add KotDath/aurora-skills --skill setup-aurora-skills
```

For additional skills, replace the name with a selection from the table. Use the user's chosen agent and installation scope; see [README.md](README.md) or [README.ru.md](README.ru.md) for installation options. Read each selected skill's `SKILL.md` before using it. Copy the whole skill directory when installing manually so supporting files remain available.

## Skill catalog

| Skill | What it does |
| --- | --- |
| [`setup-aurora-skills`](skills/setup/setup-aurora-skills/SKILL.md) | Interview the user, identify the project and toolchains, select relevant skills, and record the project workflow. |
| [`aurora-install-sdk`](skills/setup/aurora-install-sdk/SKILL.md) | Check Linux prerequisites, download the chosen BT/MB2 installer, hand graphical installation to the user, and verify the SDK. |
| [`aurora-install-psdk`](skills/setup/aurora-install-psdk/SKILL.md) | Install PSDK with the official script and verify its chroot tooling and targets. |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Create a Qt/QML application using qmake, CMake, or CMake + Conan. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Build an existing Qt application with `sfdk` and produce RPM packages. |
| [`aurora-flutter-setup-project`](skills/flutter/aurora-flutter-setup-project/SKILL.md) | Create an Aurora Flutter app or plugin, add the Aurora platform, or record the selected SDK. |
| [`aurora-flutter-add-dependency`](skills/flutter/aurora-flutter-add-dependency/SKILL.md) | Check a Flutter package against the curated allowlist and add an allowed dependency. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Sign an existing RPM with the user's developer key and certificate. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Validate an existing RPM against its security profile and explain the results. |
| [`report-issue`](skills/util/report-issue/SKILL.md) | Prepare an issue ZIP containing the current agent session and descendant subagent sessions. |
