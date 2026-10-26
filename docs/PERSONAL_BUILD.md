# Личная ARM64 сборка

Actions → Personal release APK → Run workflow → main.
По умолчанию используются стандартные Telegram API ID/hash из исходного
TMessagesProj/build.gradle (API ID 6). Их не заменяют нулями. Настройка
telegram_credentials включает вместо них личные TG_API_ID/TG_API_HASH из Secrets.
Старые сборки с API ID=0 были только проверкой компиляции и не поддерживали вход;
их нужно заменить новой сборкой.

Собирается release build type: debug-логирование future_auth_token по условию
BuildVars выключено. Без personal_signing подпись остаётся временной, хотя режим
сборки release. Сам вход в аккаунт и работа кошелька CI-сборкой не проверяются.

Для установки нужен телефон Android 7+ с ARM64. Кошелёк GramWallet включён в исходниках;
нативный wallet engine входит в libtmessages.49.so. Проверка этого пути не является
аудитом ключей/seed phrase или гарантией работоспособности переводов.

## Telegram

В этом форке отдельно создать Actions Secrets TG_API_ID и TG_API_HASH.
Workflow запишет их как TELEGRAM_APP_ID/TELEGRAM_APP_HASH в приватный local.properties.
Оставить telegram_credentials выключенным для стандартных API-реквизитов upstream.
Включать его только для собственных Secrets после их настройки.
Не писать их в код, issues, поля запуска или сообщения CI. При компиляции эти
значения встраиваются в APK и доступны скачавшему его человеку. В публичном форке
Actions-артефакты могут скачать другие авторизованные пользователи GitHub.

## Постоянная подпись

Для постоянного APK нужны Secrets:

- RELEASE_KEYSTORE — собственный JKS/PKCS12-файл в base64 одной строкой;
- KEYSTORE_PASS — пароль хранилища;
- ALIAS_NAME — имя ключа;
- ALIAS_PASS — пароль ключа.

После этого включить personal_signing. Хранилище и пароли сохранить резервной копией
вне GitHub. Без этой опции подпись временная: новый запуск может потребовать удаления
старой установки с потерей локальных данных. Ключ автора не используется.
Release с собственным ключом не установится поверх APK с другим несовместимым ключом.
Не удалять привычный клиент ради теста без понимания потери локальных данных.

## Результат

После успешного запуска скачать ZIP из Artifacts: APK, SHA256SUMS.txt и build-info.json.
Артефакт хранится 3 дня. Workflow не публикует GitHub Releases и не пишет в Telegram.
Legacy workflows вынесены из .github/workflows и больше не запускаются автоматически.
Не включать их обратно с личными Secrets без проверки.

Сборка сохраняет плагины, обновлятор и кошелёк: это не выполнение полного плана
безопасности из аудита. Плагины/developer/unsafe mode пока держать выключенными.
Для основного аккаунта и денег требуется дополнительная проверка.

## Ускорение

Собирается только arm64-v8a. Кэшируются downloaded Gradle dependencies и C++ ccache
до 2 GB. local.properties, signing files, полные build outputs и Java compilation
outputs с API-реквизитами в кэш не добавляются. Первое заполнение кэша не ускоряет
самую первую сборку. Не используется SKIP — нативная часть обязательна.

Инструменты: Java 21, Python 3.11, Gradle 9.7.1 с официальным wrapper checksum,
Android platform 37.0, Build Tools 36.0.0, NDK 27.2.12479018, CMake 3.31.6.
Actions закреплены SHA. Запуск только вручную, token contents:read, без posting/release.
