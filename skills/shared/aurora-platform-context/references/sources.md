# Sources and platform evidence

Read this before choosing platform APIs or claiming Aurora compatibility.

## Establish the target

Read the project's agent instructions, build/package metadata and `.aurora/sdk.json`. Its optional `sfdk`, `psdk`, and `flutter` fields identify independent toolchains. Use the selected installation; do not substitute host Qt headers or an upstream Flutter on PATH. Inspect only the recorded SDK roots and selected target/sysroot. If a path is missing, ask only when the requested work needs it; documentation research can continue without installing a toolchain.

Record the relevant OS release, architecture, Qt or Aurora Flutter version, and source revision in the task's evidence. Distinguish the development SDK release from the device OS release. A successful host test is not an Aurora runtime test.

## Choose the source by the question

| Question | Primary evidence | Cross-check |
| --- | --- | --- |
| Intended behavior, supported use, permissions, packaging | Official documentation for the target release | Matching SDK declarations and release notes |
| API signature or availability in this build | Headers/sources in the selected target SDK/PSDK | Documentation for that version; compile against the target |
| Flutter native integration or plugin behavior | Matching Aurora Flutter and embedder sources | Official Flutter-for-Aurora documentation and target execution |
| Working usage example | Official Aurora examples at https://hub.mos.ru/auroraos/ | Example revision, target version, dependencies and license |
| Discovery when the above lacks an answer | Web search, starting with `site:developer.auroraos.ru` and the exact symbol/error | Open the primary source; search snippets alone are not proof |

MCP is a transport for official sources, not a separate authority above the installed SDK. If sources disagree, name both versions and the conflict; prefer the selected target for availability. An internal implementation is not automatically a supported public API. Mark unresolved compatibility explicitly instead of inventing an API.

## Official MCP

Endpoint: `https://developer.auroraos.ru/api/mcp`, documented in the [official announcement](https://developer.auroraos.ru/news/17-09-2026-mcp-server).

Use the client's existing connection when available. If connecting is requested, use its supported remote HTTP MCP configuration and the user's chosen scope; preserve other servers. Do not substitute a similarly named community server. A documentation task alone does not authorize global client changes or deployment of a vector database.

To verify a connection, complete MCP initialization, list tools, and execute a documentation query. A plain GET without a session can return 401 and is not a valid health check. For a manual protocol diagnostic, POST `initialize` with JSON-RPC, JSON content type and Accept `application/json, text/event-stream`; retain the returned `Mcp-Session-Id`, send `notifications/initialized`, then `tools/list` and `tools/call`. Use a negotiated protocol version (2025-03-26 was verified on 2026-10-30). Let the MCP client manage sessions during normal work.

- Call `get_doc_versions` before versioned OS searches. Select the project's release rather than silently using latest.
- Use `search` with `query`, a focused `index`, and the selected `version`; fetch the full result using `get_document` with its returned `path` and `index`.
- For Flutter or Conan extension documentation, use `get_ext_tools_list` and search `ext_docs`. Extension versions need not equal OS versions.
- For examples, use `search_code`, then `get_code_source` with the returned URL; use line ranges for truncated files.
- Tool schemas are discovered from the server, not assumed from this reference.

If MCP fails, report the failed stage/status and retry a transient failure once. Continue with the same official web documentation and local sources when available. Do not claim MCP is configured because an HTTP request succeeded, or claim an API is verified because search returned a snippet.

## Local headers and evidence

For PSDK, resolve `psdk` from `.aurora/sdk.json`, confirm its tooling/targets with `sdk-assistant list` in the selected PSDK environment, and locate the selected target's sysroot/include directories. Use `rg --files` and symbol searches within those directories. Do not guess that all PSDK headers live directly under the recorded root, or scan every installation on the machine. If the workflow uses sfdk, use its selected target's headers instead of an unrelated PSDK release.

Cite a document URL/version or a source file/symbol/revision for consequential API decisions. Keep personal SDK paths in ignored local configuration, not committed agent instructions. Knowledge stays in the installed skill and its references; do not generate a project `docs/` tree or copy manuals during onboarding.
