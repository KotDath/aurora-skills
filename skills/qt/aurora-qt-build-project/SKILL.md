---
name: aurora-qt-build-project
description: Build an existing Aurora OS Qt application with sfdk for an installed target, producing RPM packages from a qmake or CMake project. Use when asked to compile, package, or check an Aurora Qt project; not for creating a new project or deploying it.
---

# Build an Aurora Qt project

Build an existing Qt application with the Aurora SDK command-line tool. Speak in the user's language. Use `scripts/build_project.py` for target discovery and the build; do not recreate its command sequence by hand. Run it with `--help` for arguments.

## Resolve the build request

- Use the project path and `sfdk` path already supplied by the user. Otherwise the script checks `~/AuroraOS/bin/sfdk`. If it is absent, ask for the SDK executable path; the script may suggest a `PATH` match but does not silently choose it.
- Identify the requested target or architecture. `x86_64` is for the emulator; `aarch64` and `armv7hl` are device architectures. Do not infer a device's architecture from its name. List installed targets with `--list-targets`; select an exact target from that list. An architecture alone is sufficient when it matches one installed target. If multiple SDK releases match, ask which one. If the user requests a no-questions build without a platform, use an installed `x86_64` target for a smoke build when unambiguous and disclose that choice.
- Default to a release build. Use `--debug` for an explicitly requested debug build. Run `--check` when the user asks for quality or package validation; `sfdk check` is distinct from the `%check` phase of `sfdk build`.

## Run and report

Call the script with `--project`, the chosen `--target` or `--arch`, and optional `--sfdk`, `--debug`, `--check`, or `--build-dir`. By default it creates a sibling build directory named with the full target. It passes the target as a one-command `sfdk -c target=...` option, leaving session and global target settings alone. The build itself may update its SDK target snapshot to satisfy declared dependencies.

If the project is outside the SDK's shared workspace, report the SDK error and ask the user for a workspace-accessible project location; do not relocate or copy it automatically. A shadow build keeps compiled artifacts separate, but project build rules can still edit source files (the qmake template updates translations); inspect and report any resulting source changes. Do not install targets or packages, change global SDK configuration, sign RPMs, or deploy to a device as part of a build request. For unusual project layouts or redirected RPM output, consult [references/sfdk.md](references/sfdk.md).

Report the effective target, source and build paths, build status, RPM paths, and log paths. If `--check` was run, review its output for findings even when it exits successfully: rpmlint can be configured to treat errors as warnings. If the build fails, give the relevant diagnostic and next step. A successful build does not by itself establish that the application runs on a device.
