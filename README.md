[RU](README.ru.md) | [**EN**](README.md)

# aurora-skills

Agent skills for developing applications for Aurora OS, plus a utility skill for reporting agent issues.

> **For AI agents:** Read [AGENTS.md](AGENTS.md) first for the project overview, skill selection entry point, and skill catalog.

## Install

### With `npx skills`

Start with the interview from your project directory:

```bash
npx skills add KotDath/aurora-skills --skill setup-aurora-skills
```

The interview proposes the relevant skills and resolves the agent and local/global scope. Install only the agreed selection. Add `--agent opencode` for OpenCode, `--global` for an explicitly chosen global installation, or `--copy` for copies instead of links.

For development, install `aurora-platform-context` alongside the selected development skill. Installing the whole collection remains an explicit alternative:

```bash
npx skills add KotDath/aurora-skills --agent opencode --skill '*'
```

### By copying files

Clone the repository and copy the **whole skill directory**, including its `scripts/`, `references/`, and `assets/` when present. Project-local `.agents/skills/` is discovered by Codex, Pi, OMP, and OpenCode.

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

## Start with a project interview

Ask your agent to use `setup-aurora-skills`, for example: “Help me set up an Aurora project. Ask me which type of project and toolchain I need.” It inspects an existing project first, asks only about missing choices, and distinguishes Qt/qmake, Qt/CMake, CMake + Conan, Flutter apps, and Flutter plugins using method channels, Qt, or FFI. It also identifies existing projects that need Aurora support or plugin porting work.

The setup records local SDKs in Git-ignored `.aurora/sdk.json` and adds a short project workflow section to `AGENTS.md` (or the project's existing `CLAUDE.md`). It then uses the relevant installed skills for the requested creation or build. Install those skills too when needed; the interview skill does not silently install the collection. Rerunning setup reuses prior answers and updates the chosen settings without regenerating the app.

When a required tool is not found in the checked locations, setup offers an existing path, installation, or continuing with the tool pending when possible. Desktop SDK and PSDK are independent: setup supports SDK, PSDK, or both, according to the requested workflow. When both are selected, their releases, paths, installation checks, and pending steps are tracked separately; an installation handoff for one does not block work on the other. `aurora-install-sdk` checks Linux prerequisites, asks for release and BT/MB2, and downloads the official installer; the user completes graphical installation, then the agent verifies it. `aurora-install-psdk` installs PSDK using only the official setup script and verifies its chroot tooling and targets. Both also work directly without a project interview. Docker, when required by the workflow, is checked; the user installs or fixes it. These skills do not install the Aurora Flutter fork.

CMake + Conan uses the Qt generator's `--build-system cmake --conan` mode: an empty recipe, a pinned Aurora Conan distribution, and RPM build/deployment integration. It does not add libraries implicitly. Creating an Aurora platform skeleton for an upstream Flutter plugin does not complete its port; remaining work is reported separately. Direct use of any specialized skill remains supported without running the interview first.

## Development knowledge stays in skills

Select `aurora-qt-development`, `aurora-flutter-app-development`, or `aurora-flutter-plugin-development` for the project's code work. Each includes stack-specific practices and good/bad examples in its own `references/`. Install the shared `aurora-platform-context` skill alongside it; source/MCP/embedder policy is maintained there once. Onboarding references the selected skill from `AGENTS.md`; it does not generate a project documentation tree.

The official documentation MCP is `https://developer.auroraos.ru/api/mcp`. Development skills combine versioned official documentation with the selected SDK/PSDK headers and official Mos.Hub examples. Flutter skills can retrieve matching [Aurora Embedder sources](https://hub.mos.ru/auroraos/flutter/aurora-embedder) for native behavior; a current default branch is not evidence for an older installed SDK. Local skill versions take precedence over global copies unless explicitly selected otherwise.

## Skills

| Skill | Purpose |
| --- | --- |
| [`setup-aurora-skills`](skills/setup/setup-aurora-skills/SKILL.md) | Interview the user, identify the project type, configure SDK paths and agent instructions, and select the relevant workflow. |
| [`aurora-install-sdk`](skills/setup/aurora-install-sdk/SKILL.md) | Check Linux, download the selected BT/MB2 installer, guide user installation, and verify the SDK. |
| [`aurora-install-psdk`](skills/setup/aurora-install-psdk/SKILL.md) | Install independent PSDK with the official script and verify its tooling and targets. |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Create a Qt/QML application from Aurora OS ApplicationTemplate with qmake, CMake, or CMake + Conan. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Build an Aurora Qt project with `sfdk` and produce RPM packages. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Validate an Aurora RPM against its security profile. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Sign an Aurora RPM with a developer key and certificate. |
| [`aurora-flutter-setup-project`](skills/flutter/aurora-flutter-setup-project/SKILL.md) | Create an Aurora Flutter app or plugin, or add Aurora support to an existing project. |
| [`aurora-flutter-add-dependency`](skills/flutter/aurora-flutter-add-dependency/SKILL.md) | Check a dependency against the curated list and add it with Aurora Flutter. |
| [`aurora-platform-context`](skills/shared/aurora-platform-context/SKILL.md) | Shared source policy, official MCP, SDK/PSDK evidence and matching Flutter embedder sources. |
| [`aurora-qt-development`](skills/qt/aurora-qt-development/SKILL.md) | Implement and review Aurora Qt/QML application code with platform practices and versioned sources. |
| [`aurora-flutter-app-development`](skills/flutter/aurora-flutter-app-development/SKILL.md) | Develop and port Aurora Flutter applications with platform compatibility and lifecycle guidance. |
| [`aurora-flutter-plugin-development`](skills/flutter/aurora-flutter-plugin-development/SKILL.md) | Implement and port Aurora Flutter plugins using channels, Qt or FFI and matching embedder sources. |
| [`report-issue`](skills/util/report-issue/SKILL.md) | Collect an issue ZIP with the current agent session and descendant subagent sessions. |

The Flutter [checked dependency list](skills/flutter/aurora-flutter-add-dependency/scripts/checked-dependencies.yaml) is maintained manually next to its checker. It is historical context. Admission uses the live Aurora server at `https://sdk-repo.omprussia.ru/sdk/flutter/pub/api/packages/<name>`; absent packages require source review of the selected version and dependencies with no native code or `TargetPlatform`.

Generated projects store local SDK paths in Git-ignored `.aurora/sdk.json`. Flutter setup records only the explicitly selected Aurora Flutter SDK and does not discover or invoke sfdk. Qt setup can use `~/AuroraOS/bin/sfdk` as its fallback.

The optional `psdk` field records a selected PSDK root containing `sdk-chroot`, not the outer installation directory. It is independent of `sfdk` and `flutter`; configuring one does not require installing the others. The bundled Qt build helper uses `sfdk`, not PSDK.

The specialized skills reuse answers from the setup interview and also work directly. Qt builds, RPM signing, and RPM validation use the source project's recorded `sfdk` unless the user supplies another one. Flutter workflow-only setup records its SDK without generating platform files. An explicit Flutter SDK change uses the setup helper's `--existing --record-only --replace-sdk --flutter-sdk <new-root>` mode; other settings and application files are preserved.

## Development checks

Run `python3 -m unittest discover -s tests -v` to check Flutter setup handoffs, SDK replacement, destination protection, Conan scaffolding, and bootstrap failures. These tests use local fixtures and simulated SDK/download commands; they do not install an SDK or use the network.
