# Record agreed project context

## 4. Record local SDKs and durable project instructions

Write configuration in the selected project root only after it exists and creation, if requested, has succeeded. For an existing project, merge with its current settings. Keep these two kinds of information separate:

**Local toolchain: `.aurora/sdk.json`.** Use optional independent path fields: `flutter` is the absolute Aurora Flutter SDK root; `sfdk` is the absolute desktop SDK executable; `psdk` is the absolute PSDK root containing `sdk-chroot` (not its outer installation directory). Record only tools selected for this project; the fields do not imply dependencies on one another. Preserve unrelated keys and any other stack's SDK value. Validate JSON and nonempty absolute path strings before editing; report malformed configuration rather than replacing it with an empty record. Record only tools that were found and validated, with no placeholder paths. For Flutter, verify distribution provenance and Aurora command/template support as well as `bin/flutter --version --machine`; the current Flutter setup helper additionally requires a channel containing `aurora`, which is a helper limitation rather than an established platform requirement. Report an incompatible helper check without altering the SDK; `sfdk` must be executable and identify itself through `--version`; PSDK must launch and list the selected tooling/targets through `sdk-assistant list`. Resolve conflicting choices before changing a recorded tool; a user's explicit change request already resolves that choice and needs no further approval. For Flutter, use `aurora-flutter-setup-project` in `--existing --record-only` mode, adding `--replace-sdk --flutter-sdk <new-root>` for an explicitly requested replacement. This preserves its SDK checks and legacy-marker migration without platform generation.

For an existing Qt project being configured without a build, validate the selected `sfdk` and merge its absolute executable path into `.aurora/sdk.json`; do not run a build merely to save the path. Ensure `/.aurora/sdk.json` is ignored by the project's `.gitignore`, preserving existing entries. If the file is already tracked, tell the user; adding an ignore rule alone does not untrack it. Never put personal SDK paths, keys, credentials, or device addresses into committed agent instructions.

**Project workflow: `AGENTS.md`.** Add or merge one Aurora section in the selected project's existing `AGENTS.md`. If its maintained agent instructions live in `CLAUDE.md` instead, update that file; do not create a competing set. If neither exists, create `AGENTS.md`. Keep unrelated instructions and user edits. Use the markers below to locate this skill's section on subsequent runs; if an equivalent Aurora section already exists, merge it rather than appending a duplicate.

```markdown
<!-- aurora-skills:start -->
## Aurora development

- Project: <Qt/Flutter app or plugin, build system or plugin implementation>.
- Identity: <organization, technical name, display name, or existing identifier>.
- Local SDKs: read `.aurora/sdk.json`; keep SDK paths out of committed files.
- Workflow: <selected skill names and the operations they handle>.
- Sources: `aurora-platform-context` for platform evidence and official MCP.
- Development: <matching development skill> for stack-specific practices and examples.
- Pending: <only genuine missing tools or unsupported work; omit when none>.
<!-- aurora-skills:end -->
```

Replace the example fields with the agreed facts; mention only relevant skills and omit Sources and Development for workflows without code development or documentation research. Keep reusable knowledge inside installed skills and their `references/`; do not create a project `docs/` tree or copy these references into the application. Preserve existing user documentation. Do not make generic onboarding a prerequisite for later direct skill requests or instruct other skills to rerun setup on every turn. Project type and workflow belong in the agent section; do not add an incompatible project schema to `.aurora/sdk.json`.

