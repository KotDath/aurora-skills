---
name: setup-aurora-skills
description: Interview the user to choose an Aurora OS project type and configure this skill set for a new or existing project. Use for initial onboarding, choosing between Qt and Flutter apps or plugins, or updating project SDK settings and agent instructions. Reuse known answers and route creation, builds, dependencies, signing, and validation to the relevant skills.
---

# Set up Aurora skills

Turn an app idea or an existing repository into a concrete Aurora development setup. Conduct an adaptive interview in the user's language, record the agreed project context, and perform the requested next action using the specialized skills. This is a conversational skill; it has no scaffolding CLI of its own.

## 1. Explore before interviewing

Read the request and conversation first. Inspect the intended project directory: applicable `AGENTS.md` or `CLAUDE.md`, `.aurora/sdk.json`, build files, `pubspec.yaml`, and Aurora platform and RPM files. For a monorepo, identify the relevant subproject rather than treating unrelated components as one application.

- A Flutter SDK dependency in `pubspec.yaml` identifies Flutter; its `flutter.plugin` declaration distinguishes a plugin from an app. Inspect native sources and project docs to distinguish method channels, Qt, and FFI. A plugin's `example/` is not a second project to configure unless requested.
- An Aurora Qt application has a `.pro` or `CMakeLists.txt` together with Aurora application/package references. CMake alone does not establish Qt. A Flutter plugin's native CMake file does not make it a standalone Qt app.
- `conanfile.py` or `conanfile.txt` signals Conan use. An existing `aurora/` directory and platform declarations indicate whether Flutter Aurora support is already present.
- Reuse project identity from build/package metadata; keep the technical name, organization, and display name distinct. Read conflicting declarations as a question to resolve, not permission to rename the project.

Summarize the evidence and remaining unknowns. Look for SDKs in the known locations above rather than scanning the whole machine. Do not create files in an empty destination until project creation has been resolved.

## 2. Interview only about unresolved choices

Ask a small group of related questions at a time, preferably with meaningful choices when the agent supports them. Lead with a recommendation when evidence supports one; let the user answer freely. Skip anything already answered by the request, conversation, project files, or prior setup. If the user's idea is vague, ask what the application should do before recommending a stack; do not invent features or a detailed architecture.

Work through these decisions as needed:

1. **Starting point and immediate result.** New project or existing project? Configure the agent workflow only, create a scaffold, or also build it? Honor the user's stated result instead of asking again. For a planned new project, return the proposed setup if creation is not requested. When creation is requested, generate the scaffold before writing onboarding metadata, which would otherwise make the destination nonempty.
2. **Project type.** Qt application with qmake, CMake, or CMake + Conan; Flutter application; new Flutter plugin with method channels, Qt, or FFI; or adaptation of an existing Flutter project/plugin to Aurora. Ask about Conan only for Qt/CMake, and plugin implementation only for a plugin. If the user is unsure about plugin implementation, recommend method channels for ordinary platform APIs, Qt for Qt APIs, and FFI for a C ABI.
3. **Identity and destination.** For a new project, collect the technical name, organization, display names, and brief description required by the chosen setup skill. Offer these together as a project card. If the organization is unknown, propose `ru.example` explicitly as a temporary placeholder, following this repository's setup skills. For an existing project, retain its identity and location. Never silently normalize names or rename files to fit an answer.
4. **Toolchain.** For Flutter, use the project record or a user-supplied Aurora Flutter SDK path from this conversation; ask if neither exists. For Qt, use a user-supplied `sfdk`, then the project record, then `~/AuroraOS/bin/sfdk` when available. Defer architecture, target, device, and credentials until the requested build, deployment, or signing actually needs them. A Qt scaffold can be created without a locally installed SDK; report that its toolchain remains unconfigured.

Show a compact card of the resolved project type, destination, identity, SDKs, requested action, and relevant skills. Clarify unresolved or conflicting values. Once the user has supplied the needed choices and requested the action, proceed without an additional approval round. In explicitly autonomous mode, use established project facts and the selected skill's defaults, disclose assumptions, and ask only for information that cannot safely be inferred, such as a missing Flutter SDK path or an ambiguous target project.

On rerun, show the existing setup and ask only what remains unknown or what the user wants changed. A request to change the setup is not permission to regenerate the application or switch its build system.

## 3. Load the selected skills and perform the requested action

Use the agent's skill-loading tool when available. Otherwise read the selected installed `SKILL.md` before using its scripts. Resolve each skill by name from the available skill inventory or known project/global skill directories. In a checkout of this repository they live under `skills/<category>/<name>`; installers may flatten them. Do not assume sibling relative paths survive installation, and do not load every skill in the collection.

| Need | Skill or next step |
| --- | --- |
| New Qt/qmake, Qt/CMake, or Qt/CMake + Conan application | `aurora-qt-setup-project`; use `--build-system cmake --conan` for Conan |
| New Flutter app or plugin (`plugin`, `plugin_qt`, `plugin_ffi`) | `aurora-flutter-setup-project` |
| Add the Aurora platform to an existing Flutter project | `aurora-flutter-setup-project`, using its existing-project mode only when requested |
| Record the SDK for an existing Flutter project without generation | `aurora-flutter-setup-project` with `--existing --record-only` |
| Build a Qt application | `aurora-qt-build-project` |
| Check and add a Flutter package | `aurora-flutter-add-dependency` |
| Sign or validate a built RPM | `aurora-rpm-sign` or `aurora-rpm-validate`, according to the requested operation |

Pass the agreed answers to the chosen skill so it does not restart the interview. Follow its destination checks and validation; do not duplicate its generator, bypass its refusal to write into a nonempty directory, or write onboarding files ahead of scaffolding. Use `--no-pub` for a Flutter scaffold when dependency resolution was not requested. Do not add packages just because they might be useful.

For an existing project's workflow-only setup, inspect files and record configuration; do not rerun creation or add the Aurora platform implicitly. For a Qt build, let the build skill handle target selection. No Flutter build skill is bundled: if a Flutter build was explicitly requested, inspect the selected SDK's help and the project's build instructions and use that recorded SDK; do not route it to the Qt build skill.

The Conan option creates a CMake scaffold with an empty recipe and Aurora RPM integration. Preserve existing Conan dependencies during workflow-only setup; adding packages and reviewing their RPM requirements are separate dependency changes. The Flutter setup skill can generate Aurora platform scaffolding, but that does not implement or test a port of an upstream plugin. Report the remaining porting work; do not call the port complete. For an explicitly requested unsupported operation, explain the gap before making a partial substitute.

If a selected skill is missing, report its exact name. Offer an install command such as `npx skills add KotDath/aurora-skills --skill <name>`; use the user's chosen agent and installation scope if installation is requested. Do not install the entire collection or fall back to an unrelated globally installed generator. Configuration can be saved with the missing capability clearly marked pending.

## 4. Record local SDKs and durable project instructions

Write configuration in the selected project root only after it exists and creation, if requested, has succeeded. For an existing project, merge with its current settings. Keep these two kinds of information separate:

**Local toolchain: `.aurora/sdk.json`.** Reuse the existing contract: `flutter` is the absolute Aurora Flutter SDK root; `sfdk` is the absolute Qt SDK executable. Preserve unrelated keys and any other stack's SDK value. Validate JSON and path types before editing; report malformed configuration rather than replacing it with an empty record. Record only SDKs that were found and validated, with no placeholder paths. Flutter must report an Aurora channel through `bin/flutter --version --machine`; `sfdk` must be executable and identify itself through `--version`. Resolve conflicting choices before changing a recorded SDK; a user's explicit SDK-change request already resolves that choice and needs no further approval. For Flutter, use `aurora-flutter-setup-project` in `--existing --record-only` mode, adding `--replace-sdk --flutter-sdk <new-root>` for an explicitly requested replacement. This preserves its SDK checks and legacy-marker migration without platform generation.

For an existing Qt project being configured without a build, validate the selected `sfdk` and merge its absolute executable path into `.aurora/sdk.json`; do not run a build merely to save the path. Ensure `/.aurora/sdk.json` is ignored by the project's `.gitignore`, preserving existing entries. If the file is already tracked, tell the user; adding an ignore rule alone does not untrack it. Never put personal SDK paths, keys, credentials, or device addresses into committed agent instructions.

**Project workflow: `AGENTS.md`.** Add or merge one Aurora section in the selected project's existing `AGENTS.md`. If its maintained agent instructions live in `CLAUDE.md` instead, update that file; do not create a competing set. If neither exists, create `AGENTS.md`. Keep unrelated instructions and user edits. Use the markers below to locate this skill's section on subsequent runs; if an equivalent Aurora section already exists, merge it rather than appending a duplicate.

```markdown
<!-- aurora-skills:start -->
## Aurora development

- Project: <Qt/Flutter app or plugin, build system or plugin implementation>.
- Identity: <organization, technical name, display name, or existing identifier>.
- Local SDKs: read `.aurora/sdk.json`; keep SDK paths out of committed files.
- Workflow: <selected skill names and the operations they handle>.
- Pending: <only genuine missing tools or unsupported work; omit when none>.
<!-- aurora-skills:end -->
```

Replace the example fields with the agreed facts; mention only relevant skills. Do not make generic onboarding a prerequisite for later direct skill requests or instruct other skills to rerun setup on every turn. Project type and workflow belong in the agent section; do not add an incompatible project schema to `.aurora/sdk.json`.

## 5. Verify and report

Check that the recorded SDK paths resolve, local SDK configuration is ignored, agent instructions contain one coherent Aurora section, and project identity still agrees with its build/package metadata. Inspect the diff after setup. Report the selected scenario, files changed, SDK checks, action actually completed, and any pending capabilities. Distinguish workflow configuration, scaffold creation, compilation, signing, and validation; successful setup alone does not establish that a project builds or runs.
