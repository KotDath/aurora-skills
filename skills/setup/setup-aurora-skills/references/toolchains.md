# Resolve selected toolchains

### When the required tool is not found

Check only tools needed for the selected action. Prefer an explicit user choice, then the project's recorded path. Validate these authoritative paths; do not silently switch to another installation if one is broken. For discovery, check `~/AuroraOS/bin/sfdk` and `command -v sfdk` for the desktop SDK; for PSDK, check `~/AuroraPlatformSDK/sdks/aurora_psdk/sdk-chroot`, `~/MyPSDKDir/sdks/aurora_psdk/sdk-chroot`, and relevant explicit environment hints. Multiple valid candidates require a choice. Ask for an Aurora Flutter path when neither the user nor the project supplies it; do not substitute an ordinary Flutter installation.

If the user says a required tool is absent, or it was not found in these locations, offer: supply its existing path, install that tool, or continue with it pending when the requested action allows this. Say where you checked rather than asserting it is not installed. Do not require toolchain installation for a workflow-only setup or a Qt scaffold.

After the user chooses installation, load `aurora-install-sdk`, `aurora-install-psdk`, or both according to the selected tools, carrying forward known choices and the original project action. Do not offer them as a required pair, reuse SDK BT/MB2 as a PSDK tooling selection, or install the other tool as a fallback. Neither skill installs the Aurora Flutter fork; if that fork is missing, ask for its path or explain the separate missing capability. A direct request to install a tool can use its skill without a project interview.

When both are selected, discover and validate each independently, installing only what is missing. Track separate releases, paths, targets, and readiness states; reuse a version or architecture choice only when the user or workflow establishes that it applies to both. An existing installation of one does not satisfy the other. An SDK graphical-installation handoff or SDK-specific prerequisite must not block authorized PSDK work, and vice versa. Save both verified paths as `sfdk` and `psdk` when recording project configuration. Resume each requested operation when its own prerequisites are ready, reporting any other operation still pending.

Let the install skill handle its prerequisites. In particular, when Docker is required and absent, tell the user to install it; do not install/configure it automatically. Keep the original action pending during a graphical SDK or interactive PSDK handoff. On return, verify the selected installation and resume that action without restarting the interview. A downloaded SDK installer is not an installed SDK.

