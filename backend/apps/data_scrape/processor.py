import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from .interfaces import IDataFetcher, IDataStorage

# Настройка логирования
logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, fetcher: IDataFetcher, storage: IDataStorage) -> None:
        self.fetcher = fetcher
        self.storage = storage

    async def process_historical_data(
        self, symbols: List[str], timeframes: List[str]
    ) -> None:
        """
        Загружает и сохраняет исторические данные за последний год (на текущий 2026 год).
        """
        now = datetime.now()
        one_year_ago = int((now - timedelta(days=365)).timestamp() * 1000)
        end_date = int(now.timestamp() * 1000)

        tasks = [
            asyncio.create_task(
                self._process_historical_single(
                    symbol, timeframe, one_year_ago, end_date
                )
            )
            for symbol in symbols
            for timeframe in timeframes
        ]
        if tasks:
            await asyncio.gather(*tasks)

    async def _process_historical_single(
        self, symbol: str, timeframe: str, start_date: int, end_date: int
    ) -> None:
        try:
            logger.info(
                f"Запуск загрузки истории: {symbol} {timeframe} (start_date={start_date}, end_date={end_date})"
            )
            data = await self.fetcher.fetch_historical_data(
                symbol, timeframe, start_date, end_date
            )

            if data:
                await self.storage.save_historical_data(symbol, timeframe, data)
                logger.info(
                    f"Сохранено {len(data)} исторических свечей для {symbol} {timeframe}"
                )
            else:
                logger.warning(
                    f"Данные не найдены для {symbol} {timeframe}. Повторная попытка через 5 секунд..."
                )
                await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Ошибка при обработке истории {symbol} {timeframe}: {e}")

    async def process_realtime_data(
        self, symbols: List[str], timeframes: List[str]
    ) -> None:
        """
        Загружает и сохраняет данные в реальном времени.
        """
        tasks = [
            asyncio.create_task(self._process_realtime_single(symbol, timeframe))
            for symbol in symbols
            for timeframe in timeframes
        ]
        if tasks:
            await asyncio.gather(*tasks)

    async def _process_realtime_single(self, symbol: str, timeframe: str) -> None:
        logger.info(f"Запуск WebSocket стрима: {symbol} {timeframe}")
        max_retries = 10
        retries = 0

        while retries < max_retries:
            try:
                data = await self.fetcher.fetch_realtime_data(symbol, timeframe)
                if data:
                    await self.storage.save_realtime_data(
                        symbol, timeframe, data
                    )  # Универсальный метод
                    retries = 0  # СБРОС СЧЕТЧИКА после успеха
                    logger.debug(f"Обновлены данные для {symbol}")
            except Exception as e:
                retries += 1
                logger.error(
                    f"Ошибка WebSocket {symbol}: {e}. Попытка {retries}/{max_retries}"
                )
                await asyncio.sleep(min(retries * 5, 60))  # Экспоненциальная задержка

        logger.error(
            f"Поток {symbol} {timeframe} окончательно остановлен после {max_retries} ошибок."
        )
