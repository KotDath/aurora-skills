---
name: aurora-flutter-add-dependency
description: Decide whether a dependency is allowed for an Aurora Flutter project and add it when requested. Use for package selection, compatibility review and dependency additions; not for porting a rejected native plugin.
---

# Add an Aurora Flutter dependency

Use the project's agent instructions and recorded Aurora Flutter SDK. Reuse prior answers. Onboarding or scaffolding does not authorize adding packages.

## Admission policy

Apply this decision tree to the requested package and resolved version:

Package identity is the exact name and server metadata, not an `_aurora` suffix. The server may contain Aurora ports, ordinary forks, mirrors and transitive packages such as `yaml`, all under their original names. Do not require renaming or a platform suffix for admission.

1. **Available on the Aurora server:** use that distribution. Native code in this port is allowed. The designated server is `https://sdk-repo.omprussia.ru/sdk/flutter/pub`; query `/api/packages/<name>` and select a compatible version from its metadata. Do not substitute a similarly named upstream release or silently change global registry configuration.
2. **Not available on that server:** inspect the actual resolved package sources and transitive dependency closure. Allow only if they contain no native implementation/interop and no `TargetPlatform` constructs. Inspect sources, not only package descriptions or declared supported platforms. Native code includes platform implementations, FFI/native libraries and native bridges. Presence of such code anywhere in the reviewed package sources fails this branch; do not excuse it as an unused platform directory. An unavailable dependency source means insufficient evidence, not approval.
3. **Native code or `TargetPlatform` found outside the accepted server distribution:** do not add/use the package. State the concrete file/symbol that failed the policy. Porting, replacing the package or changing this policy is a separate task, not an automatic fallback.

If a non-server package passes source review, add it for the requested project/version without requiring a permanent allowlist edit or another permission round. Record the selected version, dependency closure and review evidence in the result; do not claim every future version is compatible. Do not modify the curated list unless the user asks.

## Check the designated server

Run `python3 <this-skill-directory>/scripts/check_dependency.py --package <name>`. It performs a read-only request to `https://sdk-repo.omprussia.ru/sdk/flutter/pub/api/packages/<name>`. The collection URL `/api/packages/` is an HTML directory listing; per-package URLs return JSON with versions, pubspecs and archive locations. Successful metadata confirms server presence, not compatibility with every Flutter version.

The checker distinguishes `available_on_aurora_server`, `needs_source_review` (HTTP 404), and `server_check_failed` (network, HTTP or metadata error). `allowed: null` means unknown, not allowed or absent. Retry or report the unavailable check instead of treating an outage as a missing port. Inspect the chosen version's SDK constraints and archive origin before adding it.

Compatibility includes the selected transitive versions, especially an endorsed plugin's backend. An older frontend is not a workaround for an older SDK if it still resolves to a backend with the same higher SDK requirement. Without an actual compatible resolution, report server admission separately from SDK compatibility and leave the latter pending.

The adjacent [checked-dependencies.yaml](scripts/checked-dependencies.yaml) is historical context only. `--offline` reports membership without granting admission; neither list section replaces a live server check or source review for the selected version. The helper does not download source archives, audit code, resolve dependencies or edit the project.

Use the main app-facing package from the Aurora server when that is its distribution model; let the selected fork resolve its backend. Do not replace a requested package with a platform interface or add a random implementation merely to work around admission. If the accepted server package's own instructions require an implementation dependency, apply the same policy to that dependency. Generic federation rules do not override this admission policy. If server availability cannot be established, report the uncertainty; a network error does not establish that a port is absent.

## Add with the selected SDK

Read `flutter` from `.aurora/sdk.json`. If absent, use `aurora-flutter-setup-project --existing --record-only` with the known or user-supplied SDK path; do not generate platform files. If the recorded SDK is invalid, report it rather than switching to PATH. The setup helper's channel-name heuristic is a known limitation, not proof of fork identity.

After admission, run `<recorded-root>/bin/flutter pub add <name>` from the project; use `dev:<name>` for a development dependency and the reviewed version constraint for a source-reviewed package. Do not manually edit generated package configuration or lockfiles. Inspect the resulting source, version and dependency resolution: if it differs from the reviewed selection, reassess before claiming the package usable. Use the same SDK for subsequent commands; do not invoke sfdk for Flutter package operations.

For an accepted Aurora native port, inspect its instructions, permissions and build requirements before claiming integration complete. Report admission basis (Aurora server or source review), resolved version/origin, changes and remaining platform checks. Package admission is not a device-runtime test.
