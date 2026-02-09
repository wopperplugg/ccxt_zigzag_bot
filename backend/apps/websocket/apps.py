from django.apps import AppConfig


class WebsocketConfig(AppConfig):
    name = "apps.websocket"

    def ready(self):
        import threading
        from django.conf import settings

        # Проверяем, что мы не в миграциях
        if settings.DEBUG:
            # Запуск background задач для отправки обновлений
            def send_updates():
                import time
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                channel_layer = get_channel_layer()

                while True:
                    try:
                        # Здесь вы можете отправлять обновления, когда появляются новые данные
                        # Например, если у вас есть задача, которая обновляет данные
                        time.sleep(5)  # Проверка каждые 5 секунд
                    except Exception as e:
                        print(f"Background task error: {e}")
                        break

            # Запускаем в отдельном потоке только в режиме разработки
            thread = threading.Thread(target=send_updates, daemon=True)
            thread.start()
