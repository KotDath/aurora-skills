---
name: aurora-install-psdk
description: Install Aurora Platform SDK on Linux with the official install_aurora_psdk.sh script, selecting a release and targets, checking prerequisites, and verifying chroot tooling. Use when PSDK is missing or its installation is requested.
---

# Install Aurora Platform SDK on Linux

Use one method: the official `install_aurora_psdk.sh`. Reuse conversation and setup answers. This skill works without a project repository. A request for an explanation or command alone does not authorize installation. PSDK installation is independent of the desktop SDK: do not search for, require, or install SDK here, or reuse its BT/MB2 choice.

## Find or choose PSDK

Check a supplied path and the selected project's `.aurora/sdk.json` `psdk` field first. Bounded discovery candidates are `~/AuroraPlatformSDK/sdks/aurora_psdk` and `~/MyPSDKDir/sdks/aurora_psdk`; relevant environment variables and shell aliases may provide additional hints. A PSDK root contains `sdk-chroot`; it differs from the outer installation directory. Do not silently override invalid recorded configuration or conclude PSDK is absent from these checks alone. Validate a found installation before proposing another.

Ask only for missing choices: exact release, target architectures, online source versus an existing offline image directory, outer installation directory, and tooling variant if that release offers alternatives. Use the [official automated installation guide](https://developer.auroraos.ru/doc/sdk/psdk/setup_script) and its linked [release catalog](https://sdk-repo.omprussia.ru/sdk/installers/). Locate a real release directory with matching chroot, tooling, targets, and checksums; layouts differ between releases. Confirm the chroot supports the host architecture; target architecture is a different choice.

Select `--toolchain-suffix` from the actual release filenames and downloaded script's help. The current script can choose unsuffixed tooling for 5.2+; older releases or special variants may require a suffix. Do not blindly force `MB2`, translate a desktop SDK BT choice into `base`, or hardcode a “latest” URL. For 4.x, use available `armv7hl`/`i486` targets rather than assuming 5.x architectures.

## Preflight and prepare

Check Linux distribution, host architecture, free space for downloaded archives and installed components, and write access to the working directory and installation parent. Follow the selected PSDK release's host requirements. Inspect the current installer's required utilities and archive decompressors, including Bash, download tools, `tar`, checksum tools, and `sudo`; report missing packages for the user to install. Do not transfer desktop SDK disk-space requirements to PSDK. The standard chroot installation has no Docker prerequisite.

Choose a new outer installation directory (default `~/AuroraPlatformSDK`). The current official script rejects an existing destination and paths containing spaces. Expand `~` before passing an absolute path. Outside the user's home, the parent must exist and satisfy the script's ownership checks. Report problems instead of mounting disks, changing unrelated ownership, or deleting an existing or partial installation.

Follow the script archive link from the official guide. Download into a dedicated working directory outside the project, inspect archive paths, and extract there. Read the current script and its help before execution. Do not vendor a copy into this skill or pipe a remote response into a shell. Retain the working directory: the installer also downloads large images there and generates an uninstall script.

For offline mode, ensure one release's matching chroot, tooling, requested targets, and published checksums are present, retaining any checksum subdirectory layout. Keep checksum checks enabled for both modes. **Never pass `--ignore-md5-checks` or continue after a mismatch.**

## Run the official installation

Present the resolved source, release, targets, destination, and concrete command. Explain that the script uses `sudo` for chroot operations, changes shell startup files for PSDK aliases/environment, and generates an uninstall script. When the user has requested installation and resolved these choices, proceed without another generic confirmation. For a command-only request, return instructions instead.

Run as the ordinary user from the prepared working directory, using exactly one source argument:

```text
./install_aurora_psdk.sh --input-url <verified-release-directory> --install-dir <absolute-outer-directory> --allowed-targets <comma-separated-architectures>
./install_aurora_psdk.sh --input-dir <absolute-offline-directory> --install-dir <absolute-outer-directory> --allowed-targets <comma-separated-architectures>
```

These are alternatives. Substitute and shell-quote real values, choose one command, and append a suffix only if required. Do not add Ubuntu/HADK chroots or hardware variants unless requested.

Let the user enter any sudo password directly in an interactive terminal; never request it in chat, store it, or pass it through a tool. If user input is unavailable in the agent's terminal, provide the exact prepared command for the user to run and resume afterward. The script may open a new shell at the end; terminal liveness or its final exit code alone does not prove installation succeeded. After a failure, report the stage and inspect partial state before retrying. Do not automatically uninstall or fall back to manual chroot extraction.

## Verify and return

The PSDK root is `<outer-directory>/sdks/aurora_psdk`. Check the executable `sdk-chroot` and its supported invocation, then run `sdk-assistant list` through it, for example `<psdk-root>/sdk-chroot sdk-assistant list`. Use the same interactive sudo handoff if needed. Use the absolute launcher rather than relying on a fresh shell alias. Confirm the expected tooling release and every requested target. Missing targets or an unusable chroot mean incomplete installation.

For an identified existing project being configured, merge the verified absolute PSDK root as optional `psdk` in `.aurora/sdk.json`, preserving unrelated keys. Validate JSON and nonempty absolute path strings; resolve conflicts before replacing recorded choices. Ensure `/.aurora/sdk.json` is Git-ignored and report if already tracked. Do not put a PSDK root in `sfdk`. For standalone installation, write no project metadata. For a planned new project, return the verified path for recording after generation.

Report the actual root, release, verified tooling/targets, working directory and generated uninstall-script path, and pending work. Return to the original requested operation using tools that support PSDK. `aurora-qt-build-project` uses `sfdk`, so do not pass it a PSDK path or install a desktop SDK to complete a PSDK request. The Aurora Flutter fork is a separate tool.
