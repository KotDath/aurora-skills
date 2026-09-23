---
name: aurora-rpm-validate
description: Validate an existing Aurora OS RPM package against its security profile and explain validator errors or warnings. Use for a built package from Qt, Flutter, Web, or another stack; not for compiling or signing it.
---

# Validate an Aurora RPM

Validate the selected `.rpm` artifact with `rpm-validator`. Work from the package path, regardless of the framework that produced it. Speak in the user's language.

## Choose the package and profile

Use an RPM path supplied by the user or the exact artifact(s) produced by the current build workflow. Handle all newly built architectures covered by the request. Do not pass a wildcard that could include unrelated packages or old versions; ask only when several unrelated artifacts remain plausible.

The validator profile must match the developer certificate used to sign the package. Use a profile supplied by the user; otherwise inspect existing signature information with `rpmsign-external dump` when available. If the profile remains unclear in an autonomous workflow, run a provisional `regular` check, report the assumption, and do not present it as definitive validation under an unknown signing profile. For a standalone request where the intended profile materially affects the result, ask. Query the installed validator's `--help` or `--suites` for supported profiles rather than assuming a fixed list.

## Run the validator

Prefer an available `rpm-validator` executable. If it is available only inside Aurora SDK Build Engine, use the user's `sfdk` path or `~/AuroraOS/bin/sfdk` and run `sfdk engine exec rpm-validator -p <profile> <exact-rpm-path>` from a directory inside the SDK shared workspace. If the default `sfdk` is missing, ask for its path. The RPM must be visible in that workspace too; report the constraint if it fails rather than silently moving the package. `apptool validate` is a valid backend when that is the user's available tooling; its arguments are passed through to `rpm-validator`.

Treat validator exit codes distinctly: `0` passed, `1` failed, `2` passed with remarks. Review the full diagnostic output even on success and report warnings, because future Aurora OS releases can reject packages that currently pass with warnings. Report the package path, profile, tool/version, status, and actionable findings. Validation for one SDK release does not prove installation on every Aurora OS release.

Use [`rpm-validator` documentation](https://developer.auroraos.ru/doc/sdk/tools/rpm_validator) for profile and diagnostic details. `sfdk check` additionally runs other quality suites; its aggregate exit status does not replace a direct RPM validator result.
