import asyncio
import ccxt.pro as ccxt
from datetime import datetime
from typing import List, Dict
from interfaces import IDataFetcher
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RestAPIFetcher(IDataFetcher):
    def __init__(self, exchange_name: str = "binance") -> None:
        if exchange_name not in ccxt.exchanges:
            raise ValueError(f"Exchange '{exchange_name}' is not supported by ccxt.")
        self.exchange = getattr(ccxt, exchange_name)()

    async def fetch_historical_data(
        self, symbol: str, timeframe: str, start_date: int, end_date: int
    ) -> List[List[float]]:
        all_candles = []
        since = start_date

        logging.info(f"Загрузка истории для {symbol}...")

        while since < end_date:
            try:
                ohlcv_list = await self.exchange.fetch_ohlcv(symbol, timeframe, since)

                if not ohlcv_list:
                    break

                all_candles.extend(ohlcv_list)
                since = ohlcv_list[-1][0] + 1

                await asyncio.sleep(self.exchange.rateLimit / 1000)

            except Exception as e:
                logging.error(f"Ошибка при получении истории {symbol}: {e}")
                break

        await self.exchange.close()
        return all_candles

    async def fetch_realtime_data(self, symbol, timeframe):
        raise NotImplementedError("RestAPIFetcher не поддерживает real-time данные")


class WebSocketDataFetcher(IDataFetcher):
    def __init__(self, exchange_name: str = "binance") -> None:
        if exchange_name not in ccxt.exchanges:
            raise ValueError(f"Exchange '{exchange_name}' is not supported.")
        self.exchange = getattr(ccxt, exchange_name)()
        self.last_saved: Dict[str, int] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self.exchange:
            await self.exchange.close()

    async def fetch_historical_data(self, *args, **kwargs):
        raise NotImplementedError("WebSocketFetcher не поддерживает историю.")

    async def fetch_realtime_data(
        self, symbol: str, timeframe: str
    ) -> List[List[float]]:
        retry_delay = 5
        max_retries = 10
        retries = 0
        key = f"{symbol}_{timeframe}"

        while True:
            try:
                ohlcv_list = await self.exchange.watch_ohlcv(symbol, timeframe)
                retries = 0

                if not ohlcv_list:
                    logging.info(
                        f"Пустой ответ для {symbol} {timeframe}. Продолжение..."
                    )
                    continue

                last_ts = self.last_saved.get(key, -1)
                new_candles = [c for c in ohlcv_list if c[0] > last_ts]

                if new_candles:
                    self.last_saved[key] = max(c[0] for c in new_candles)
                    logging.info(
                        f"Получены новые свечи для {symbol} {timeframe}: {len(new_candles)}"
                    )
                    return new_candles

            except Exception as e:
                retries += 1
                logging.error(
                    f"Ошибка при получении OHLCV для {symbol} {timeframe}: {e}"
                )
                if retries > max_retries:
                    logging.error(
                        f"Превышено количество попыток для {symbol} {timeframe}. Завершение."
                    )
                    break
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
