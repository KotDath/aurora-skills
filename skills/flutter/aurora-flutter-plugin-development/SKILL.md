---
name: aurora-flutter-plugin-development
description: Implement, port, debug, and review Aurora Flutter plugins using D-Bus, platform channels, Qt, or FFI. Use for Dart/native contracts, plugin registration, missing Aurora backends, callbacks, or native lifecycle bugs. Excludes ordinary Flutter app UI and scaffold-only tasks.
---

# Develop an Aurora Flutter plugin

Read the plugin's Dart API, `pubspec.yaml`, Aurora native sources, build metadata, example and tests. Preserve existing platform implementations. Native CMake in a Flutter plugin does not make it a Qt application.

Before choosing APIs, load `aurora-platform-context` by name and read its source-selection policy. Read [architecture and registration](references/development.md) for bridge selection, federated packages, wrapper generations and consumer packaging. For asynchronous calls, streams or Qt, read [native lifetime](references/native-lifecycle.md). Read [reviewed examples](references/examples.md) for D-Bus cleanup, reply ownership and FFI allocation. For API mismatches or missing source, read the Flutter/embedder reference in `aurora-platform-context`. [Research evidence](references/evidence.md) records exact documents/commits, conflicts and validation limits; consult it before treating an example as a release guarantee.

Retain the existing channel/Qt/FFI design unless the task requires changing it. If a new plugin needs a design choice, consider direct Dart D-Bus for a documented service, platform channels for message-based native APIs, Qt integration for required Qt APIs, or FFI for a suitable C ABI. Confirm actual support in the selected Aurora Flutter SDK. Use `aurora-flutter-setup-project` only for requested generation, and `aurora-flutter-add-dependency` for dependency changes.

Specify the Dart/native contract before editing: method names, argument/result types, error codes, unsupported operations, ownership and cancellation. Implement the actual Aurora backend and applicable Dart/native registration; a generated directory or platform declaration alone is not a completed port.

Test serialization and errors at the Dart boundary, compile native code for the selected target, and exercise the plugin's example on Aurora when available. Include unknown methods, invalid arguments, platform errors and teardown with in-flight work. Report host mock tests, native compilation and real platform execution separately; explicitly identify any untested path.
