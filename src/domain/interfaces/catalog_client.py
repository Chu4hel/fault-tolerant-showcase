"""Интерфейс HTTP-клиента для взаимодействия с внешним каталогом."""

from abc import ABC, abstractmethod

from src.domain.models.quote import Quote


class ICatalogClient(ABC):
    """Абстрактный интерфейс взаимодействия с каталогом цитат."""

    @abstractmethod
    def set_source_url(self, url: str) -> None:
        """Установить или обновить базовый URL каталога.

        Args:
            url: URL каталога.
        """
        pass

    @abstractmethod
    def get_source_url(self) -> str | None:
        """Получить текущий базовый URL каталога.

        Returns:
            Строка с URL или None, если адрес еще не установлен.
        """
        pass

    @abstractmethod
    async def fetch_quote(self, quote_id: str) -> Quote | None:
        """Запросить цитату из внешнего каталога.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Экземпляр Quote, если найден (200), либо None при 404/503/недоступности.
        """
        pass
