---
name: aurora-qt-setup-project
description: Create a new Aurora OS Qt/QML application from ApplicationTemplate with qmake or CMake, including a conversational choice of app identity and metadata. Use for a new project scaffold, not for renaming an existing application.
---

# Aurora Qt project setup

Create a Qt/QML application scaffold from the official Aurora OS `ApplicationTemplate`. The bundled script performs the file and identifier changes; use the conversation to decide the values passed to it. Speak in the user's language.

## Collect project details

Extract any values the user already supplied. For missing values, propose a compact project card rather than asking one question per field:

- Build system: `qmake` or `cmake`. If the user gives no preference, offer both and recommend `qmake`, which uses the template's default branch. Use `qmake` in no-questions mode.
- Output directory: the current directory if the user says “here” or “in this project”. For an unspecified destination, use the current directory if empty (or containing only `.git`); otherwise propose an app-named child directory. In no-questions mode, use that child directory.
- Organization identifier, such as `ru.example`, and code name, such as `DotaCompanion`. Together they form the package ID `ru.example.DotaCompanion`.
- Display names in English and Russian, short RPM summary, and app description.
- Optional version and project URL.

Treat an app idea as input for suggestions, not as a complete functional specification. Keep the code name separate from the display names. Do not invent a real organization identifier. If it is unknown, suggest `ru.example` explicitly as a temporary value. Do not fabricate specific app features for a vague idea; use a neutral description or ask what the app should do.

In the normal conversational mode, show the proposed values together and invite corrections before creating files. Ask only about missing or ambiguous information. If the user already supplied all values and requested creation, proceed without an extra confirmation. If the user explicitly asks for autonomous or no-questions operation, choose sensible defaults, create the scaffold, and report every assumption and temporary value afterward.

The script accepts only a new/empty directory or one containing only `.git`. Treat this as a boundary. If the user explicitly requests a nonempty directory, report the conflict and ask for an empty destination or a separate integration task; even in no-questions mode, stop rather than merging files manually. Do not generate in a staging directory and copy files around this check. If the destination was not specified, choose an app-named child directory as described above.

## Generate

Run `scripts/setup_project.py` with the resolved values. It accepts `--build-system`, `--organization`, `--app-name`, and `--output`; pass display names, summary, descriptions, version, and URL when known. Use `--help` for exact flags. Do not implement identifier replacement ad hoc when the script supports the task.

The script downloads the `example` branch for qmake or `cmake-version` for CMake, records its commit, creates the project, and checks for stale template identifiers. Read [references/template-map.md](references/template-map.md) when investigating a template change or adapting the transformation. If a user supplies their own icon assets, replace the matching generated placeholder icons after creation; otherwise tell them that the Aurora template artwork is still present.

After generation, report the output path, package ID, build system, template commit, and checks performed. When `~/AuroraOS/bin/sfdk` exists, the script records its absolute path in the Git-ignored project file `.aurora/sdk.json`; use `--sfdk` with a different Qt SDK root or executable supplied by the user. The same file can later hold the explicitly supplied Aurora Flutter SDK path. The script's static validation is sufficient for setup. Build with the Aurora SDK only when the user asks for a build; do not change global SDK settings or copy the project outside the output directory for this purpose. This skill sets up a project; implement the app's requested features separately if the user asked for them.
