# Channels, Qt and native lifetime

The facts below come from the recorded embedder commit in `evidence.md`; its mapping to an installed release binary is not established. Recheck the selected SDK before using these signatures.

## Method calls

`cw::MethodResult` expects one completion: success, error or not-implemented. The inspected `ReplyManager` suppresses duplicate replies, but that is not a concurrency guarantee. Its destructor warns about an unanswered message and does not automatically send an error, because the engine may be gone. Do not intentionally drop a result as normal cancellation.

`cw::BasicPlugin::HandleMethodCall` returns a result which is immediately applied by the wrapper. For asynchronous work, use a mechanism that explicitly owns the pending result, supported by the selected wrapper (the inspected wrapper also exposes `Preprocess`); do not return success and later reply again. Copy arguments needed beyond the handler lifetime. Validate codec variants, numeric widths, missing keys and domain ranges before calling services. Distinguish unsupported operations from failures of supported ones.

The recorded `ForwardToHandler` comment permits the **reply callback** on any thread. This does not make the plugin, `MethodResult`, Qt objects, EventSink or messenger handler map generally thread-safe. Serialize completion, prevent races with teardown, and inspect the actual sending/dispatch path for event delivery. Do not import Android TaskQueue APIs or assume a universal Aurora “post to main thread” function.

## Registration and shutdown

The recorded `PluginRegistrar` holds plugins in shared ownership. `ClearPlugins()` calls each plugin's `Release()` before clearing plugins, then the registrar destroys the messenger. A reference held elsewhere may keep a plugin alive after registrar teardown: its raw messenger/application pointers are not thereby valid. Use the selected release hook to stop producers, unregister handlers and settle pending operations while the engine is valid; ensure late callbacks cannot touch released state. Do not add a `Release()` override to older wrappers that lack it.

Both MethodChannel and EventChannel headers explicitly state that destroying the channel object does **not** unregister the messenger handler. For early plugin disposal, unregister the handler while its messenger still lives; retain access to the channel or equivalent unregistration route. A lambda capturing `this` may otherwise outlive the plugin. QObject context-based connections help with QObject lifetime but do not replace channel unregistration or pending-reply ownership.

## Streams and Qt

Treat `listen`, `cancel` and engine release as resource transitions:

- On listen, establish one producer subscription, retain its sink and define whether an initial snapshot is emitted. Return an explicit error if the feature cannot start.
- On cancel, stop/disconnect that subscription, invalidate/reset its sink and prevent queued callbacks from publishing to it. Relistening creates a fresh usable state.
- On release, perform cleanup even if Dart never sent cancel. Unregister the channel while the messenger is alive.

The recorded EventChannel invokes `OnCancel(nullptr)` when a new listen replaces an active one; handlers must tolerate that argument. Unregistering the handler does not itself call `OnCancel`, so stop the producer explicitly. The local sensors implementation illustrates cancel/relisten and two logical streams sharing one accelerometer: stop a shared device only after its last consumer leaves. Its filtering/units/clock policy must be checked against the platform-interface contract rather than copied as universal sensor behavior.

For Qt plugins, inspect `useQt`, the runner's Qt integration, CMake AUTOMOC/Q_OBJECT handling and linked modules in the selected template. Use one clear ownership scheme for QObject resources; respect affinity when starting/stopping sensors or handling signals. Move blocking work off the UI/platform event loop only when the underlying API supports that execution context. Do not assume an isolate has a Qt event loop or that setting a manifest flag resolves all threading requirements.

These are resource/contract practices grounded in source inspection, not a claim that the local example plugins passed teardown or concurrency tests.
