<div align="center">

<img src="assets/logo.png" width="128" alt="exteraless">

# exteraless

Freezgram / exteraless — редакция без плагинов (`no-plugins`)

[![Канал](https://img.shields.io/badge/Telegram-@exteraless-2CA5E0?logo=telegram&logoColor=white)](https://t.me/exteraless)

</div>

---

## Что это

exteraless — форк [NagramX](https://github.com/risin42/NagramX), в котором возможности
exteraGram реализованы с открытым исходным кодом.

Ветка `no-plugins` полностью исключает движок плагинов, Python runtime,
установку плагинов и их пункты интерфейса. Редакция с плагинами остаётся в `main`.
Обе редакции сохраняют общий пакет и схему подписи. Для личных APK из CI
используется `com.exteraless.app.personal`; переход между ветками выполняется
новой сборкой с общим возрастающим versionCode и тем же ключом.

Проект **в бете**: часть возможностей exteraGram ещё не перенесена. Если заметили, что
каких-то функций не хватает, — откройте issue или напишите в [канал](https://t.me/exteraless?direct).

* Имя пакета: `com.exteraless.app`
* Что перенесено: экраны настроек, оформление и параметры чатов, иконпаки, полоса
  пилюль (Pill Stack), боковое меню

### Ссылки

* Канал: [@exteraless](https://t.me/exteraless)
* Исходники: [github.com/exteraless/exteraless](https://github.com/exteraless/exteraless)

### Сборка

1. Склонировать репозиторий вместе с подмодулями:

    ```bash
    git clone --branch no-plugins --recursive --shallow-submodules https://github.com/cneqq/freezgram.git freezgram
    ```

    Если репозиторий уже склонирован без подмодулей:

    ```bash
    git submodule update --init --recursive --depth=1
    ```

2. Получить `TELEGRAM_APP_ID` и `TELEGRAM_APP_HASH` на [my.telegram.org](https://my.telegram.org/auth)
   и создать `local.properties` в корне проекта:

   ```properties
   TELEGRAM_APP_ID=<ваш_app_id>
   TELEGRAM_APP_HASH=<ваш_app_hash>
   ```

3. Для подписи APK положить свой `TMessagesProj/release.keystore` и дописать в `local.properties`:

   ```properties
   KEYSTORE_PASS=<пароль_хранилища>
   ALIAS_NAME=<имя_ключа>
   ALIAS_PASS=<пароль_ключа>
   ```

   Ключа в репозитории нет намеренно. Без него сборка не падает — APK подписывается
   отладочным ключом Android.

4. Для push-уведомлений положить свой `TMessagesProj/google-services.json`
   (Firebase, имя пакета `com.exteraless.app`).

5. Заменить метаданные проекта:

    - ключ Google Maps в записи `com.google.android.maps.v2.API_KEY` в `TMessagesProj/src/main/AndroidManifest.xml`;
    - `BaseRemoteHelper.CHANNEL_METADATA_ID` — числовой id вашего канала метаданных, без префикса `-100`.

6. Собрать: `./gradlew :TMessagesProj:assembleDebug` или открыть проект в Android Studio.

**Про ABI.** Сохранены цели `arm64-v8a` и `x86_64`. Переменная
`NATIVE_TARGET` задаёт цель: `arm64-v8a` (один ABI, быстрее), `universal` (оба),
`SKIP` (без нативной части — только Java и ресурсы; это не полноценный APK).
Для ARM64 debug в PowerShell: `$env:NATIVE_TARGET='arm64-v8a'`, затем
`.\gradlew.bat :TMessagesProj:assembleDebug`. Нужны Java 21, Android platform 37.0,
Build Tools 36.0.0, NDK 27.2.12479018, CMake 3.31.6 и остальные подмодули.

### Сборка через GitHub Actions

Для этого форка используйте [личную сборку ARM64](docs/PERSONAL_BUILD.md).
Старые workflows ниже отключены; инструкция upstream сохранена для справки.


Нужны два секрета репозитория:

* `LOCAL_PROPERTIES` — содержимое `local.properties` в base64:

  ```bash
  base64 -w0 local.properties
  ```

* `RELEASE_KEYSTORE` — файл ключа в base64:

  ```bash
  base64 -w0 TMessagesProj/release.keystore
  ```

Дальше запустить workflow **Release Build**. Готовый APK лежит в артефактах прогона.

### Авторы дизайна

Иконки и оформление, унаследованные от exteraGram, созданы его дизайнером —
[@the8055u](https://t.me/the8055u) и студией [@BlueprintDsgn](https://t.me/BlueprintDsgn).
Права на эти материалы принадлежат авторам.

### Благодарности

- [AyuGram](https://github.com/AyuGram/AyuGram4A)
- [Cherrygram](https://github.com/arsLan4k1390/Cherrygram)
- [Dr4iv3rNope](https://github.com/Dr4iv3rNope/NotSoAndroidAyuGram)
- [exteraGram](https://github.com/exteraSquad/exteraGram)
- [Inugram](https://github.com/teidesu/inugram)
- [Nagram](https://github.com/NextAlone/Nagram)
- [NagramX](https://github.com/risin42/NagramX)
- [Nekogram](https://github.com/Nekogram/Nekogram)
- [OctoGram](https://github.com/OctoGramApp/OctoGram)

---

## English

### What this is

exteraless is a fork of [NagramX](https://github.com/risin42/NagramX) that implements
exteraGram's features open-source.

The `no-plugins` branch removes the plugin engine, Python runtime and plugin UI.
The plugin edition remains on `main`. Both editions keep the same package and signing
policy; a newly built APK with a higher shared versionCode can update either edition
when signed with the same key. See the personal build guide for the CI package.

The project is **in beta**: some exteraGram features have not been ported yet. If you
notice a missing feature, open an issue or write to the [channel](https://t.me/exteraless?direct).

* Package name: `com.exteraless.app`

### Design credits

Icons and visual design inherited from exteraGram are the work of its designer,
[@the8055u](https://t.me/the8055u), and the [@BlueprintDsgn](https://t.me/BlueprintDsgn)
studio. Rights to those materials belong to their authors.

### Building

1. Clone with submodules:

    ```bash
    git clone --branch no-plugins --recursive --shallow-submodules https://github.com/cneqq/freezgram.git freezgram
    ```

2. Get `TELEGRAM_APP_ID` and `TELEGRAM_APP_HASH` from [my.telegram.org](https://my.telegram.org/auth)
   and put them into `local.properties` in the project root.

3. For release signing, drop your own `TMessagesProj/release.keystore` and add
   `KEYSTORE_PASS`, `ALIAS_NAME`, `ALIAS_PASS` to `local.properties`. No keystore is
   shipped with the repository; without one the build is signed with the Android debug key.

4. For push notifications, replace `TMessagesProj/google-services.json` with your own
   Firebase config for `com.exteraless.app`.

5. Build with `./gradlew :TMessagesProj:assembleDebug` or from Android Studio.

The existing 64-bit targets (`arm64-v8a`, `x86_64`) are retained. `NATIVE_TARGET`
selects `arm64-v8a`, `universal` (both) or `SKIP` (no native part; not a complete APK).

For CI, set two repository secrets — `LOCAL_PROPERTIES` and `RELEASE_KEYSTORE`, both
base64-encoded — and run the **Release Build** workflow. The APK ends up in the run
artifacts.
