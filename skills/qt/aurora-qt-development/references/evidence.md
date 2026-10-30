# Evidence and limits

Research performed 2026-10-30. Full official documents were retrieved through `https://developer.auroraos.ru/api/mcp` (`initialize`, `search`, `get_document`); these notes are a synthesis, not copied manuals. The OS documentation baseline is **5.2.1**. This skill does not claim compatibility with every older/newer release.

## Official source map

| ID | Document | What was confirmed |
| --- | --- | --- |
| A1 | [Libauroraapp](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/interface_and_interaction/libauroraapp) | Startup/view ownership, installed resource resolution, application data/cache APIs |
| A2 | [First application code](https://developer.auroraos.ru/doc/5.2.1/software_development/first_experience/first_app_code) | Generated app structure and native/QML entrypoint |
| A3 | [Silica introduction](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/interface_and_interaction/silica/silica_introduction) | QtQuick + Silica, pages, Theme, scrolling and standard controls |
| A4 | [ApplicationWindow](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/interface_and_interaction/silica/silica-types/applicationwindow) | Initial page, page stack, cover and orientation |
| A5 | [Public APIs](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/public_api) | Supported modules, import versions, permissions, deprecated libraries, QtWidgets exclusion |
| A6 | [Desktop requirements](https://developer.auroraos.ru/doc/5.2.1/software_development/guidelines/rpm_requirements/desktop_requirements) | Required X-Application section, identity, permissions, D-Bus activation metadata |
| A7 | [Security profiles](https://developer.auroraos.ru/doc/5.2.1/software_development/guidelines/security_profiles) | Certificate-selected validation profile, profile-dependent capabilities |
| A8 | [Dependency mapping](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/public_api/dependency_connection) | Mapping APIs to spec, qmake, CMake and imports |
| A9 | [KeepAlive](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/system_utils/keepalive/all-types/keepalive) | Suspend prevention subject to lower-level policy |
| A10 | [BackgroundJob](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/system_utils/keepalive/all-types/backgroundjob) | Coalesced timing, finish/disable requirement |
| A11 | [Spec creation](https://developer.auroraos.ru/doc/5.2.1/software_development/guides/packages_configuration/spec_creation) | Build/runtime requirements, CMake-only Conan flow, private library deployment |
| C1 | [CMake FindPkgConfig](https://cmake.org/cmake/help/latest/module/FindPkgConfig.html) | Imported target usage requirements and support since CMake 3.7 |
| Q1 | [Qt C++ attributes in QML](https://doc.qt.io/qt-6/qtqml-cppintegration-exposecppattributes.html) | General NOTIFY semantics only; current upstream Qt 6 syntax is not a target compatibility claim |
| Q2 | [QML property binding](https://doc.qt.io/qt-6/qtqml-syntax-propertybinding.html) | General binding removal on imperative assignment |

Qt 5.6 archive pages were unavailable through the research web tool. Qt 5-style NOTIFY usage was additionally cross-checked in L3; no Qt 6 registration/build macros were adopted.

## Local source map

Projects below are from the user's supplied Qt example collection. Paths are relative to that collection, not installation prerequisites. Git revisions identify the checkout base; dirty files are called out. Do not assume all local code is official or production-ready solely from its name.

| ID | Project and inspected files | Revision / status | Observation |
| --- | --- | --- | --- |
| L1 | `ApplicationTemplate/src/main.cpp` | Base `055559df3a2419b93919d7033db6c398c44092e0`; main and many other files modified | Aurora startup, identity and context object before QML loading; customized keystore reproducer, not a pristine template |
| L2 | `KeepAlive/src/main.cpp`, `qml/KeepAlive.qml`, `qml/pages/MainPage.qml`, `CMakeLists.txt`, `ru.auroraos.KeepAlive.desktop` | `9e7a4fdcdbeaed9433d2aed4d2e0743465e2bd60`; clean | Application shell, Theme, DisplayBlanking, BackgroundJob, separate keepalive control |
| L3 | `Geolocation/src/gpsinfoprovider/gpsinfoprovider.{h,cpp}`, `ru.auroraos.Geolocation.desktop` | `5b5ea6667c2b1e004008c541a2b5df39fc0ee867`; translations modified, inspected files unchanged | QObject properties/signals, nullable sources, start/stop updates, Location/Internet permissions |
| L4 | `ConanTest/conanfile.py`, `rpm/ru.lizik.ConanTest.spec` | No git repository; unversioned local snapshot | PkgConfigDeps and install/deploy flow; contains questionable Conan coordinate in RPM Requires |
| L5 | `AuroraConan/docs/use-conan-packages.md` | `29b3be33f28d890854ba399016c4aa48831b6f10`; unrelated untracked recipe directory | CMake/pkg-config flow, private libraries, QML import path; compared with A11 |

Public example discovery starts at [Aurora's MosHub namespace](https://hub.mos.ru/auroraos/) or MCP `search_code`. This research used the supplied local checkouts; it did not verify every checkout's remote or establish that local HEAD equals the latest MosHub version.

## Conflicts and limits deliberately retained

- L2 executes a network request while its desktop permission list is empty. A6 says Internet is the applicable permission. Reuse the lifecycle mechanism, not that incomplete permission configuration. Runtime behavior was not tested.
- L2 finishes a background job after a timer count while network requests may still be pending. A10 supports finishing after the actual work: production code needs completion/error/timeout tracking.
- L3 `setAvailableSources` creates a source without assigning it to the active provider. Do not copy that as a working provider-switch implementation. Its broader error/recovery behavior was not validated.
- L4 includes a Conan coordinate in RPM Requires; no corresponding RPM capability was verified. Keep recipe coordinates distinct from RPM dependencies.
- L5 contains a package-version prose mismatch and passes an imported target where an include directory is expected. The skill uses the architectural flow, not those fragments verbatim.
- No modified skill example was compiled, packaged, or run on Aurora hardware/emulator in this research. No matching target headers were audited. Availability of a concrete new API still requires reading the selected target SDK/PSDK declarations and building against it.
- This is a representative application-development baseline, not a complete catalog of camera, crypto, Bluetooth, D-Bus, MDM or other APIs. Research the relevant versioned API when a feature needs it.
