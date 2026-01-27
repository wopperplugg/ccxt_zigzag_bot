from django.core.management.base import BaseCommand
import asyncio
from data_scrape.fetcher import RestAPIFetcher, WebSocketDataFetcher
from data_scrape.storage import DatabaseStorage
from data_scrape.processor import DataProcessor
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Запускает процессор данных для загрузки исторических и реалтайм данных."

    def handle(self, *args, **options):
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Программа завершена пользователем."))

    async def main(self):
        # Загрузка исторических данных
        historical_fetcher = RestAPIFetcher("binance")
        symbols = ["BTC/USDT", "ETH/USDT"]
        timeframes = ["1h", "15m"]

        for symbol in symbols:
            for timeframe in timeframes:
                start_date = int(
                    (datetime.now() - timedelta(days=365)).timestamp() * 1000
                )
                end_date = int(datetime.now().timestamp() * 1000)
                data = await historical_fetcher.fetch_historical_data(
                    symbol, timeframe, start_date, end_date
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Загружено {len(data)} свечей для {symbol} {timeframe}"
                    )
                )

        # Загрузка данных в реальном времени
        realtime_fetcher = WebSocketDataFetcher("binance")

        async with realtime_fetcher:
            for symbol in symbols:
                for timeframe in timeframes:
                    data = await realtime_fetcher.fetch_realtime_data(symbol, timeframe)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Получены новые свечи для {symbol} {timeframe}: {len(data)}"
                        )
                    )
