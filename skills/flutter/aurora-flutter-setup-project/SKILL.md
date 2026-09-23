---
name: aurora-flutter-setup-project
description: Create an Aurora OS Flutter app or plugin, or add the Aurora platform to an existing Flutter project, using a specified Aurora Flutter SDK and recording its local path for later work.
---

# Set up an Aurora Flutter project

Use the Aurora Flutter fork, not an upstream `flutter` found on `PATH`. For first-time setup, require a Flutter SDK path explicitly supplied by the user; use a path already supplied in the conversation without asking again. The bundled script verifies that the executable reports an Aurora channel and records its absolute root as the `flutter` value in the project-root `.aurora/sdk.json`. Once that value exists, treat it as authoritative: do not switch to another SDK through `PATH`, an environment variable, or an incidental command argument. If no Flutter SDK path is known, ask for it.

Run `scripts/setup_project.py --flutter-sdk <sdk-root> --output <directory>` for a new app. Add `--template plugin`, `plugin_qt`, or `plugin_ffi` when the user wants a plugin of that kind; the normal plugin template uses method channels. Pass `--org`, `--project-name`, and `--description` when known. For an existing Flutter project, pass `--existing`; use `--record-only --existing` if the Aurora platform already exists and only the SDK path needs recording. The script records `~/AuroraOS/bin/sfdk` in the same config when installed, or a user-supplied alternative via `--sfdk`. Read `--help` for exact flags.

For an unspecified output, use an app-named child directory of the current directory. Do not overwrite a nonempty destination for a new project. When no organization was given, `ru.example` is a temporary placeholder; tell the user. Do not invent a real organization identity.

After a successful create, the script writes `.aurora/sdk.json` and ignores that local file in Git. Its fields are `flutter` (Aurora Flutter SDK root) and, when available, `sfdk` (Qt SDK executable). Read `flutter` on every later turn and use its `<sdk-root>/bin/flutter` for every project operation, including `pub add`, `pub get`, building, and running. A conflicting Flutter SDK path is an error to resolve explicitly, not a reason to overwrite the record. The setup script migrates an existing `.aurora-flutter-sdk` marker to this format. Check that `pubspec.yaml` and the Aurora platform files were created. Report the project location, template, effective SDK path, and Flutter version. Build or run the app only when requested.

To add packages after setup, use the separate `aurora-flutter-add-dependency` skill. Its manually maintained `scripts/checked-dependencies.yaml` is the dependency acceptance list; do not duplicate that list here.
