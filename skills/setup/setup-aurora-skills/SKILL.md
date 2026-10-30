---
name: setup-aurora-skills
description: Interview the user to choose an Aurora OS project type and configure this skill set for a new or existing project. Use for initial onboarding, choosing between Qt and Flutter apps or plugins, or updating project SDK settings and agent instructions.
---

# Set up Aurora skills

Turn the user's intended project into an agreed skill set and workflow. Use the user's project directory, not this collection's checkout. Reuse known answers; a direct specialized operation does not require a new interview.

## Consultation

Read [interview](references/interview.md) to inspect existing project evidence and ask only unresolved questions: intended result, Qt/Flutter app/plugin, relevant build/bridge choice and destination. Collect scaffold identity only when creating a scaffold. Keep consultation separate from installation or application creation.

An empty directory is a valid starting point: infer nothing from missing build files. Ask about the app idea and unresolved stack choices. Consultation alone returns a proposal without files; workflow-only setup can record agreed instructions without creating an app; scaffold creation follows the selected generator's destination rules. For local skill installation into the same empty scaffold destination, generate the scaffold first using the selected skill read from the collection, then install the agreed skills and write metadata. Creating `.agents/` first would also violate the empty-directory requirement. See the empty-project cases in [interview](references/interview.md).

Read [toolchains](references/toolchains.md) when checking the selected workflow's tools. Qt commands may use sfdk; Flutter commands use the selected Aurora Flutter executable. A native build backend does not imply calling sfdk or adding its path to a Flutter project's configuration.

## Select and agree

Read [selection](references/selection.md) to propose exact skills and purposes, including the shared source policy for development. Resolve target agent and project-local/global scope; recommend project-local for a project. Show a compact card with project type, destination, requested action, tools, skill selection/scope and pending items.

Install only the agreed missing skills after confirmation; reuse authorization already given for that exact selection and scope. Choosing “local”, a stack, or an SDK does not approve a skill list that has not been shown. Put the concrete names and purposes in the installation question itself, or show the resolved list afterward and wait for agreement. An explicit request to choose and install autonomously authorizes selection without this extra question. Inspect actual discovery after installation. Installation completion does not authorize scaffolding, building or signing. A workflow-only request remains workflow-only.

## Perform and record

Load the selected specialized skill and pass the agreed answers for the requested operation. If scaffolding is requested, generate it before writing metadata that would make the destination nonempty. Otherwise preserve application files.

Read [project record](references/project-record.md) before merging `.aurora/sdk.json`, its ignore rule and one marked `AGENTS.md`/existing `CLAUDE.md` section. Shared knowledge stays in skills; do not generate project documentation copies. Preserve unrelated keys and instructions.

Report the selected skills/scope, changed files, actual checks and pending capabilities. Distinguish consultation, installed skills, configured workflow, generated scaffold, build and runtime results. On rerun, address only new or unresolved choices.
