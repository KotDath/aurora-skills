# ApplicationTemplate map

Source: <https://hub.mos.ru/auroraos/demos/ApplicationTemplate>

| User choice | Git branch | Project file | Translation filenames |
| --- | --- | --- | --- |
| `qmake` | `example` | `<package-id>.pro` | `<package-id>.ts`, `<package-id>-ru.ts` |
| `cmake` | `cmake-version` | `CMakeLists.txt` | `<app-name>-en.ts`, `<app-name>-ru.ts` |

There are no branches literally named `qmake` or `cmake`. The `dev` branch is a separate qmake development branch.

Both branches contain `<package-id>.desktop`, `rpm/<package-id>.spec`, `qml/ApplicationTemplate.qml`, `src/main.cpp`, four package PNG icons, and `qml/icons/ApplicationTemplate.svg`. The build files, desktop entry, source, QML, translations, and `.gitignore` refer to the original identity. The translations also contain an upstream template description and the original BSD license text. Change the description, retain the license text and SPDX notices.

The generated project keeps the source license and `AUTHORS.md` for attribution. It gets a new README identifying the source branch and commit. The upstream CLA, code of conduct, CI files, badges, and screenshots describe the template repository rather than the new application and are omitted. The template icon artwork remains until the user supplies replacement assets.

If the script reports that the expected file layout changed, inspect both the selected upstream branch and the references in its build files before updating the manifest or transformations. Do not silently ship a partially renamed project.
