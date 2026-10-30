# Good/bad patterns with bounded claims

These are original educational fragments. General language/ownership rules are not Aurora-specific APIs. Only the small C ABI fragment below was host-tested; no fragment was compiled as an Aurora plugin or executed on an Aurora device.

## D-Bus client ownership

The official D-Bus tutorial and local battery backend close clients after a successful await. If the service throws first, that cleanup is skipped. Improve the lifetime without changing which bus/service the platform contract requires.

Bad (pseudocode):

```dart
final client = DBusClient.system();
final value = await query(client);
await client.close();
return value;
```

Better, original Dart helper (imports `package:dbus/dbus.dart`):

```dart
Future<T> withSystemBus<T>(Future<T> Function(DBusClient) query) async {
  final client = DBusClient.system();
  try {
    return await query(client);
  } finally {
    await client.close();
  }
}
```

This owns a client per request. A shared client instead belongs to a documented service lifetime and must not be closed after every call. For streams, keep cleanup in a cancellation/error-safe lifetime (for example `try/finally` around an `async*` producer), release subscriptions, and test cancellation. Do not turn a service failure into a valid-looking `false` or zero unless the public API explicitly specifies that fallback. The local battery power-save fallback is not a general recommendation.

## Method dispatch and cancellation

Bad (wrapper-independent pseudocode):

```text
if method == "read":
    start_work(callback = value => reply.success(value))
reply.success("")
```

Better (design pseudocode, not an invented wrapper API):

```text
if unknown method: reply.not_implemented(); return
if invalid arguments: reply.error("invalid-arguments"); return
transfer reply to one pending-request owner
start work with a cancellation token and a safe reference to that owner
on completion: serialize success/error and remove pending request
on shutdown while engine is valid: cancel and resolve pending requests once
prevent late callbacks from accessing plugin/messenger state
```

The exact ownership/dispatch API must come from the selected wrapper. See `native-lifecycle.md`: dropping a pending result is not guaranteed to complete Dart's Future.

## FFI: UTF-8 byte size and matching deallocator

The [official FFI tutorial](https://developer.auroraos.ru/doc/extended/flutter/plugins_development/ffi), read on 2026-10-30, contains an unsafe demonstration: it allocates by QString character count before copying UTF-8 bytes, allocates with `new[]` but releases with Dart `calloc.free`, and returns a non-owned literal on failure which the Dart code also tries to free. This is a source-level finding; the original code was not executed. Use the guide for the integration outline, not those memory operations.

A narrow alternative C ABI owns all returned strings in the same native library. This example accepts an existing NUL-terminated UTF-8 string; it does not query an Aurora service, validate UTF-8 or represent embedded NULs. Null input/failure returns null, while an empty string is a successful owned allocation. `label_free(NULL)` is allowed. Expose both symbols using the chosen library's export convention.

```cpp
#include <cstdlib>
#include <cstring>

extern "C" char* label_copy(const char* utf8) noexcept {
  if (!utf8) return nullptr;
  const size_t size = std::strlen(utf8) + 1;
  auto* copy = static_cast<char*>(std::malloc(size));
  if (copy) std::memcpy(copy, utf8, size);
  return copy;
}

extern "C" void label_free(char* value) noexcept {
  std::free(value);
}
```

For a QString adapter, first obtain and retain `QByteArray bytes = value.toUtf8()`, then copy bytes with their byte length or this helper while `bytes` lives. Define separate status/error reporting if null must distinguish service failure from allocation failure. Catch native exceptions before the C boundary; never expose QObject/C++ layouts to Dart as a C ABI.

Dart-side consumption pattern after a native call, assuming generated bindings `label_free(Pointer<Char>)` and imports `dart:ffi` plus `package:ffi/ffi.dart`:

```dart
String consumeLabel(Pointer<Char> pointer) {
  if (pointer == nullptr) throw StateError('Native label unavailable');
  try {
    return pointer.cast<Utf8>().toDartString();
  } finally {
    bindings.label_free(pointer);
  }
}
```

`bindings` is the selected generated library binding, not a Flutter API. The code assumes the pointer came from that library's matching allocator and is consumed exactly once. Do not use Dart `calloc.free` as a universal deallocator. Generate binding widths from the C declaration and target ABI; verify exported symbols and the library bundled in the RPM.

The C++ fragment was compiled and exercised on the host with Cyrillic/emoji, empty input, null input and matching frees under AddressSanitizer. Allocation-failure injection and the Dart/generated-binding path were not tested. Host testing establishes neither target ABI nor Aurora service permissions.
