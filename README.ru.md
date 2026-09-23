[**RU**](README.ru.md) | [EN](README.md)

# aurora-skills

Скиллы для разработки приложений под ОС Аврора и вспомогательный скилл для сообщений о проблемах с агентом.

## Установка

### Через `npx skills`

Выполняйте команду из проекта, в который хотите установить скиллы. Чтобы установить **все скиллы для всех поддерживаемых агентов** без вопросов:

```bash
npx skills add KotDath/aurora-skills --all
```

Чтобы установить все скиллы с выбором агентов в диалоге или установить один конкретный скилл:

```bash
npx skills add KotDath/aurora-skills --skill '*'
npx skills add KotDath/aurora-skills --skill aurora-qt-setup-project
```

Вместо `aurora-qt-setup-project` можно подставить любое название из таблицы ниже. Добавьте `--copy`, чтобы копировать файлы вместо создания ссылок, или `--global`, чтобы установить скиллы для пользователя во всех проектах.

### Копированием файлов

Клонируйте репозиторий и копируйте **папку скилла целиком**, вместе с `scripts/` и `references/`, если они есть. Проектную `.agents/skills/` находят Codex, Pi, OMP и OpenCode.

```bash
git clone https://github.com/KotDath/aurora-skills.git
cd aurora-skills
PROJECT=/path/to/your/project
mkdir -p "$PROJECT/.agents/skills"

# Все скиллы:
cp -R skills/*/* "$PROJECT/.agents/skills/"
```

Чтобы скопировать только один скилл, замените последнюю команду на `cp -R skills/qt/aurora-qt-setup-project "$PROJECT/.agents/skills/"` (или укажите другую папку скилла из таблицы).

Чтобы скиллы были доступны во всех проектах, используйте вместо этого каталог `~/.agents/skills/`.

## Скиллы

| Скилл | Для чего нужен |
| --- | --- |
| [`aurora-qt-setup-project`](skills/qt/aurora-qt-setup-project/SKILL.md) | Создать Qt/QML-приложение из Aurora OS ApplicationTemplate на qmake или CMake. |
| [`aurora-qt-build-project`](skills/qt/aurora-qt-build-project/SKILL.md) | Собрать Qt-проект через `sfdk` и получить RPM-пакеты. |
| [`aurora-rpm-validate`](skills/rpm/aurora-rpm-validate/SKILL.md) | Проверить Aurora RPM по профилю безопасности. |
| [`aurora-rpm-sign`](skills/rpm/aurora-rpm-sign/SKILL.md) | Подписать Aurora RPM ключом и сертификатом разработчика. |
| [`aurora-flutter-setup-project`](skills/flutter/aurora-flutter-setup-project/SKILL.md) | Создать Aurora Flutter-приложение или плагин либо добавить поддержку Авроры в существующий проект. |
| [`aurora-flutter-add-dependency`](skills/flutter/aurora-flutter-add-dependency/SKILL.md) | Проверить зависимость по списку и добавить её через Aurora Flutter. |
| [`report-issue`](skills/util/report-issue/SKILL.md) | Собрать ZIP с описанием проблемы, текущей сессией агента и дочерними сессиями субагентов. |

[Список проверенных Flutter-зависимостей](skills/flutter/aurora-flutter-add-dependency/scripts/checked-dependencies.yaml) поддерживается вручную и лежит рядом со скриптом проверки. В нём указаны названия пакетов без привязки к версиям; пакеты из Aurora Pub считаются допустимыми по правилам проекта.

Сгенерированные проекты хранят локальные пути к SDK в исключённом из Git файле `.aurora/sdk.json`. Путь к Aurora Flutter SDK выбирается явно; для `sfdk` по умолчанию используется `~/AuroraOS/bin/sfdk`, если он установлен.
