---
name: aurora-qt-development
description: Implement, debug, and review Qt/QML application code for Aurora OS. Use for screens, C++ models, platform APIs, lifecycle bugs, or CMake/Conan integration in an Aurora application. Excludes scaffold-only, build-only, and Flutter plugin tasks.
---

# Develop an Aurora Qt application

Read project instructions and reuse its identity, stack, SDK and target selection. This skill implements application behavior; use `aurora-qt-setup-project` for a requested scaffold and `aurora-qt-build-project` for target builds. Resolve those skills by name when needed; an existing project does not require onboarding again.

Before choosing platform APIs, load `aurora-platform-context` by name and read its source-selection policy. For application code, read [development practices](references/development.md): the Aurora shell, UI, storage, permissions and lifecycle, followed by explicitly identified general Qt guidance. For native dependencies or CMake/Conan changes, also read [packaging](references/packaging.md). [Evidence](references/evidence.md) records the exact documentation baseline, inspected local files, contradictions and verification gaps.

Establish the relevant target OS release, architecture, Qt/QML imports and security profile from project/toolchain evidence. Distinguish SDK release from device release. Preserve the existing Aurora startup and public API constraints; do not translate a desktop/Qt 6 example mechanically into this target. Header availability, permitted API use and runtime permission are separate checks.

Implement the requested behavior with shared domain state behind pages and cover. Preserve the selected build system; ordinary logic does not require adding dependencies. If requirements imply a build-system change (for example the documented CMake-only Conan flow), explain the concrete dependency before changing it.

Verify proportionally: focused logic tests, selected-target compilation, packaging checks and emulator/device behavior as available. For platform access, cover unavailable/denied/error states. For background operations, cover cancellation and completion. Report separately what was inspected, tested, compiled, packaged and exercised on Aurora; a generated RPM is not runtime proof. Cite versioned sources for consequential platform choices and name unresolved conflicts rather than silently treating local examples as authoritative.
