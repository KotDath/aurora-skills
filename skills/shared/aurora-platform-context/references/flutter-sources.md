# Aurora Flutter and embedder sources

Read when investigating native behavior, porting a plugin, or resolving differences between documentation and the installed SDK.

Official repositories:

- Aurora Flutter: https://hub.mos.ru/auroraos/flutter/flutter
- Aurora Embedder: https://hub.mos.ru/auroraos/flutter/aurora-embedder
- Documentation: https://developer.auroraos.ru/doc/extended/flutter
- Platform channel examples: https://developer.auroraos.ru/doc/extended/flutter/plugins_development/platform_channels

The embedder integrates the Flutter engine with Aurora. Its implementation can answer questions about platform messages, lifecycle, event processing and native resources. It does not make an Android/iOS-only plugin work on Aurora by itself.

## Obtain the relevant revision

1. Inspect the selected Aurora Flutter SDK's version output, revision and dependency/build manifests. Reuse an existing source checkout if its origin and revision match the required component.
2. Determine the embedder revision from that SDK's manifests, release metadata or official build instructions. Matching names of branches alone do not establish compatibility. If the mapping cannot be established, label the checkout exploratory and avoid treating it as evidence for the installed binary.
3. When sources are needed and absent, download only the relevant official repository into an agent cache or an ignored local directory. Read-only source downloads for the requested investigation can proceed without a new installation interview. Inspect remote refs first; fetch the needed tag/commit and record the resulting commit. Do not fetch all history or clone the full Flutter tree when one embedder file suffices.
4. Preserve existing checkouts and local edits. Use a separate checkout for another revision. Reading sources does not require running their scripts, rebuilding the engine or replacing the SDK.
5. Search the exact API and its call sites. Inspect headers plus implementation, ownership and thread/lifetime rules; verify public status before depending on a symbol. Retain origin and commit in the answer or an existing project decision record, not a new documentation tree.

If Mos.Hub is unavailable, use matching local sources and official documentation, state the gap, and avoid substituting an unverified mirror. Current repository HEAD is not proof of behavior in a released SDK.
