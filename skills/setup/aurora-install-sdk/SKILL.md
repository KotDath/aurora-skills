---
name: aurora-install-sdk
description: Check a Linux host and download an official Aurora SDK BT or MB2 installer for a chosen release, guide the user's graphical installation, and verify sfdk afterward. Use when the desktop SDK is missing or its installation is requested.
---

# Install Aurora SDK on Linux

Prepare the official installer; the user performs the graphical installation. Reuse answers from the conversation or `setup-aurora-skills`. This skill also works without a project repository. A request for advice or a download link alone does not authorize a download.

## Resolve the installation

Check a supplied SDK path or the selected project's `.aurora/sdk.json` `sfdk` field first, then `~/AuroraOS/bin/sfdk` and a bounded `command -v sfdk` lookup. Validate candidates with `--version`. Do not silently replace an invalid recorded path or select between multiple installations. Finding nothing here means “not found in checked locations.”

Ask only for missing choices:

- Exact SDK release, informed by the target OS and official compatibility guidance. Do not assume the newest release or use `5.2.1.200` as a universal default.
- **BT or MB2**. Explain the difference using that release's documentation; recommend BT when the documentation recommends it, honoring an explicit MB2 choice.
- Online or offline installer, download directory, and intended installation directory. Host CPU architecture selects the installer; device architecture selects build targets later.

Consult the official [SDK selection guide](https://developer.auroraos.ru/doc/sdk/app_development/setup/setup_linux/download_sdk), [Linux requirements](https://developer.auroraos.ru/doc/sdk/app_development/setup/setup_linux/system_requirements), and [installer launch guide](https://developer.auroraos.ru/doc/sdk/app_development/setup/setup_linux/launch_sdk_install). Match documentation to the chosen release: requirements and build engines change. For other host systems, give the official platform instructions and explain this skill's Linux scope.

## Check the host before downloading

Use read-only probes for distribution (`/etc/os-release`), host architecture (`uname -m`), user privileges, RAM, graphical session, free space, and write access. Check both the download and installation filesystems, using the nearest existing parent. Allow space for the installer, unpacked SDK, and temporary files. Compare results with the selected release's documented requirements; distinguish actual blockers from recommendations and unsupported distributions. Check the installer GUI libraries specified for that distribution. Report missing packages rather than running package-manager commands automatically.

For a Docker build engine, check both the executable and current user's daemon access (`docker --version`, then a bounded `docker info`, for example with `timeout 15s`). If absent, say plainly in the user's language: “Docker не установлен. Установи Docker, затем продолжим,” with the [official installation link](https://docs.docker.com/engine/install/). If unavailable or access is denied, report that specific problem. **Do not install Docker, start its service, change groups or permissions, or retry with `sudo docker`.** Recheck after the user fixes it. Missing Docker blocks build readiness; it need not block an explicitly requested installer download. Check virtualization only when the user needs an emulator.

Report blockers and the next step briefly. Keep installation pending when required prerequisites are unresolved. Do not run the SDK installer as root or silently provision the host.

## Download and hand off

Open the official download page for the chosen type, release, Linux, and host architecture. The [BT 5.2.1.200 page](https://developer.auroraos.ru/downloads/sdk_bt/5.2.1.200/linux) is an example. Follow real page links to the exact `.run` artifact and its published checksum. Do not synthesize timestamped filenames or substitute a different release/type. If the page is inaccessible, try an available browser or ask for the official artifact link.

For an authorized download, show the selected artifact, source link, published size when available, and local destination. Download outside the source tree to a `.part` file, fail on HTTP errors, and verify against the official checksum using its published algorithm before renaming to the final filename. Verify an existing download before reusing it. A mismatch is a failed download. If no official checksum is available, report that verification is pending instead of claiming success.

Give the user the exact local path and quoted commands to make the verified installer executable and launch it as their ordinary desktop user. Explain the chosen release/type, intended SDK directory, and outstanding prerequisites. **The user launches and completes the graphical installer.** Do not click through it or mark installation complete after downloading. State: “Установщик скачан и проверен; установи SDK и сообщи путь установки.” For a links-only request, return the link and guidance without downloading.

## Verify when the user returns

Resolve the actual installed directory and run its `bin/sfdk --version` and `bin/sfdk --no-pager tools target list` with bounded timeouts. Confirm the requested release and relevant installed targets, and check the installed SDK's type from its metadata or installer record. A directory alone is insufficient. Report partial readiness if the build engine remains unavailable. Do not start a build unless requested.

When configuring an identified existing project, merge the verified absolute `sfdk` executable path into `.aurora/sdk.json`. Preserve unrelated keys, reject malformed JSON or invalid path types, and ensure `/.aurora/sdk.json` is Git-ignored. Resolve conflicting recorded choices before replacement; an explicit SDK-change request suffices. Tell the user if the local file is already tracked. For standalone installation, write no project metadata. For a new project, return the verified path to its setup skill; wait until generation succeeds before recording it.

Report release/type, installer path, actual SDK path, checks, and pending work. Return to the calling setup and its original requested action with known answers after verification. SDK installation is independent of PSDK; do not search for, require, or install PSDK here. The Aurora Flutter fork is a separate tool too.
