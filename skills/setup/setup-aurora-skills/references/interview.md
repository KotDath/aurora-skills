# Project interview

## Empty project cases

| User's requested result | Behavior |
| --- | --- |
| Consultation only | Ask about purpose and missing choices, propose stack/skills/scope, write no project files and install nothing without authorization. |
| Configure workflow now, create the app later | Install only agreed skills and record instructions when requested. State that the directory now contains workflow files; do not claim it remains a valid empty scaffold destination. A future scaffold needs an agreed new empty destination, commonly a child directory; do not move/delete workflow files automatically. |
| Create an application now | Agree identity/destination and skill selection first. Read the required generator skill from the collection before project-local installation, generate into the empty destination, then install the agreed skills and record instructions. Neither `.agents/` nor `AGENTS.md` may precede generation in that destination. |

An empty Flutter directory has no `pubspec.yaml`: do not use `--existing --record-only` there. For workflow-only setup, defer the Flutter SDK record until the Flutter project exists rather than generating an app implicitly; record the pending state in the agreed workflow instructions.

Skill installation scope and project metadata are separate choices. Global skills do not keep the destination empty when `AGENTS.md`, `.aurora/` or a project MCP configuration is written there. Explain that consequence for either scope; do not recommend global installation as a workaround for generator destination checks.

## 1. Explore before interviewing

Read the request and conversation first. Inspect the intended project directory: applicable `AGENTS.md` or `CLAUDE.md`, `.aurora/sdk.json`, build files, `pubspec.yaml`, and Aurora platform and RPM files. For a monorepo, identify the relevant subproject rather than treating unrelated components as one application.

- A Flutter SDK dependency in `pubspec.yaml` identifies Flutter; its `flutter.plugin` declaration distinguishes a plugin from an app. Inspect native sources and project docs to distinguish method channels, Qt, and FFI. A plugin's `example/` is not a second project to configure unless requested.
- An Aurora Qt application has a `.pro` or `CMakeLists.txt` together with Aurora application/package references. CMake alone does not establish Qt. A Flutter plugin's native CMake file does not make it a standalone Qt app.
- `conanfile.py` or `conanfile.txt` signals Conan use. An existing `aurora/` directory and platform declarations indicate whether Flutter Aurora support is already present.
- Reuse project identity from build/package metadata; keep the technical name, organization, and display name distinct. Read conflicting declarations as a question to resolve, not permission to rename the project.

Summarize the evidence and remaining unknowns. Check tool paths using [toolchains](toolchains.md) rather than scanning the whole machine. Do not create files in an empty destination until project creation has been resolved.

## 2. Interview only about unresolved choices

Ask a small group of related questions at a time, preferably with meaningful choices when the agent supports them. Lead with a recommendation when evidence supports one; let the user answer freely. Skip anything already answered by the request, conversation, project files, or prior setup. If the user's idea is vague, ask what the application should do before recommending a stack; do not invent features or a detailed architecture.

Work through these decisions as needed:

1. **Starting point and immediate result.** New project or existing project? Configure the agent workflow only, create a scaffold, or also build it? Honor the user's stated result instead of asking again. For a planned new project, return the proposed setup if creation is not requested. When creation is requested, generate the scaffold before writing onboarding metadata, which would otherwise make the destination nonempty.
2. **Project type.** Qt application with qmake, CMake, or CMake + Conan; Flutter application; new Flutter plugin with Dart D-Bus, method channels, Qt, or FFI; or adaptation of an existing Flutter project/plugin to Aurora. Ask about Conan only for Qt/CMake, and plugin implementation only for a plugin. If the user is unsure about plugin implementation, use the plugin development skill to choose between documented Dart D-Bus access, method channels, Qt APIs and a C ABI; do not force native scaffolding for a Dart-only backend.
3. **Identity and destination.** When scaffold creation is requested, collect the technical name, organization, display names, and brief description required by the chosen setup skill. For consultation or workflow-only setup, defer unused scaffold fields. Offer these together as a project card. If the organization is unknown, propose `ru.example` explicitly as a temporary placeholder, following this repository's setup skills. For an existing project, retain its identity and location. Never silently normalize names or rename files to fit an answer.
4. **Toolchains for the requested operations.** SDK and PSDK are independent and can be used together: select SDK, PSDK, or both from the user's requested workflow. Neither requires the other. The bundled Qt build/sign/validate skills use the desktop SDK's `sfdk`. A PSDK/chroot workflow uses `sdk-chroot` and its tooling; do not route it to an `sfdk` helper. For Flutter, use only the recorded or user-supplied Aurora Flutter executable for project commands; do not discover or record sfdk as part of Flutter setup. Its native build backend can still require SDK BT or PSDK, configured through the selected Flutter tooling. Defer device and credentials until needed, and architecture/target until a build or toolchain installation needs them. A Qt scaffold can be created without an installed toolchain; report it as pending.

For development workflows, include the matching development skill from [selection](selection.md); it carries platform knowledge and source priorities. A scaffold-only or build-only request does not require loading development references.

Base Qt compatibility and build-system advice on the target Aurora SDK and template, not the host's Qt or CMake version. A host Qt 6 installation does not establish Qt 6 support in the selected Aurora target. Honor an explicit build-system choice; otherwise use the Qt setup skill's documented recommendation.

Show a compact card of the resolved project type, destination, identity, SDKs, requested action, and relevant skills. Clarify unresolved or conflicting values. Once the user has approved the concrete skill selection and scope and requested the action, proceed without an additional approval round. Answers about stack or scope alone do not approve an unseen list. In explicitly autonomous mode, use established project facts and the selected skill's defaults, disclose assumptions, and ask only for information that cannot safely be inferred, such as a missing Flutter SDK path or an ambiguous target project.

On rerun, show the existing setup and ask only what remains unknown or what the user wants changed. A request to change the setup is not permission to regenerate the application or switch its build system.

