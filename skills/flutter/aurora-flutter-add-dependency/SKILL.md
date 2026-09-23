---
name: aurora-flutter-add-dependency
description: Add or assess a Flutter package in an Aurora OS project using the Aurora Flutter SDK, Aurora Pub, and the checked dependency list. Use for package additions or compatibility checks, not for creating a project.
---

# Add an Aurora Flutter dependency

Use `scripts/add_dependency.py` for dependency checks and additions. It finds the Aurora Flutter SDK from `--flutter-sdk`, `AURORA_FLUTTER_ROOT`, or the project's `.aurora-flutter-sdk` file. Never substitute an upstream `flutter` on `PATH`.

The packaged [checked-dependencies.yaml](references/checked-dependencies.yaml) is the list to read. `aurora_pub` is a snapshot of the official Aurora Pub index; by this project's rule, a package found in Aurora Pub is supported, including packages with native Aurora implementations. `source_checked_outside_aurora_pub` contains names accepted after source inspection. The script also queries Aurora Pub live so newly published names need not wait for a list update. Do not treat the registry's mere mirror of a package as evidence that every method has been tested on a device; the accepted status here follows the user's registry rule.

For a question about a package, run `--check-only --project <project> --package <name>` and report the decision. To add it, run without `--check-only`; omit `--version` unless the user specified a constraint so Aurora Flutter can choose its compatible version and map an upstream version to a `+N` Aurora port. Use `--dev` for development dependencies. The script reports the exact resolved version and source URI after `flutter pub add`.

If a package is absent from both Aurora Pub and the checked source list, inspect its exact source version and transitive dependencies before calling it supported. An explicit user request can still add such a package with `--allow-unreviewed`; say that its compatibility remains unverified. The script reports `source_review_required` for resolved packages accepted by name from the source-checked list: inspect those exact versions and their dependencies, because the list deliberately has no version pins. `dependency_tree_listed` only means every resolved name appears in Aurora Pub, in the source-checked list, or in the Flutter SDK; it is not a claim that every API was run on a device. A direct package from Aurora Pub remains accepted under the project's registry rule.

For a native Aurora plugin, read its README and `pubspec.yaml` for required permissions, `buildRequires`, and setup steps; apply those steps to the project when the user asked for a working integration. Use the resulting `aurora_pubspec.lock` and `flutter pub deps --json` to describe what was actually selected. Building or device testing is a separate request.
