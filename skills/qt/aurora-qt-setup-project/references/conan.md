# Aurora CMake + Conan scaffold

The integration follows the user's Aurora OS wakeword example and the
[official Conan package guide](https://developer.auroraos.ru/doc/extended/conan/conan_packages).
It uses an external distribution pinned in `rpm/version.config`, starting at
`2.22.0`, rather than requiring Conan to be installed on the host or as an SDK RPM.

## Create the project

```bash
python3 <this-skill-directory>/scripts/setup_project.py \
  --build-system cmake --conan \
  --organization com.example --app-name MyApplication \
  --output <new-directory>
```

Use `--conan-version <version>` when the user explicitly selects another external
Conan 2 release, at least 2.22.0. Distribution availability for the chosen SDK
and architecture must be established before claiming a build is supported.
qmake with Conan is not supported by this workflow. Existing projects are not
migrated by the scaffolding script.

## Generated integration

- `conanfile.py` has an empty `requires` tuple and uses `PkgConfigDeps`.
- `rpm/version.config` pins the distribution version. `rpm/load-conan.sh` finds
  the SDK workspace and downloads the matching distribution into its
  `.cache/AuroraTools/<SDK-major>/conan/<version>/<host-architecture>/` cache
  only when its `rpm-macros` file is absent. It runs inside the SDK/PSDK during
  RPM processing, not as an arbitrary host-side setup command.
- The RPM spec loads that macro file, runs `%conan_install` before
  `%conan_cmake`, then `%ninja_build`. Installation runs `%ninja_install` and
  `%conan_deploy_libraries`.
- CMake retains its RPATH to `${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}/lib`.
  `%define _cmake_skip_rpath %{nil}` prevents the RPM CMake macro from removing
  it. The deployment tool copies libraries needed by the app and packaged QML
  modules into the application's private data directory.
- `__provides_exclude_from` prevents those private libraries from being advertised
  as system libraries. The empty scaffold has no `__requires_exclude` list.
- CMake lists the recipe, bootstrap, version pin, and retained BSD license in a
  source-only `conan_files` target so they are visible in the IDE.

The bootstrap keeps the cache layout and RPM macro contract used by wakeword,
while rejecting failed downloads/extractions with an RPM error. Its original
Open Mobile Platform BSD-3-Clause attribution is retained in the asset and
generated source tree. No paths to the user's wakeword checkout are required.

## Adding a library later

Scaffolding leaves dependencies empty. If adding one is requested later, treat
the recipe, CMake linkage, and RPM packaging as one change:

1. Verify the actual package and version on the configured Aurora Conan server;
   use a confirmed reference such as `<package>/<version>@aurora` rather than
   inventing a version or requesting a local source build.
2. Add it to `requires`, resolve it with the Aurora distribution in the selected
   SDK, and inspect the generated `.pc` files. The pkg-config module can differ
   from the package name.
3. Add `pkg_check_modules(<MODULE> REQUIRED IMPORTED_TARGET <actual-module>)` and
   link `PkgConfig::<MODULE>` in CMake. QML packages can also require the generated
   `lib/qmlplugins` import path in the application.
4. Inspect the actual deployed shared-library closure and resulting RPM
   requirements. Exclude requirements satisfied by packaged private libraries
   without suppressing genuine SDK/system requirements. Recheck this closure
   when removing or changing dependencies.

The wakeword app's ONNX Runtime requirement, multimedia features, and broad
`__requires_exclude` expression are application-specific. They do not belong in
an empty scaffold. This skill does not provide a dependency-management CLI or
automatically calculate those exclusions.

## Verify

Use `aurora-qt-build-project` for an explicitly requested build. First builds
may need network access for the distribution and binary packages. Inspect the
resulting RPM, executable RPATH, private libraries, and requirements before
claiming a dependency is packaged correctly. Scaffold checks alone establish
file/identifier consistency, not successful cross-compilation or device behavior.
