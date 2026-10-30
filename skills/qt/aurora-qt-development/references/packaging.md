# Native dependencies, CMake and Conan

Evidence baseline: Aurora 5.2.1 [spec guide](https://developer.auroraos.ru/doc/5.2.1/software_development/guides/packages_configuration/spec_creation), [dependency mapping](https://developer.auroraos.ru/doc/5.2.1/software_development/reference/public_api/dependency_connection), and local AuroraConan documentation at the revision recorded in [evidence](evidence.md). Recheck for the selected target/tooling; do not change a project's working bootstrap merely to match a different example.

## Three different dependency layers

| Layer | Meaning | Check |
| --- | --- | --- |
| CMake/qmake | Compile/link and installed resources | Selected target headers, Qt modules, pkg-config entries |
| Conan recipe | Library coordinates and target binary selection | Recipe, settings, Aurora remote/package availability |
| RPM spec | Build environment and installed runtime contents | `BuildRequires`, `Requires`, `%install`, `%files`, ELF dependencies |

A Conan reference such as `name/version@aurora` belongs in the recipe. It is not automatically an RPM `Requires` name. Do not paste that coordinate into the spec without an actual RPM capability proving it exists. The inspected local ConanTest does this; it is a cautionary example, not a template to copy.

The official 5.2.1 Conan application workflow supports **CMake, not qmake**. Preserve qmake for ordinary qmake applications; if Conan becomes a requirement, explain and implement the needed build-system change within the requested scope. This describes the supported Aurora integration, not a claim that custom Conan/qmake plumbing is technically impossible. Host Conan availability does not prove target integration.

## Maintain the complete dependency chain

The researched Aurora flow uses `PkgConfigDeps`, `conan-install-if-modified` before CMake, and the generated directory in `PKG_CONFIG_PATH`. CMake resolves the library's actual pkg-config module (which need not equal its Conan name). Link an imported `PkgConfig::...` target with `target_link_libraries`; do not put a CMake target name into `target_include_directories` as though it were a filesystem path. Imported targets carry usage requirements. CMake documents this form from 3.7 onward; check the selected CMake version before using it ([FindPkgConfig](https://cmake.org/cmake/help/latest/module/FindPkgConfig.html)).

Retain the existing pinned tooling/bootstrap in generated projects. The documentation snapshot describes `BuildRequires: conan`; it does **not** prove that one fixed Conan version is required for every Aurora release. Verify the project's actual helper and target repository before adjusting it.

Building is only part of deployment:

- Set the executable's runtime search path consistently with the package's private library location, normally `/usr/share/<package>/lib` in this documented flow.
- Deploy required shared libraries with the matching Aurora helper during `%install` and include the directory in `%files`.
- The documented deploy helper follows linked shared libraries. Libraries loaded dynamically, QML plugins and non-library assets need explicit inspection; do not assume everything is copied.
- If a Conan QML module is delivered in `lib/qmlplugins`, make its installed import directory visible to the QML engine before loading the root QML; check the package actually supplies that layout.
- Private-library `Provides`/`Requires` filtering must match libraries actually bundled. Do not reuse a demo's broad regex list to conceal a missing system dependency.

Check ELF dependencies/RPATH, the RPM file list and launch on the intended target. Cross-compilation succeeding while a library is absent from the RPM is not a successful integration.

For a new platform API, use the versioned dependency table to identify both build/link requirements and QML runtime packages, then check `.desktop` permissions separately. Prefer public supported APIs; a header existing in a sysroot does not establish that application policy permits its use.
