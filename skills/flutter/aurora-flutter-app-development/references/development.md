# Aurora Flutter application practices

Read [evidence](evidence.md) for the documents, example revisions and unresolved conflicts behind this guidance. General Flutter engineering rules below are distinguished from Aurora-specific integration.

Dependency admission is defined only by `aurora-flutter-add-dependency`: verify the designated Aurora server first; otherwise require source review without native code or `TargetPlatform`. The federation patterns below explain registration for accepted packages or explicitly requested port development; they do not authorize using a rejected dependency.

## Establish a compatible environment

Use the selected Aurora Flutter executable, not whichever upstream `flutter` is on PATH. `flutter-aurora` in the official instructions is an alias for that distribution's `bin/flutter`, not a required executable filename. Record its revision/version, Dart constraints, OS/device release, architecture and selected native build backend. A version number alone does not identify the Aurora fork. Check its origin/provenance and Aurora command support without upgrading it.

The official installation/build pages describe **SDK BT** and, on Linux, **PSDK** as alternative backends. They say a configured `aurora-psdk-dir` takes precedence over `aurora-sdk-dir`. Overview/FAQ content disagrees, and the pages have no version labels; do not infer that every release supports both. Inspect the selected SDK's `config --help`, `build aurora --help` and existing configuration before proposing changes. Reading `.aurora/sdk.json` does not itself configure Flutter. Do not reset a user's backend during a UI change.

The official compatibility table explicitly associates Flutter releases with OS/SDK releases. Check the actual pair; do not infer compatibility from equal major numbers or from an example that compiles elsewhere. See the documented 3.41.4/5.2.1 discrepancy in [evidence](evidence.md).

## Application structure and ownership

| Area | Responsibility / inspection |
| --- | --- |
| `lib/`, assets, `pubspec.yaml` | Dart UI/domain behavior, dependencies, SDK constraints, assets and identity metadata |
| `pubspec.lock` | Resolved dependency versions; preserve the application's lockfile policy |
| `aurora/main.cpp` | Native runner; initialize the matching embedder and register plugins using that SDK's template |
| `aurora/CMakeLists.txt` | Build/install runner, generated plugin integration and bundled assets/libraries |
| `aurora/desktop/*.desktop` | Launcher, application identity, isolation permissions and platform metadata |
| `aurora/rpm/*.spec` | Native build/runtime requirements and RPM contents |
| Generated registrant/CMake files | Output of Flutter dependency discovery, not an independent dependency source |

Local examples use `aurora::FlutterApp` while one official document uses `Initialize`/`RegisterPlugins`/`Launch`. Preserve the selected SDK's runner conventions; these snippets are not interchangeable. Qt compatibility for a plugin is an explicit integration requirement, not a reason to replace the runner with a Qt/QML application's `libauroraapp`/Silica shell.

Some inspected runner, desktop, spec and CMake files explicitly say they will be recreated at the next build unless a marker line is removed. Before editing, determine whether the selected SDK generates the file and whether the change belongs in supported metadata. If a manual override is required, follow that SDK's opt-out mechanism and review the next build's diff. Do not universally remove regeneration markers or edit generated registrants as a permanent fix.

## Resolve the whole plugin chain

Classify each feature by its dependency tree, not its top-level Dart API:

- Platform-independent Dart packages can still impose SDK constraints.
- A Dart implementation using D-Bus is platform-dependent even without C++ code.
- A federated plugin needs a compatible app-facing package, platform interface and Aurora implementation. Inspect the **resolved** manifests and README, not only the package name.
- If the app-facing package endorses an Aurora `default_package`, verify the dependency is resolved and registered. If it does not, add the implementation explicitly according to its instructions. Do not blindly apply both patterns.
- `dependency_overrides` and relative paths in monorepo examples are development wiring. Do not copy them into a separate application whose dependencies differ.

For example, the inspected battery package endorses `battery_plus_aurora`, whose implementation declares a Dart plugin class and `DeviceInfo`. Its example uses local overrides. This establishes that pattern in that revision, not that every pub.dev version has Aurora support.

For package changes, use `aurora-flutter-add-dependency` if available; its policy check is not runtime compatibility proof. If that skill is absent, report the missing admission policy and offer installation in the chosen scope; do not substitute generic compatibility guidance.

## Permissions, identity and packaging

Adding a Dart dependency does not by itself prove that the installed RPM has the required permissions or libraries. Follow the selected plugin's native instructions and inspect the final packaged metadata.

Aurora OS 5.2.1 documentation requires `[X-Application]` identity/isolation metadata and semicolon-separated `Permissions`. For example, networking uses `Internet`, device information uses `DeviceInfo`, and camera use uses `Camera`. Permission availability can depend on the security profile. SDK linking, RPM requirements, sandbox permission and signing are separate checks.

Bad: copy `Permissions=Camera;UserDirs;Audio;Music` from a scanner demo for an unrelated device-information screen.

Better: derive permissions from the actual feature/API, merge them with existing requirements, and verify the installed desktop entry. A battery-only integration may require `DeviceInfo`; it does not justify camera or broad user-directory access. Do not overwrite an existing permission list with this example.

Keep binary/package identity, `Exec`, icons, organization/application fields and generated metadata consistent. Prefer a supported Aurora storage plugin/API for application data; do not hardcode another application's home/data path. Preserve Flutter's bundle installation and selected SDK's dependency-exclusion machinery; blanket RPM exclusions can hide missing dependencies. Review any plugin-supplied exclusions against the libraries actually bundled.

`build aurora` produces an RPM; `run` includes development deployment/signing according to the official guide. A successful build is not proof of distribution signing, policy validation or real-device support.

## UI and app architecture

General Flutter practice: keep widget presentation separate from domain state and a small platform adapter so unavailable capabilities and failures can be tested. Reuse the project's state-management approach rather than introducing a framework merely for a port.

For an Aurora-like UI, evaluate `aurora_controls`; its example uses `AuroraApp`, `AuroraTheme` and `AuroraPageRoute`. Official documentation separates these widgets/themes from `aurora_window_manager` for native transparency and atmosphere integration. Material widgets are also present in inspected applications; Aurora Controls is not established here as a mandatory platform requirement. Check the selected package API and the separate icon license before reusing icons in other-platform builds.

Test keyboard/text input, back navigation, safe areas, rotation, text scaling, locale, loading/error/empty states and long lists on the intended device. Avoid hardcoded screen dimensions; a desktop preview does not establish touch behavior or performance on Aurora hardware.

## Async UI and resource lifetime (general Flutter rules)

These are original illustrative fragments, not compiled Aurora samples. Inside a `State`, assume `deviceService` is the application's adapter, `_status` is its UI state and overlapping requests are disabled by the caller. Import `PlatformException` from `package:flutter/services.dart`.

Bad: a platform reply can arrive after the widget is removed and failures leave no UI state.

```dart
Future<void> refreshStatus() async {
  final status = await deviceService.readStatus();
  setState(() => _status = status);
}
```

Better: perform the asynchronous work outside `setState`, handle expected platform failures, and check widget lifetime before updating.

```dart
Future<void> refreshStatus() async {
  try {
    final status = await deviceService.readStatus();
    if (!mounted) return;
    setState(() => _status = status);
  } on PlatformException catch (error) {
    if (!mounted) return;
    setState(() => _status = 'Unavailable: ${error.code}');
  }
}
```

Localize production messages. For overlapping requests, add cancellation or request-generation tracking so old replies cannot overwrite new state. Cancel subscriptions and release controllers/resources through their supported APIs; `mounted` prevents invalid UI access but does not cancel work. Handle asynchronous cleanup failures according to the controller contract; do not assume `State.dispose` can await them. The local battery sample cancels its subscription, but its initial future callback lacks a mounted check: examples require review too.

Bad: `catch (_) { return; }` around a save operation makes failure look like successful persistence. Better: propagate a typed failure or show an explicit unavailable state. Distinguish `MissingPluginException` from a supported backend reporting an operation failure; investigate resolved implementation/registration before adding a fake success fallback.

## App lifecycle is not widget disposal

Use the selected Flutter version's `WidgetsBindingObserver` or `AppLifecycleListener` for application transitions; remove listeners when their owner ends. Do not use Android-only `reassemble()` camera workarounds as Aurora background handling: reassemble is a development hot-reload hook.

In the inspected embedder source revision labeled 3.41.4, `lifecycle_plugin.cc` maps minimized windows to `inactive`, hidden windows to `hidden`, and ordinary visible windows to `resumed`. This is source evidence for that revision, not a guarantee of installed-device behavior or all synthesized Dart transitions. Code that releases a camera **only** on `paused` needs a target-specific review. Decide which inactive/hidden states should pause the feature, and re-check capability/permissions when resuming; media/background use cases may have different requirements.

Persist important state when it changes instead of relying on a final lifecycle notification: Flutter explicitly does not guarantee every transition before termination. A periodic Dart timer does not establish background-execution permission. For background operation, research the actual Aurora service/plugin policy and test suspend/resume, screen lock and termination on target.

## Development and verification loop

Use the selected executable throughout; `flutter-aurora` below means that executable or a verified alias. Inspect its help before using version-sensitive flags.

1. Inspect resolved dependencies and generated/native files; make the smallest app change.
2. Run its formatter/analyzer and focused unit/widget tests. Use a fake adapter for success, unavailable, failure, delayed response and widget-disposal cases. These tests establish Dart behavior, not native plugin operation.
3. When building is in scope, use `flutter-aurora build aurora --release --target-platform <target>`: documented targets are `aurora-arm` (armv7hl), `aurora-arm64` (aarch64), `aurora-x64` (x86_64). Confirm support in this SDK and use the printed RPM path, not a copied sample path.
4. Run on the selected Aurora device/emulator, checking launcher startup, actual plugin call/event, denied/unavailable hardware, navigation away during pending work, minimize/resume and restart persistence. Native/runner/plugin changes require rebuild/relaunch; hot reload is insufficient evidence.
5. Inspect packaged permissions/libraries and perform validation/signing for the intended distribution workflow. Report host tests, target build, emulator and physical-device checks separately, including skipped checks.

For errors use focused verbose build/runtime logs and `doctor`; redact credentials. Do not begin by upgrading SDK/dependencies, deleting caches or regenerating the runner. The official CLI page lists `drive` and `test`, but integration-runner support must be checked for the selected fork; do not infer Aurora support for upstream-only testing plugins.
