---
name: aurora-platform-context
description: Resolve authoritative Aurora OS documentation, SDK evidence and matching Flutter embedder sources. Use for platform API compatibility questions, official documentation MCP access, or source conflicts during Qt and Flutter development.
---

# Aurora platform context

This is the common source-selection policy used by the Qt and Flutter development skills. Read [sources](references/sources.md) before choosing platform APIs or making compatibility claims. It defines target identification, documentation/MCP access, SDK/PSDK header inspection, source priority and unavailable-source behavior.

For Flutter native behavior, wrapper APIs or plugin lifecycle, also read [Flutter and embedder sources](references/flutter-sources.md). It defines how to find or retrieve a matching revision without replacing the installed SDK.

Return the relevant versioned evidence to the calling development skill and continue the user's task. Do not repeat onboarding or load unrelated stack guidance. Project-specific implementation practices stay in the selected development skill; dependency admission belongs to `aurora-flutter-add-dependency`.

For reviews, distinguish a demonstrated defect in the supplied code from an integration check that needs files not supplied. A snippet without `main`, registration, a desktop file or build rules does not prove that the complete project lacks them. Cite the inspected file/symbol and conditions for each finding; do not claim a compile/runtime failure was reproduced when only source or documentation was inspected. Stop researching once the relevant contract is established; leave unavailable evidence explicit instead of repeatedly searching unrelated examples.

Resolve this skill by name from the selected agent's inventory, preferring the project-local copy unless the user selected otherwise. Installers may flatten directories: other skills must not assume a sibling relative filesystem path. If this skill is unavailable, report the missing shared policy and offer its installation in the user's chosen scope; do not invent a local replacement policy.
