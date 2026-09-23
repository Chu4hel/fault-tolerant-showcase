---
chutils_version: 3.8.1
project_version: 0.1.0
git_commit: d90e7d186e4aaf2d27b058a1caf193c1fa600358 (dirty)
generated_at: 2026-09-23T16:25:17.284471+00:00
project_hash: 6e00fb77cbd84a2f7c3ebabf93e9e3a19a3bc2d34e1e541300d857df7203989e
---

# Public API Map: quote-showcase

| Name                                                                                     | Type     | Signature                       | Description                                                                            |
|:-----------------------------------------------------------------------------------------|:---------|:--------------------------------|:---------------------------------------------------------------------------------------|
| `quote-showcase.src.application.quote_service.QuoteService`                              | class    |                                 | Сервис для координации работы с кэшем, каталогом и метриками.                          |
| `quote-showcase.src.config.Settings`                                                     | class    |                                 | Настройки сервиса витрины цитатника.                                                   |
| `quote-showcase.src.config.load_settings`                                                | function | `()`                            | Загружает настройки из config.yml через провайдер chutils с валидацией Pydantic.       |
| `quote-showcase.src.dependencies.create_catalog_client`                                  | function | `()`                            | Создает экземпляр HTTP клиента каталога.                                               |
| `quote-showcase.src.dependencies.create_quote_service`                                   | function | `(storage, catalog_client)`     | Создает экземпляр QuoteService через автовайринг зависимостей.                         |
| `quote-showcase.src.dependencies.create_quote_storage`                                   | function | `()`                            | Создает экземпляр хранилища цитат.                                                     |
| `quote-showcase.src.dependencies.get_quote_service`                                      | function | `()`                            | Возвращает экземпляр QuoteService из DI-контейнера chutils.                            |
| `quote-showcase.src.dependencies.setup_container`                                        | function | `()`                            | Регистрирует интерфейсы и реализации в DI-контейнере chutils.                          |
| `quote-showcase.src.domain.interfaces.catalog_client.ICatalogClient`                     | class    |                                 | Абстрактный интерфейс взаимодействия с каталогом цитат.                                |
| `quote-showcase.src.domain.interfaces.quote_storage.IQuoteStorage`                       | class    |                                 | Абстрактный интерфейс in-memory хранилища цитат.                                       |
| `quote-showcase.src.domain.models.quote.Quote`                                           | class    |                                 | Модель цитаты.                                                                         |
| `quote-showcase.src.domain.models.quote.QuoteSource`                                     | class    |                                 | Источник происхождения отданной цитаты.                                                |
| `quote-showcase.src.domain.models.quote.QuoteUpsertPayload`                              | class    |                                 | Полезная нагрузка для добавления или изменения цитаты через витрину.                   |
| `quote-showcase.src.domain.models.quote.SourceConfigPayload`                             | class    |                                 | Полезная нагрузка для задания адреса каталога.                                         |
| `quote-showcase.src.domain.models.stats.ShowcaseStats`                                   | class    |                                 | Эксплуатационная сводка сервиса.                                                       |
| `quote-showcase.src.infrastructure.catalog_client.http_catalog_client.HttpCatalogClient` | class    |                                 | Асинхронный HTTP-клиент каталога с Circuit Breaker, Bulkhead и поддержкой Retry-After. |
| `quote-showcase.src.infrastructure.logging.logger`                                       | constant |                                 |                                                                                        |
| `quote-showcase.src.infrastructure.storage.memory_storage.MemoryQuoteStorage`            | class    |                                 | In-memory реализация хранилища цитат с LRU-кэшем и компактным индексом каталога.       |
| `quote-showcase.src.main.app`                                                            | constant |                                 |                                                                                        |
| `quote-showcase.src.main.create_app`                                                     | function | `()`                            | Создает и настраивает экземпляр приложения FastAPI.                                    |
| `quote-showcase.src.presentation.api.routers.catalog.DeleteResponse`                     | class    |                                 | Модель ответа на удаление цитаты.                                                      |
| `quote-showcase.src.presentation.api.routers.catalog.SourceResponse`                     | class    |                                 | Модель ответа на установку адреса каталога.                                            |
| `quote-showcase.src.presentation.api.routers.catalog.delete_quote`                       | function | `(quote_id, service)`           | Снятие цитаты с публикации редакцией через витрину.                                    |
| `quote-showcase.src.presentation.api.routers.catalog.router`                             | constant |                                 |                                                                                        |
| `quote-showcase.src.presentation.api.routers.catalog.set_source`                         | function | `(payload, service)`            | Установка или обновление адреса каталога.                                              |
| `quote-showcase.src.presentation.api.routers.catalog.upsert_quote`                       | function | `(quote_id, payload, service)`  | Добавление или замена цитаты редакцией через витрину.                                  |
| `quote-showcase.src.presentation.api.routers.health.HealthResponse`                      | class    |                                 | Модель ответа ручки /health.                                                           |
| `quote-showcase.src.presentation.api.routers.health.check_health`                        | function | `()`                            | Возвращает статус здоровья сервиса.                                                    |
| `quote-showcase.src.presentation.api.routers.health.router`                              | constant |                                 |                                                                                        |
| `quote-showcase.src.presentation.api.routers.import_snapshot.ImportResponse`             | class    |                                 | Модель ответа на импорт снимка каталога.                                               |
| `quote-showcase.src.presentation.api.routers.import_snapshot.import_snapshot`            | function | `(request, service)`            | Прием полного снимка каталога через потоковую обработку тела.                          |
| `quote-showcase.src.presentation.api.routers.import_snapshot.router`                     | constant |                                 |                                                                                        |
| `quote-showcase.src.presentation.api.routers.quotes.get_quote`                           | function | `(quote_id, response, service)` | Чтение цитаты читателем с установкой заголовка X-Source (LOCAL / CATALOG).             |
| `quote-showcase.src.presentation.api.routers.quotes.router`                              | constant |                                 |                                                                                        |
| `quote-showcase.src.presentation.api.routers.stats.get_stats`                            | function | `(service)`                     | Получение эксплуатационной статистики службы.                                          |
| `quote-showcase.src.presentation.api.routers.stats.router`                               | constant |                                 |                                                                                        |
