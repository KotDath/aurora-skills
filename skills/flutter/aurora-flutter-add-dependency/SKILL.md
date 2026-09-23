---
name: aurora-flutter-add-dependency
description: Check a Flutter dependency against the manually maintained Aurora allowlist, then add an allowed package to an Aurora Flutter project when requested.
---

# Add an Aurora Flutter dependency

Before adding a package, run `python3 <this-skill-directory>/scripts/check_dependency.py --package <name>`. The checker reads only the adjacent [checked-dependencies.yaml](scripts/checked-dependencies.yaml). It is a fast, offline lookup: it does not query a registry, modify the YAML, run Flutter, or edit a project. The user maintains the YAML manually; do not add names to it unless explicitly asked.

If the result has `allowed: true`, treat the package as permitted by this project's list. Both `aurora_pub` and `source_checked_outside_aurora_pub` are accepted sections. A package recorded under `aurora_pub` is accepted by the user's rule that presence in Aurora Pub is sufficient. If the result has `allowed: false`, tell the user that compatibility is uncertain and follow the returned links to inspect the package's physical source and its transitive dependencies. Do not silently mark an unknown name as allowed or write the result into the YAML.

When the user asks to actually add an allowed dependency, find the Aurora Flutter SDK from an explicit path, `AURORA_FLUTTER_ROOT`, or the project's `.aurora-flutter-sdk` file created by `aurora-flutter-setup-project`. Use that SDK's `bin/flutter pub add <name>` in the project; use `dev:<name>` for a development dependency and pass a version constraint only when requested. Do not substitute an upstream Flutter on `PATH`. Report the resolved version from `aurora_pubspec.lock` or `flutter pub deps --json`.

For a native Aurora plugin, read its README and `pubspec.yaml` for project setup, permissions, and build requirements before claiming integration is complete. Device testing is a separate step.
