## [Unreleased]

### Added
- Ручка для частичного обновления настроек аффирмаций пользователя ([PR #20](https://github.com/mksmin/api-backend/pull/20))
- Ручка для обновления аффирмаций пользователя ([Issue #17](https://github.com/mksmin/api-backend/issues/17), [PR #21](https://github.com/mksmin/api-backend/pull/21))
- S3 сервис для загрузки файлов ([PR #22](https://github.com/mksmin/api-backend/pull/22))
- Проверка изображений и ссылок ([PR #23](https://github.com/mksmin/api-backend/pull/23))
- Авторизация через Telegram OpenID Connect ([PR #29](https://github.com/mksmin/api-backend/pull/29))
- Создание учётных данных с email и паролем, вход с установкой JWT-cookie и отображение статуса email в профиле
- Смена пароля авторизованного пользователя и выход из аккаунта с очисткой cookie и CSRF-состояния
- CSRF-защита форм входа и операций авторизованного пользователя с привязкой токена к JWT-сессии
- Модуль LMS с флагом `lms.enabled`, списком и страницами проектов из базы данных и созданием проектов для организаторов
- Потоки LMS: модель и миграция, создание, список, страницы деталей и счётчик потоков проекта
- Редактирование названия потока LMS с проверкой прав владельца, валидацией и обработкой повторяющихся названий ([commit da99df8](https://github.com/mksmin/api-backend/commit/da99df8))
- Обработка недоступных проектов и потоков LMS с ответом 404 и документация архитектуры MVP
- Сортировка аффирмаций по тексту и дате создания с выбором направления
- Ручка проверки работоспособности `/health/` и страница подписки подпроекта `sdelkanv`
- Docker-образ, конфигурация Docker Compose и автоматическое развёртывание через GitHub Actions ([PR #24](https://github.com/mksmin/api-backend/pull/24), [PR #26](https://github.com/mksmin/api-backend/pull/26))
- Регрессионные тесты недоступности устаревших маршрутов проектов и запуск тестов в CI с включённым и выключенным LMS

### Changed
- Updated logging format: CustomFormatter with colored output and improved HTTP request parsing. ([PR #18](https://github.com/mksmin/api-backend/pull/18))
- Основной страницей входа стала форма email и пароля; вход через Telegram Widget доступен по `/login/tg`
- Авторизация разделена на сервис, диспетчер и отдельные верификаторы Telegram Mini App, Widget и OpenID Connect ([PR #28](https://github.com/mksmin/api-backend/pull/28), [PR #30](https://github.com/mksmin/api-backend/pull/30))
- Конфигурация разделена на модули, обновлены настройки подключения к базе данных и шаблоны конфигурации ([PR #25](https://github.com/mksmin/api-backend/pull/25), [PR #27](https://github.com/mksmin/api-backend/pull/27))
- CRUD-сервисы проектов и потоков LMS вынесены из `core` в модуль LMS
- Обновлены зависимости для Python 3.13+; Docker-образ и проверки CI переведены на Python 3.14
- Poetry в CI устанавливается в отдельное окружение во временной директории runner

### Fixed
- Недоступность RabbitMQ больше не блокирует запуск API: подключение выполняется в фоне с повторными попытками
- При тайм-ауте сервиса аффирмаций возвращается HTTP 503 с JSON-ответом для API или страницей ошибки для браузера
- Поддержано подключение к PostgreSQL через Unix-сокет и исправлено формирование URL подключения для Alembic
- Исправлена передача `request` при рендеринге Jinja-шаблонов
- Вход по email и паролю поддерживает локальный HTTP через настройку `run.auth_cookies_secure`; перенаправление после входа проверяется на безопасность
- Исправлены конфигурация Docker Compose и workflow развёртывания

### Removed
- Устаревшие API-маршруты и страницы проектов отключены независимо от флага LMS ([commit 08eff8e](https://github.com/mksmin/api-backend/commit/08eff8e))
- Связь родительского проекта и неиспользуемые поля модели проекта удалены с миграцией базы данных
