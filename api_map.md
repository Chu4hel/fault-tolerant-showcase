---
chutils_version: 3.8.1
project_version: 0.1.0
git_commit: 177d7b4138feb0703becbe7d07f20a8a5036dfce (dirty)
generated_at: 2026-09-23T15:40:28.878470+00:00
project_hash: b3126135691dfd005214cc358c23e7c0dff07cdee3e0e86535267d92f6879e44
---

# Public API Map: quote-showcase

| Name                                                                                     | Type     | Signature              | Description                                                          |
|:-----------------------------------------------------------------------------------------|:---------|:-----------------------|:---------------------------------------------------------------------|
| `quote-showcase.src.application.quote_service.QuoteService`                              | class    |                        | Сервис для работы с цитатами, каталогом и статистикой.               |
| `quote-showcase.src.config.Settings`                                                     | class    |                        | Настройки сервиса витрины цитатника.                                 |
| `quote-showcase.src.config.settings`                                                     | constant |                        |                                                                      |
| `quote-showcase.src.domain.interfaces.catalog_client.ICatalogClient`                     | class    |                        | Абстрактный интерфейс взаимодействия с каталогом цитат.              |
| `quote-showcase.src.domain.interfaces.quote_storage.IQuoteStorage`                       | class    |                        | Абстрактный интерфейс in-memory хранилища цитат.                     |
| `quote-showcase.src.domain.models.quote.Quote`                                           | class    |                        | Модель цитаты.                                                       |
| `quote-showcase.src.domain.models.quote.QuoteSource`                                     | class    |                        | Источник происхождения отданной цитаты.                              |
| `quote-showcase.src.domain.models.quote.QuoteUpsertPayload`                              | class    |                        | Полезная нагрузка для добавления или изменения цитаты через витрину. |
| `quote-showcase.src.domain.models.quote.SourceConfigPayload`                             | class    |                        | Полезная нагрузка для задания адреса каталога.                       |
| `quote-showcase.src.domain.models.stats.ShowcaseStats`                                   | class    |                        | Эксплуатационная сводка сервиса.                                     |
| `quote-showcase.src.infrastructure.catalog_client.http_catalog_client.HttpCatalogClient` | class    |                        | Асинхронный HTTP-клиент каталога с поддержкой Retry-After.           |
| `quote-showcase.src.infrastructure.storage.memory_storage.MemoryQuoteStorage`            | class    |                        | In-memory реализация хранилища цитат с поддержкой LRU-вытеснения.    |
| `quote-showcase.src.main.app`                                                            | constant |                        |                                                                      |
| `quote-showcase.src.main.create_app`                                                     | function | `()`                   | Создает и настраивает экземпляр приложения FastAPI.                  |
| `quote-showcase.src.presentation.api.routers.catalog.DeleteResponse`                     | class    |                        | Модель ответа на удаление цитаты.                                    |
| `quote-showcase.src.presentation.api.routers.catalog.SourceResponse`                     | class    |                        | Модель ответа на установку адреса каталога.                          |
| `quote-showcase.src.presentation.api.routers.catalog.delete_quote`                       | function | `(quote_id)`           | Снятие цитаты с публикации редакцией через витрину.                  |
| `quote-showcase.src.presentation.api.routers.catalog.router`                             | constant |                        |                                                                      |
| `quote-showcase.src.presentation.api.routers.catalog.set_source`                         | function | `(payload)`            | Установка или обновление адреса каталога.                            |
| `quote-showcase.src.presentation.api.routers.catalog.upsert_quote`                       | function | `(quote_id, payload)`  | Добавление или замена цитаты редакцией через витрину.                |
| `quote-showcase.src.presentation.api.routers.health.HealthResponse`                      | class    |                        | Модель ответа ручки /health.                                         |
| `quote-showcase.src.presentation.api.routers.health.check_health`                        | function | `()`                   | Возвращает статус здоровья сервиса.                                  |
| `quote-showcase.src.presentation.api.routers.health.router`                              | constant |                        |                                                                      |
| `quote-showcase.src.presentation.api.routers.import_snapshot.ImportResponse`             | class    |                        | Модель ответа на импорт снимка каталога.                             |
| `quote-showcase.src.presentation.api.routers.import_snapshot.import_snapshot`            | function | `(request)`            | Прием полного снимка каталога через потоковую обработку тела.        |
| `quote-showcase.src.presentation.api.routers.import_snapshot.router`                     | constant |                        |                                                                      |
| `quote-showcase.src.presentation.api.routers.quotes.get_quote`                           | function | `(quote_id, response)` | Чтение цитаты читателем с заголовком X-Source (LOCAL / CATALOG).     |
| `quote-showcase.src.presentation.api.routers.quotes.router`                              | constant |                        |                                                                      |
| `quote-showcase.src.presentation.api.routers.stats.get_stats`                            | function | `()`                   | Получение эксплуатационной статистики службы.                        |
| `quote-showcase.src.presentation.api.routers.stats.router`                               | constant |                        |                                                                      |
