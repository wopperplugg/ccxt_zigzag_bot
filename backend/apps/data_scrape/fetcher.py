import asyncio
from datetime import datetime
from typing import List
import ccxtpro
from apps.api.models import OHLCV


class DataFetcher:
    """
    Класс для загрузки и сохранения OHLCV данных с биржи.

    Поддерживает различные биржи через библиотеку ccxt.
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __init__(self, exchange_name: str = "binance") -> None:
        """
        Иницилизация обьекта для работы с биржей

        :param exchange_name: Название биржи (например, 'binance').
        """
        if exchange_name not in ccxtpro.exchanges:
            raise ValueError(f"Exchange '{exchange_name}' is not supported by ccxt.")
        self.exchange: ccxtpro.Exchange = getattr(ccxtpro, exchange_name)()

    async def fetch_ohlcv_realtime(
        self, symbol: str, timeframe: str
    ) -> List[List[float]]:
        """
        Загружает OHLCV данные для указаной торговой пары и таймфрейма

        :param symbol: Торговая пара (например, 'BTC/USDT').
        :param timeframe: Таймфрейм (например, '1h', '15m').
        :param limit: Максимальное количество свечей для загрузки.
        :return: Список свечей, где каждая свеча представлена списком [timestamp, open, high, low, close, volume].
        """
        retry_delay = 5
        max_retries = 10
        retries = 0
        while True:
            try:
                ohlcv = await self.exchange.watch_ohlcv(symbol, timeframe)
                print(f"поток данных для OHLCV для {symbol} {timeframe}")
                self.store_ohlcv(symbol, timeframe, ohlcv)
                retries = 0
                retry_delay = 5

            except Exception as e:
                retries += 1
                if retries > max_retries:
                    print(
                        f"ошибка получения ohlcv данных для {symbol} {timeframe}: {e}"
                    )
                    break

                print(f"повторное подключение через {retry_delay} секунд...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2

    def store_ohlcv(
        self, symbol: str, timeframe: str, ohlcv_data: List[List[float]]
    ) -> None:
        """
        Сохраняет OHLCV данные в базу данных

        :param symbol: Торговая пара (например, 'BTC/USDT').
        :param timeframe: Таймфрейм (например, '1h', '15m').
        :param ohlcv_data: Список свечей для сохранения.
        """
        for data in ohlcv_data:
            timestamp_ms: float = data[0]
            candle_time: datetime = datetime.fromtimestamp(timestamp_ms / 1000)
            open_price: float = data[1]
            high_price: float = data[2]
            low_price: float = data[3]
            close_price: float = data[4]
            volume: float = data[5]

            OHLCV.objects.get_or_create(
                symbol=symbol,
                timeframe=timeframe,
                candle_time=candle_time,
                defaults={
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                },
            )

    async def run(self, symbols: List[str], timeframes: List[str]) -> None:
        """
        основной метод для загрузки и сохранения данных

        :param symbols: Список торговых пар (например, ['BTC/USDT', 'ETH/USDT']).
        :param timeframes: Список таймфреймов (например, ['1h', '15m']).
        """
        tasks = []
        for symbol in symbols:
            for timeframe in timeframes:
                task = asyncio.create_task(self.fetch_ohlcv_realtime(symbol, timeframe))
                tasks.append(task)
        await asyncio.gather(*tasks)


async def main():
    symbols = ["BTC/USDT", "ETH/USDT"]
    timeframes = ["1h", "15m"]

    async with DataFetcher() as fetcher:
        await fetcher.run(symbols, timeframes)


if __name__ == "__main__":
    asyncio.run(main())
