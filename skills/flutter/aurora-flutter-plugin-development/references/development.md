# Plugin architecture, registration and packaging

## Choose the bridge from the service, not from the word “plugin”

Dependency admission is defined only by `aurora-flutter-add-dependency`: verify the designated Aurora server first; otherwise require source review without native code or `TargetPlatform`. The federation patterns below explain registration for accepted packages or explicitly requested port development; they do not authorize using a rejected dependency.

The official guides describe four routes. Preserve the existing public Dart API and other platform implementations when porting.

| Route | Appropriate evidence/design | Aurora-specific work |
| --- | --- | --- |
| Dart D-Bus | A documented service exposes the required operation; a native wrapper adds no value | Correct bus, service/interface/object path, generated XML bindings, permissions, cancellation and client lifetime |
| Platform channels | Native APIs or embedder features need a Dart message interface | Codec contract, native registration, target library and error/results lifetime |
| Channels + Qt | Required Qt APIs or Qt signals supply the feature | Selected wrapper generation, Qt integration in the host runner, target Qt dependencies, QObject affinity and event-loop lifecycle |
| FFI | A C ABI library already exists or is a suitable narrow boundary | Exported C symbols, generated bindings, ownership, ABI/architecture and bundled shared library |

A Dart-only platform implementation can still be Aurora-specific: the inspected battery backend uses D-Bus and `dartPluginClass` without a C++ plugin. FFI and Qt are not mutually exclusive, but an FFI call does not establish the correct Qt application/event-loop/thread context. Do not replace supported asynchronous service APIs with blocking UI-isolate calls.

Sources: official [D-Bus](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/dbus), [channels](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/platform_channels), [Qt](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/platform_channels_qt), [FFI](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/ffi) guides; inspected battery, path-provider, sensors and SQLite implementations in `evidence.md`.

## Follow the whole registration chain

Read the resolved app-facing package, platform interface and Aurora implementation manifests, not just the consumer's pubspec. Check interface versions, overrides and Dart/Flutter minimum constraints. In a federated implementation, `implements` identifies the app-facing plugin; `dartPluginClass` points to Dart registration which assigns the platform-interface instance. Native registration is a separate step. An endorsed implementation may already be selected by the app-facing package's `default_package`; a non-endorsed implementation needs an explicit dependency. Do not add duplicate manual registration to fix a dependency-selection problem.

In the inspected collection:

- Battery uses a Dart `registerWith()` and an endorsed Aurora backend in its app-facing fork.
- Path-provider declares both `dartPluginClass` and `pluginClass`, bridges a Dart method channel to a native implementation and uses older `flutter::` headers.
- The Qt guide documents `pluginEntryPointHeader`, `pluginEntryPoint`, `useQt`, `buildRequires` and `permissions`; the sensors implementation uses a `FlutterAuroraPluginContext*` entrypoint and `cw::PluginRegistrarManager`.
- SQLite's native-library package declares `ffiPlugin: true`; it builds a library rather than supplying a method-channel implementation.

These are different supported patterns in their respective sources, not fields to combine into every manifest. Compare the selected Aurora SDK's template and generated registrant. Regenerate through its tooling instead of editing generated registrants as the durable fix. Investigate missing-plugin failures in order: resolved package → manifest → Dart registration → native entrypoint/export → linked/bundled library → exact channel/method name. Native changes require rebuilding/restarting the native application; Dart hot reload is insufficient evidence.

## Avoid mixing wrapper generations

The channel guide explicitly discusses Flutter 3.35.7 with `cw::BasicPlugin` and `registrar->app()`. The inspected 3.41.4-labelled source also has `cw::` and `client_wrapper/` headers. The local path-provider uses `flutter::BasicPlugin`, `registrar->engine()` and `<flutter/...>` headers. Even the official Qt page mixes a `cw::` plugin with an older `FlutterApp`/`flutter::PluginRegistrar` runner excerpt. Treat that as a compatibility question, not a complete paste-ready recipe.

Keep the runner, generated registration, plugin headers, CMake integration and link targets from one verified generation. `FlutterApp` and `Initialize`/`RegisterPlugins`/`Launch` examples must not be merged mechanically. Qt is an optional plugin dependency, not an instruction to replace Flutter UI with QML. Resolve SDK BT vs PSDK through the chosen Aurora Flutter distribution; PSDK is not universally mandatory.

## Native dependencies and permissions belong to the consumer too

The plugin's CMake links target libraries; RPM `BuildRequires` makes development packages available during the consumer build; runtime dependencies and bundled libraries must exist on the installed target. These are separate checks. Where the selected Flutter tooling supports plugin `buildRequires`/`permissions`, inspect the generated consumer spec/desktop files to verify propagation. Older guides edit the example's metadata manually. Preserve the toolchain's generated-file conventions and request only capabilities actually used.

The Device Info guides require `DeviceInfo`; the Qt network guide uses `Internet`; local path-provider declares `UserDirs`. These are feature-specific examples, not a universal permission set. Verify the target release's service access and sandbox rules. Successful calls under a developer shell do not demonstrate access from the packaged sandbox.

The local SQLite package builds `libsqlite3.so` and copies it to the bundle's `lib/`. Its source-download/build recipe is an example, not a verified reproducible build or ABI guarantee. Check the packaged ELF architecture, exported symbols, required shared libraries and loader path, including release mode. A library that builds but is absent from the RPM is not a working FFI plugin. Do not bundle arbitrary host `.so` files.

## Validate the public contract at three levels

1. Dart tests: names, argument/result types, nullable values, unknown methods, platform errors and interface registration.
2. Target compilation/packaging: chosen architecture and wrapper generation, native symbols, generated registration, consumer dependencies and permissions.
3. Aurora execution: example loads the real backend, actual service success/denial/unavailability, stream cancel/relisten and shutdown while work is pending. Check sensor units/timebase and semantics against the public API, not just nonempty output.

Host mocks establish serialization/control flow only. Record what was compiled, what ran on a target and what remains unverified. Use `aurora-flutter-setup-project` only when generation is requested; use the dependency skill for additions, if available. See `native-lifecycle.md` for callback rules and `examples.md` for reviewed patterns.
