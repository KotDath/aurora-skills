# Research evidence and limits

Research date: 2026-10-30. The official MCP completed initialization and full `get_document` retrieval after `get_ext_tools_list`/`search`. Flutter extension search results have `version: null`: they are **unversioned documentation**, even when the body names particular releases. This is a representative study, not a complete platform certification.

## Official documents actually read in full

All Aurora URLs below were retrieved through MCP, not inferred from search snippets.

| Document | Supported use in this skill |
| --- | --- |
| [Platform](https://developer.auroraos.ru/doc/extended/flutter/about_flutter/platform) | SDK/PSDK/framework/embedder roles; PSDK-centric description conflicts with installation page |
| [Components](https://developer.auroraos.ru/doc/extended/flutter/about_flutter/components) | Engine, embedder, SDK and plugin separation |
| [Packages](https://developer.auroraos.ru/doc/extended/flutter/about_flutter/packages) | Pure Dart vs platform-dependent dependencies, non-endorsed implementation instructions, Qt compatibility example |
| [Development](https://developer.auroraos.ru/doc/extended/flutter/flutter_development) | Native platform directory, plugin README, permissions/spec, device and deployment workflow |
| [Installation](https://developer.auroraos.ru/doc/extended/flutter/flutter_development/install) | 3.41.4 distribution example, SDK BT/PSDK alternatives, alias and configuration, precedence of PSDK setting |
| [Build an application](https://developer.auroraos.ru/doc/extended/flutter/flutter_development/hello_world) | App structure, targets, RPM and development signing |
| [CLI support](https://developer.auroraos.ru/doc/extended/flutter/support/flutter) | Analyze, build, run, logs, doctor, test/drive command inventory |
| [Flutter FAQ](https://developer.auroraos.ru/doc/extended/flutter/faq/flutter) | Qt compatibility, transitive native dependencies; inconsistent host-support and runner examples |
| [Compatibility](https://developer.auroraos.ru/doc/extended/flutter/about_flutter/compatibility) | Explicit Flutter 3.27.3–3.41.4 to OS/SDK release matrix |
| [Aurora Controls](https://developer.auroraos.ru/doc/extended/flutter/about_flutter/ui_kit) | Optional widgets/themes, window-manager separation, icon license and official MosHub repository links |
| [Desktop requirements, OS 5.2.1](https://developer.auroraos.ru/doc/5.2.1/software_development/guidelines/rpm_requirements/desktop_requirements) | Identity, sandbox metadata, permissions and profile distinctions |

General Flutter references read separately: [setState](https://api.flutter.dev/flutter/widgets/State/setState.html) (synchronous state update, disposal/cancellation), [AppLifecycleState](https://api.flutter.dev/flutter/dart-ui/AppLifecycleState.html) (observers and potentially skipped notifications), [testing overview](https://docs.flutter.dev/testing/overview) (unit/widget/integration distinction). These describe Flutter generally and do not establish Aurora's native behavior or testing-plugin support.

## Local sources actually inspected

Paths are relative to the user-provided Flutter collection; they are evidence identifiers, not mandatory installation locations. All three plugin checkouts below were clean when inspected. Their remote provenance/latest upstream status was not independently established.

| Checkout/revision | Files inspected | Finding |
| --- | --- | --- |
| `plugins/battery_plus_aurora`, `5226ad181c2734b8476fe67b101c521d0d458a90` | `packages/battery_plus/example/{pubspec.yaml,lib/main.dart,aurora/main.cpp,aurora/CMakeLists.txt,aurora/desktop/ru.aurora.battery_plus_example.desktop,aurora/rpm/ru.aurora.battery_plus_example.spec}`; app-facing and implementation `pubspec.yaml` | Endorsed local fork, monorepo overrides, Dart plugin/D-Bus dependency with DeviceInfo permission, generated-file markers, subscription cancellation and an unchecked initial future callback |
| `plugins/qr_code_scanner_aurora`, `d73a0d48124de2f4b47250c29513e4a61e08b1be` | `packages/qr_code_scanner/example/{pubspec.yaml,lib/main.dart,aurora/main.cpp,aurora/CMakeLists.txt,aurora/desktop/ru.aurora.qr_code_scanner_example.desktop,aurora/rpm/ru.aurora.qr_code_scanner_example.spec}` | Native runner/packaging; broad permissions, Android-specific reassemble workaround, unchecked async UI updates and old Dart constraints are not production recommendations |
| `plugins/aurora-controls`, `71a59bf43a6421022d152511bf949275f926c8e4` | `example/{pubspec.yaml,lib/main.dart,aurora/main.cpp,aurora/CMakeLists.txt,aurora/rpm/ru.auroraos.aurora_controls_example.spec}` | AuroraApp/theme/page route with Material components; framework and native entrypoints remain separate |
| `embedders/embedder-3.41.4`, `0d68d41615ba13862d143b66d52ee7bb2bada4a6`, clean | `flutter/shell/platform/aurora/plugins/lifecycle_plugin.cc`; initial public API declarations in `flutter/shell/platform/common/public/flutter_aurora/flutter_aurora.h` | Actual window-visibility to lifecycle message mapping; native API exists separately from Dart/framework APIs |

The embedder directory label is not a verified release tag/binary match. Its lifecycle mapping is established for the recorded commit only. No claim is made that a particular installed device runs it. A remote Flutter `git ls-remote` request stalled during research; this study relies on the explicitly recorded local sources rather than claiming a fresh upstream checkout.

## Conflicts deliberately not flattened into rules

- Installation/build pages recommend SDK BT and offer PSDK on Linux; platform overview says builds use PSDK, and FAQ says Linux-only. Extension pages lack version labels. The skill directs the agent to the **selected SDK's capabilities/configuration** instead of treating publication order as known.
- Installation names SDK **5.2.1.200** and an archive named Flutter **3.41.4**, while the compatibility matrix lists **3.41.4** against OS/SDK/PSDK releases only through **5.2.0**. The 5.2.1 pairing requires release-specific confirmation; this study did not establish it.
- Packages documentation shows `Initialize`/`RegisterPlugins`/`Launch`; FAQ and local examples use `FlutterApp`. No universal runner replacement or migration is recommended.
- Package docs describe manually adding non-endorsed implementations, but the inspected battery fork endorses its Aurora implementation. Registration advice must follow the resolved manifest, not a universal add-two-packages rule.
- Local battery implementation requires Dart `^3.8.1` and Flutter `^3.35.7`, stronger than its app-facing example's minimum constraints. The scanner example requires Dart `<3.0.0`. Neither example's presence proves it resolves on Flutter 3.41.4.
- Desktop docs explain `silica-qt5` in terms of Silica, while Flutter examples contain that launcher metadata without a QML UI. Preserve the selected runner/template metadata; do not infer a requirement to rewrite Flutter UI in Silica.
- Overview/build prose can imply a generated RPM is already valid/signed, while the build guide also says the resulting RPM needs signing. Distinguish `build`, development `run`, policy validation and distribution signing; inspect the actual artifact/workflow.
- Official FAQ's fixed flutter_map tuning values were not adopted as universal performance rules: package version, workload and device measurements were not verified.

## Validation limits

No example was compiled, installed or run on an Aurora target in this research. The authored good/bad fragments are original educational code, not copied tested samples. No selected PSDK header audit or exhaustive native capability matrix was performed. The embedder lifecycle source was read but not exercised; exact runtime delivery/synthesized Dart states remain target checks. SDK toolchain configuration, local examples and global agent configuration were not changed.

The separately inspected local Flutter checkout at `ff37bef603469fb030f2b72995ab929ccfc227f0` did not expose Aurora tooling/templates in the searched conventional paths; it was not accepted as a verified Aurora SDK. A version string or a channel-name heuristic alone is insufficient provenance. Documentation uses `flutter-aurora` as an alias and does not establish that all official distributions report a channel containing `Aurora`.
