---
name: aurora-flutter-setup-project
description: Create an Aurora OS Flutter app or plugin, or add the Aurora platform to an existing Flutter project, using a specified Aurora Flutter SDK and recording its local path for later work.
---

# Set up an Aurora Flutter project

Use the Aurora Flutter fork, not an upstream `flutter` found on `PATH`. Resolve the SDK from an explicit user path, `AURORA_FLUTTER_ROOT`, or the project's `.aurora-flutter-sdk` file. If none is available, ask for the SDK path. The bundled script verifies that the executable reports an Aurora channel.

Run `scripts/setup_project.py --flutter-sdk <sdk-root> --output <directory>` for a new app. Add `--template plugin`, `plugin_qt`, or `plugin_ffi` when the user wants a plugin of that kind; the normal plugin template uses method channels. Pass `--org`, `--project-name`, and `--description` when known. For an existing Flutter project, pass `--existing`; use `--record-only --existing` if the Aurora platform already exists and only the SDK path needs recording. Read `--help` for exact flags.

For an unspecified output, use an app-named child directory of the current directory. Do not overwrite a nonempty destination for a new project. When no organization was given, `ru.example` is a temporary placeholder; tell the user. Do not invent a real organization identity.

After a successful create, the script writes the absolute SDK root to `.aurora-flutter-sdk` in the project and ignores that local file in Git. Read it on every later turn so the path survives context changes. Check that `pubspec.yaml` and the Aurora platform files were created. Report the project location, template, effective SDK path, and Flutter version. Build or run the app only when requested.

To add packages after setup, use the separate `aurora-flutter-add-dependency` skill. Its manually maintained `scripts/checked-dependencies.yaml` is the dependency acceptance list; do not duplicate that list here.
