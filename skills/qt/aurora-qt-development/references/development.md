# Qt/QML application practices

Baseline researched: Aurora documentation **5.2.1**, inspected 2026-10-30. This is evidence for that release, not a declaration that every Aurora target has identical APIs. Source IDs below resolve in [evidence](evidence.md).

## Application structure and UI — Aurora-specific

For a normal native application, preserve the template's `Aurora::Application::application`, organization/application identity, `createView`, and `pathTo` initialization. `libauroraapp` supplies platform configuration and application paths; replacing it with a generic desktop `QGuiApplication` startup loses that integration. The returned application and view are application-owned. Register C++ types/context objects before loading the root QML, and ensure objects exposed to QML outlive their consumers. [A1, A2, L1, L2]

The standard UI combines QtQuick and `Sailfish.Silica 1.0`: `ApplicationWindow`, `initialPage`, `Page`, `pageStack`, and an optional scalable cover. Retain the chosen imports; a namespace containing Sailfish is not by itself obsolete. `Aurora.Controls` is also listed in the platform API, but that does not imply replacing the whole application shell. Check the particular component and its release availability. **QtWidgets is explicitly disallowed** by the 5.2.1 public API guidance; a desktop widgets example is not an appropriate mobile application baseline. [A3, A4, A5]

Use `Theme` sizes/colors/padding, layout widths derived from parents, Silica scrolling containers, and `qsTr`/existing translation workflow. Preserve orientation handling and test keyboard/long-text layouts. Use the platform page/dialog interaction rather than assuming desktop windows and menus. For a board game, a custom QtQuick board can live inside a Silica `Page`; every cell need not be a heavyweight platform control. The last sentence is a design recommendation, not a platform requirement. [A3]

A cover displays application state while backgrounded; it is not a second independent model. Feed pages and cover from the same state, and avoid starting duplicate sensors/network polls in each view. This recommendation follows the documented cover lifecycle. [A4]

## Files, permissions and API selection — Aurora-specific

Use `Aurora::Application::pathTo(...)` for installed assets, and the documented application data/cache helpers for mutable files. An installed resource directory is not a writable state directory. Select per-user versus shared storage intentionally; verify the selected SDK declarations and directory permissions before writing. Keep organization/application identity consistent between startup, desktop metadata and package target. [A1, A6]

For every new platform feature, check four distinct things:

1. Public API availability for the target OS and security profile.
2. Qt/pkg-config link dependency and RPM `BuildRequires`.
3. Runtime packages/QML imports and private library deployment.
4. `.desktop` `[X-Application]` permissions and failure behavior when access is unavailable.

The 5.2.1 desktop specification requires `[X-Application]`; permissions are semicolon-separated. Examples are `Internet` for network access and `Location` for geolocation. Request only permissions the feature needs. A GPS-only feature does not acquire `Internet` merely because the Geolocation demo also has maps. The validation profile comes from the certificate; adding a permission string does not grant a more privileged profile. Inspect the versioned public-API/dependency tables rather than copying an entire demo's permission set. [A5, A6, A7, A8]

Geolocation demonstrates nullable `QGeoPositionInfoSource`/satellite sources, QObject ownership, asynchronous updates and NOTIFY properties. Check absence/error/stale data as separate states; never show “0,0” as a successful location merely because a default coordinate exists. This is defensive application guidance derived from the inspected example, not a new Aurora API guarantee. [L3]

## Foreground, background and suspend — Aurora-specific

Do not assume a QML `Timer` ensures execution while the device sleeps. Distinguish UI visibility, preventing display blanking, preventing system suspend and scheduled background work. `Nemo.KeepAlive 1.2` supplies separate abstractions; select the one required by the feature. `KeepAlive.enabled` requests suspend prevention subject to lower-level policies, not immortality or restart after process termination. [A9, L2]

`BackgroundJob` coalesces wakeups across the system; the first wakeup may occur earlier than its nominal interval. After each triggered job, call `finished()` to permit suspend and schedule the next wakeup, or disable the job. Release on success, failure, cancellation and timeout. For async work, release when the operation actually completes, not immediately after starting a request. Avoid permanent keepalive for an idle game. [A10]

Bad illustrative control flow:

```qml
BackgroundJob {
    onTriggered: controller.refresh() // never releases suspend prevention
}
```

Better integration contract (pseudocode; controller is application-defined):

```text
job triggered -> start one bounded refresh
refresh success/error/cancel/timeout -> finish that active job exactly once
feature disabled -> cancel work and disable job
```

Keep the job owner alive until completion; if a page can be popped, own background work outside that page. The release requirement is documented; ownership/cancellation policy is application engineering. The fragments are not compiled or device-tested. [A10]

## C++ / QML state — general Qt practice

Use domain state shared by UI and tests; do not duplicate rules in QML and C++. Expose dynamic QObject properties with appropriate notifications; the local Geolocation implementation demonstrates the Qt 5-style mechanism. A view binding updates from notifications, not merely because a C++ field changed. [L3, Q1]

Original illustrative fragment, not compiled:

```cpp
// Inside a QObject-derived class with Q_OBJECT, getter, signal and backing field:
Q_PROPERTY(QString status READ status WRITE setStatus NOTIFY statusChanged)

// Bad: m_status = value; alone leaves QML uninformed.
void Board::setStatus(const QString &value) {
    if (m_status == value)
        return;
    m_status = value;
    emit statusChanged();
}
```

Likewise, imperative assignment to a bound property removes that binding. [Q2]

```qml
Label { id: statusLabel; text: board.status }
// Bad reset handler: statusLabel.text = "New game"
// Better: board.reset() updates domain state; text remains bound.
```

Do not import the surrounding Qt 6 syntax from current upstream documentation into a Qt 5 target: `QML_ELEMENT`, `qt_add_qml_module`, required properties and newer connection helpers need their own version checks. Q1/Q2 support the general notification/binding concepts only.

General engineering guidance: keep blocking work off the UI thread, define QObject ownership, bind callback lifetimes to their consumers, and mutate UI models on their owning thread. For `QAbstractItemModel`, use the appropriate insertion/removal/data-change notifications rather than changing a container silently. These are Qt practices, not Aurora-specific security rules.

## Verification suited to the change

- Logic: focused tests of transitions, invalid actions, errors and reset; for a game include post-win moves and draws.
- Target compatibility: compile against the selected target, inspect missing APIs/imports; host Qt success is insufficient.
- Packaging: inspect runtime QML/plugins/libraries and permissions; use the build/validation skills when requested.
- Runtime: launch from the installed package; check rotation, page transitions, cover/background/resume and platform denial/offline cases relevant to the feature.

Report which of these actually ran. A produced RPM does not establish UI/runtime correctness. Read [packaging](packaging.md) when changing native dependencies or CMake/Conan integration.
