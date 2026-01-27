from decimal import Decimal
from django.db import connection
from asgiref.sync import sync_to_async
from datetime import datetime
from typing import List
from interfaces import IDataStorage


class OHLCV:
    symbol = str
    timeframe = str
    candle_time = datetime
    open = Decimal
    high = Decimal
    low = Decimal
    close = Decimal
    volume = Decimal


class DatabaseStorage(IDataStorage):
    @sync_to_async
    def save_historical_data(
        self, symbol: str, timeframe: str, ohlcv_data: [List[float]]
    ) -> None:
        """
        Сохраняет исторические данные через bulk_create.
        """
        candles = [
            OHLCV(
                symbol=symbol,
                timeframe=timeframe,
                candle_time=datetime.fromtimestamp(data[0] / 1000),
                open=Decimal(str(data[1])),
                high=Decimal(str(data[2])),
                low=Decimal(str(data[3])),
                close=Decimal(str(data[4])),
                volume=Decimal(str(data[5])),
            )
            for data in ohlcv_data
        ]
        OHLCV.objects.bulk_create(candles, ignore_conflicts=True)

    @sync_to_async
    def save_realtime_data(
        self, symbol: str, timeframe: str, ohlcv_data: [List[float]]
    ) -> None:
        """
        Сохраняет данные в реальном времени через сырой SQL.
        """
        with connection.cursor() as cursor:
            for data in ohlcv_data:
                timestamp_ms = data[0]
                candle_time = datetime.fromtimestamp(timestamp_ms / 1000)
                open_price, high_price, low_price, close_price, volume = data[1:6]

                cursor.execute(
                    """
                    INSERT INTO ohlcv (symbol, timeframe, candle_time, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, timeframe, candle_time) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume;
                """,
                    [
                        symbol,
                        timeframe,
                        candle_time,
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                        volume,
                    ],
                )
