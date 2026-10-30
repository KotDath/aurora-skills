# Skill selection, installation and handoff

## 3. Load the selected skills and perform the requested action

Use the agent's skill-loading tool when available. Otherwise read the selected installed `SKILL.md` before using its scripts. Resolve each skill by name from the available skill inventory or known project/global skill directories. Prefer an explicitly selected version, otherwise the project-local copy over a global copy; report a shadowed global copy when it affects the result. Respect applicable project instructions and do not combine conflicting versions of a skill. In a checkout of this repository they live under `skills/<category>/<name>`; installers may flatten them. Do not assume sibling relative paths survive installation, and do not load every skill in the collection.

| Need | Skill or next step |
| --- | --- |
| Install the desktop Aurora SDK after the user selects installation | `aurora-install-sdk` |
| Install the independent Aurora Platform SDK after the user selects installation | `aurora-install-psdk` |
| Install both SDK and PSDK | Use both installation skills independently; retain each installation's state and paths |
| Implement, debug or review Qt/QML application behavior | `aurora-platform-context` + `aurora-qt-development` |
| Implement, debug or review a Flutter application | `aurora-platform-context` + `aurora-flutter-app-development` |
| Implement or port an Aurora Flutter plugin/backend | `aurora-platform-context` + `aurora-flutter-plugin-development` |
| New Qt/qmake, Qt/CMake, or Qt/CMake + Conan application | `aurora-qt-setup-project`; use `--build-system cmake --conan` for Conan |
| New Flutter app or plugin (`plugin`, `plugin_qt`, `plugin_ffi`) | `aurora-flutter-setup-project` |
| Add the Aurora platform to an existing Flutter project | `aurora-flutter-setup-project`, using its existing-project mode only when requested |
| Record the SDK for an existing Flutter project without generation | `aurora-flutter-setup-project` with `--existing --record-only` |
| Build a Qt application | `aurora-qt-build-project` |
| Check and add a Flutter package | `aurora-flutter-add-dependency` |
| Sign or validate a built RPM | `aurora-rpm-sign` or `aurora-rpm-validate`, according to the requested operation |

Pass the agreed answers to the chosen skill so it does not restart the interview. Follow its destination checks and validation; do not duplicate its generator, bypass its refusal to write into a nonempty directory, or write onboarding files ahead of scaffolding. Use `--no-pub` for a Flutter scaffold when dependency resolution was not requested. Do not add packages just because they might be useful.

Project-local skill installation also creates files. For a requested scaffold in the same empty root, defer that installation until generation succeeds; load/read the selected skill from this collection for the generation step. Authorization covers the agreed installation, not changing its scope to global as a workaround.

For an existing project's workflow-only setup, inspect files and record configuration; do not rerun creation or add the Aurora platform implicitly. For a Qt build, let the build skill handle target selection. No Flutter build skill is bundled: if a Flutter build was explicitly requested, inspect the selected SDK's help and the project's build instructions and use that recorded SDK; do not route it to the Qt build skill.

The Conan option creates a CMake scaffold with an empty recipe and Aurora RPM integration. Preserve existing Conan dependencies during workflow-only setup; adding packages and reviewing their RPM requirements are separate dependency changes. The Flutter setup skill can generate Aurora platform scaffolding, but that does not implement or test a port of an upstream plugin. Report the remaining porting work; do not call the port complete. For an explicitly requested unsupported operation, explain the gap before making a partial substitute.

If selected skills are missing, propose their exact names and purpose, identify the target agent, and resolve project-local versus global scope. Recommend project-local installation for a project workflow. Show the concrete selection and scope for confirmation before installing unless the user has already authorized that selection and scope; reuse prior answers. Use a command such as `npx skills add KotDath/aurora-skills --skill <name> --agent <agent> --copy` from the project root, adding `--global` only for the chosen global scope. Do not install the entire collection or fall back to an unrelated globally installed generator. Verify discovery after installation and read the selected skills. Configuration can be saved with missing capabilities clearly marked pending.

For requested documentation MCP setup, use `aurora-platform-context` for the endpoint, evidence policy and verification. Resolve the client configuration scope before editing it, preserving other servers. Include this shared skill with each development skill; it is not needed for a scaffold-only or build-only task.

Install independent copies by default, including every supporting file. Do not link installed skills to a source checkout or temporary clone. With the skills CLI use `--copy`; with manual installation copy the whole directory. Symbolic-link installation is only for an explicitly requested development workflow. Check the installed paths and report the method; installation scope and copy/link method are separate concerns.
