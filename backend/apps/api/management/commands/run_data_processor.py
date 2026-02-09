from django.core.management.base import BaseCommand
import asyncio
import logging
from ....data_scrape.fetcher import RestAPIFetcher, WebSocketDataFetcher
from ....data_scrape.storage import DatabaseStorage
from ....data_scrape.processor import DataProcessor
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Command(BaseCommand):
    help = "Запускает процессор данных для загрузки исторических и реалтайм данных."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск команды..."))
        try:
            asyncio.run(self.main())
        except KeyboardInterrupt:
            logger.warning("Программа принудительно завершена пользователем")
            self.stdout.write(self.style.WARNING("Программа завершена пользователем."))
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))

    async def main(self):
        logger.info("Инициализация компонентов...")
        storage = DatabaseStorage()
        historical_fetcher = RestAPIFetcher("binance")
        realtime_fetcher = WebSocketDataFetcher("binance")  # Используем WebSocket
        processor = DataProcessor(fetcher=historical_fetcher, storage=storage)

        # Загрузка исторических данных
        symbols = ["BTC/USDT", "ETH/USDT"]
        timeframes = ["1h", "15m"]

        logger.info(f"Начало загрузки исторических данных: {symbols}, TF: {timeframes}")
        await processor.process_historical_data(symbols, timeframes)
        logger.info("Исторические данные успешно загружены.")

        # Загрузка данных в реальном времени
        logger.info("Переключение на WebSocket для реального времени...")
        processor.fetcher = realtime_fetcher  # Меняем fetcher на WebSocket
        logger.info("Запуск реального времени (WS)...")
        await processor.process_realtime_data(symbols, timeframes)
