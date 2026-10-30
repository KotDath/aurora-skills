# Research evidence and limits

Research date: 2026-10-30. This is a representative source study, not an audit of every plugin or a certification of an SDK release. Paths below are relative to the supplied Flutter collection; they identify evidence, not required installation locations.

## Official sources

The official MCP at `https://developer.auroraos.ru/api/mcp` completed initialization, search and full `get_document` retrieval for all four guides below. Their search results have `index: ext_docs`, `version: null`; the content is unversioned even where it names Flutter 3.35.7. The retrieved text, including code, was read; claims do not rely solely on snippets.

- [Platform channels](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/platform_channels): package/native/example structure, method channel and `cw::BasicPlugin`, application wrapper (explicitly 3.35.7).
- [Platform channels with Qt](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/platform_channels_qt): `plugin_qt` template (3.35.7 onward according to the page), EventChannel, Qt integration, manifest/build/permission metadata; contains a mixed-generation runner example.
- [D-Bus](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/dbus): direct Dart service access, XML generation and DeviceInfo permission. Its `busctl --user` discovery example and system-bus introspection/client are inconsistent; verify the actual documented service bus rather than copy that discovery command.
- [FFI](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/ffi): `plugin_ffi`, C ABI/bindings, library build and DeviceInfo permission. Its memory-management example has the defects recorded below.

General references opened separately: [Flutter channels](https://docs.flutter.dev/platform-integration/platform-channels), [package/plugin development](https://docs.flutter.dev/packages-and-plugins/developing-packages), [Dart C interop](https://dart.dev/interop/c-interop). These inform general contracts; their current upstream templates and platform-specific threading examples are not proof of Aurora support. In particular upstream now recommends `package_ffi` since 3.38, while the Aurora guide uses `plugin_ffi`: choose the verified Aurora SDK's capabilities rather than mechanically migrating templates.

## Inspected local implementations

| Checkout / commit | Files read | What the skill derives |
| --- | --- | --- |
| `plugins/battery_plus_aurora` / `5226ad181c2734b8476fe67b101c521d0d458a90` | `packages/battery_plus_aurora/{pubspec.yaml,lib/battery_plus_aurora.dart}`; app-stage evidence covers app-facing manifest/example | Dart-only federated registration, D-Bus calls/signals, DeviceInfo metadata, cleanup/fallback caveats |
| `plugins/path-provider-aurora` / `c07d47320786bd91c2d9cf14ee341d94360c462b` | `pubspec.yaml`, `lib/path_provider_aurora.dart`, `aurora/{path_provider_aurora_plugin.cc,path_provider_aurora_plugin_impl.h,path_provider_aurora_plugin_impl.cc,CMakeLists.txt}` | Combined Dart/native registration; older flutter namespace; target/embedder paths rather than arbitrary host paths |
| `plugins/sensors_plus_aurora` / `0914d71ffef723e815ba655b974a69059bd97ed1` | `packages/sensors_plus_aurora/pubspec.yaml`, `aurora/{sensors_plus_aurora_plugin.cpp,sensors_plus_aurora_plugin.h,CMakeLists.txt}` within that package | cw entrypoint, Qt sensor events, separate sinks, shared accelerator subscription, target build/permission metadata |
| `plugins/sqlite3_flutter_libs_aurora` / `34e613df97aa65765b976971c1ed61db4f95577a` | `pubspec.yaml`, `aurora/CMakeLists.txt`, `aurora/3rdparty/sqlite3/CMakeLists.txt` | ffiPlugin library packaging; SQLite source generation, target library and bundle copy |

These tracked files had no local changes at inspection; sensors had an untracked `.opencode/` directory which was not used as platform evidence. Remote origins/latest upstream status were not independently verified. A local fork is an implementation example, not automatically an official requirement. No plugin/example files were changed.

## Embedder implementation

Official source location: [Aurora Embedder](https://hub.mos.ru/auroraos/flutter/aurora-embedder). Local checkout `embedders/embedder-3.41.4`, commit `0d68d41615ba13862d143b66d52ee7bb2bada4a6`.

Inspected under `flutter/shell/platform/common/client_wrapper/`:

- `include/client_wrapper/basic_plugin.h`: synchronous result application, Preprocess hook.
- `include/client_wrapper/{method_result.h,engine_method_result.h}` and `core_implementations.cc`: one completion, pending result destructor warning, duplicate reply guard, reply callback thread comment, messenger handler ownership.
- `include/client_wrapper/{event_channel.h,method_channel.h}`: explicit unregistration responsibility; listen replacement invokes cancel; sink lifecycle.
- `include/client_wrapper/{plugin_registrar.h,binary_messenger.h}` and `plugin_registrar.cc`: raw borrowed messenger lifetime, shared plugin ownership, Release before messenger destruction.

The directory's version label is not a verified SDK-to-binary mapping. These are facts about that commit, not guarantees for every release. No blanket cross-thread event sending rule was established.

## Conflicts and unsafe examples

- Official channels/Qt content uses `cw::`, while the Qt runner excerpt uses `FlutterApp` and `flutter::PluginRegistrar`; local path-provider also uses the older wrapper. Keep generations coherent and recheck templates for the chosen SDK.
- Qt guide initialization reads `m_manager` while initializing `m_state`, although declaration order places `m_state` first. The skill does not copy this constructor. Initialize Qt objects before querying them.
- Official FFI `copyString` allocates `QString::length()+1` bytes then copies UTF-8; non-ASCII output can need more bytes. The allocation is `new[]`, whereas Dart registers `calloc.free`. The error path returns a literal also sent to that deallocator. These are code-review findings, not observed runtime crashes. The replacement demonstrates one allocation/free contract and byte sizing.
- Official D-Bus code and battery request paths close clients only after successful awaits; exceptions can skip cleanup. Battery stream cleanup is after its loop rather than a finally block. The skill recommends cancellation/error-safe ownership instead of adopting tutorial cleanup verbatim.
- Battery's silent power-save fallback and sensors' software gravity/rate/unit/time conversions are implementation choices requiring API semantics/device checks, not platform truths.
- Local SQLite build flags and unchecksummed source download were not adopted as a production build recipe.

## Validation actually performed

Skill frontmatter and local reference links were checked. The exact authored C++ ownership fragment in `examples.md` was extracted, compiled with C++17 `-Wall -Wextra -Werror -fsanitize=address`, and run on the host for ASCII, Cyrillic/emoji, empty input, null input and matching deallocation. The test driver called `label_copy` for each input, asserted byte equality/null and called `label_free`; compilation and execution both exited 0. Command: `c++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address <temporary-test.cpp> -o <temporary-test>` followed by the resulting executable. Combined AddressSanitizer/UndefinedBehaviorSanitizer linking initially failed because the host's `libubsan.so.1.0.0` was missing; no UBSan result is claimed. Allocation-failure injection, generated Dart bindings, target ABI and service calls were not tested.

No Aurora compilation, device execution, sensor measurements, teardown stress test, or selected PSDK header audit was performed. No global configuration or SDK was changed. Wrapper/session/permission behavior beyond the cited sources remains a target validation task.
