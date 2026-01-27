from abc import ABC, abstractmethod
from typing import List


class IDataFetcher(ABC):
    @abstractmethod
    async def fetch_historical_data(
        self, symbol: str, timeframe: str, start_date: int, end_date: int
    ) -> List[List[float]]:
        """Абстрактный метод для получения исторических данных."""
        pass

    @abstractmethod
    async def fetch_realtime_data(
        self, symbol: str, timeframe: str
    ) -> List[List[float]]:
        """Абстрактный метод для получения данных в реальном времени."""
        pass


class IDataStorage(ABC):
    @abstractmethod
    async def save_historical_data(
        self, symbol: str, timeframe: str, ohlcv_data: List[List[float]]
    ) -> None:
        """Абстрактный метод для сохранения исторических данных."""
        pass

    @abstractmethod
    async def save_realtime_data(
        self, symbol: str, timeframe: str, ohlcv_data: List[List[float]]
    ) -> None:
        """Абстрактный метод для сохранения данных в реальном времени."""
        pass
