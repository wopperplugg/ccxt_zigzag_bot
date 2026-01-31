from django.core.management.base import BaseCommand
import asyncio
from ....data_scrape.fetcher import RestAPIFetcher, WebSocketDataFetcher
from ....data_scrape.storage import DatabaseStorage
from ....data_scrape.processor import DataProcessor
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Запускает процессор данных для загрузки исторических и реалтайм данных."

    def handle(self, *args, **options):
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Программа завершена пользователем."))

    async def main(self):
        # Создание объектов
        storage = DatabaseStorage()
        historical_fetcher = RestAPIFetcher("binance")
        realtime_fetcher = WebSocketDataFetcher("binance")  # Используем WebSocket
        processor = DataProcessor(fetcher=historical_fetcher, storage=storage)

        # Загрузка исторических данных
        symbols = ["BTC/USDT", "ETH/USDT"]
        timeframes = ["1h", "15m"]

        await processor.process_historical_data(symbols, timeframes)

        # Загрузка данных в реальном времени
        processor.fetcher = realtime_fetcher  # Меняем fetcher на WebSocket
        await processor.process_realtime_data(symbols, timeframes)
