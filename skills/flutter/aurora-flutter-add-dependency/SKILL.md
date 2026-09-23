---
name: aurora-flutter-add-dependency
description: Check a Flutter dependency against the manually maintained Aurora allowlist, then add an allowed package to an Aurora Flutter project when requested.
---

# Add an Aurora Flutter dependency

Before adding a package, run `python3 <this-skill-directory>/scripts/check_dependency.py --package <name>`. The checker reads only the adjacent [checked-dependencies.yaml](scripts/checked-dependencies.yaml). It is a fast, offline lookup: it does not query a registry, modify the YAML, run Flutter, or edit a project. The user maintains the YAML manually; do not add names to it unless explicitly asked.

If the result has `allowed: true`, treat the package as permitted by this project's list. Both `aurora_pub` and `source_checked_outside_aurora_pub` are accepted sections. A package recorded under `aurora_pub` is accepted by the user's rule that presence in Aurora Pub is sufficient. The list is for direct dependencies: keep the main federated plugin, such as `package_info_plus`, and do not suggest its `platform_interface` or `package_info_plus_aurora` implementation as separate additions. Let Aurora Flutter resolve those internally. Standalone Aurora-specific APIs such as `services_aurora` remain valid direct dependencies.

If a requested package is absent, first check whether it is a platform interface or an implementation of a listed main plugin; if so, use the main plugin. Otherwise, tell the user that compatibility is uncertain and follow the returned links to inspect the package's physical source and its transitive dependencies. Absence from this curated list alone does not mean the package is incompatible. Do not silently mark an unknown name as allowed or write the result into the YAML.

When the user asks to add an allowed dependency, read the `flutter` value from the project-root `.aurora/sdk.json` created by `aurora-flutter-setup-project`. This absolute path is the only SDK source for project operations. If the file is missing, use the setup skill to record the user's SDK path first; do not guess from `PATH` or an environment variable. If the recorded path is invalid, stop and report that problem instead of switching SDKs. Verify that `<recorded-root>/bin/flutter --version --machine` reports an Aurora channel.

From the project directory, run `<recorded-root>/bin/flutter pub add <name>`; for a development dependency use `dev:<name>`, and supply a version constraint only when requested. Do not add dependencies by manually editing `pubspec.yaml`, `aurora_pubspec.lock`, or package configuration. Let `flutter pub add` update them, then inspect the resulting diff and report the resolved version from `aurora_pubspec.lock` or `<recorded-root>/bin/flutter pub deps --json`. Use the same recorded SDK for every later Flutter command.

For a native Aurora plugin, read its README and `pubspec.yaml` for project setup, permissions, and build requirements before claiming integration is complete. Device testing is a separate step.
