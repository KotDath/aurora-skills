---
name: aurora-flutter-app-development
description: Implement, debug, port, and review Flutter applications for Aurora OS. Use for Dart screens, state, platform-dependent features, lifecycle issues, or Aurora app compatibility. Excludes scaffold-only tasks and native plugin implementation.
---

# Develop an Aurora Flutter application

Read the project's instructions, `pubspec.yaml`, lockfile and `.aurora/sdk.json`. Reuse the recorded Aurora Flutter SDK for commands. An ordinary upstream SDK or a dependency's Linux support does not establish Aurora support.

Before selecting platform APIs, load `aurora-platform-context` by name and read its source-selection policy. Before editing app behavior, read [platform practices and examples](references/development.md). For native integration failures or uncertain embedder behavior, read the Flutter/embedder reference in `aurora-platform-context`.

Keep Dart UI and app state separate from the platform adapter. Check whether each required feature is pure Dart or requires an Aurora native implementation. Use `aurora-flutter-add-dependency` for package changes, `aurora-flutter-setup-project` for requested scaffolding/platform generation, and `aurora-flutter-plugin-development` when a native plugin must be implemented or ported. Load those skills by name only for the relevant work; do not silently install them or expand an app change into a plugin rewrite.

Use the selected SDK's analyzer and focused Dart/widget tests for changed behavior. For requested target builds, inspect that SDK's help and project build instructions; the Qt build helper is not a Flutter builder. Verify native features on Aurora when available, and report device/emulator checks separately from host tests. A Dart mock does not prove that a plugin is registered or functional on Aurora.

Research provenance and known documentation conflicts are in [evidence and limits](references/evidence.md). Do not treat the source snapshots as proof that an arbitrary installed SDK/device matches them. Install `aurora-platform-context` alongside this skill for the shared source policy; task-specific references remain in this skill.
