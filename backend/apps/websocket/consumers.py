# apps/websocket/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OHLCVConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("=== WebSocket connection attempt ===")

        # Получаем параметры
        symbol_param = self.scope["url_route"]["kwargs"]["symbol"]
        # Заменяем дефис на слэш
        symbol = symbol_param.replace("-", "/")
        timeframe = self.scope["url_route"]["kwargs"]["timeframe"]

        self.symbol = symbol
        self.timeframe = timeframe
        self.room_group_name = f'ohlcv_{symbol.replace("/", "_")}_{timeframe}'

        print(
            f"Symbol param: {symbol_param}, Processed symbol: {symbol}, Timeframe: {timeframe}"
        )
        print(f"Room name: {self.room_group_name}")

        try:
            # Присоединяемся к группе
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print("=== WebSocket accepted! ===")
        except Exception as e:
            print(f"=== Connection error: {e} ===")
            import traceback

            traceback.print_exc()

    async def disconnect(self, close_code):
        print(f"=== WebSocket disconnected: {close_code} ===")
        try:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            print(f"Disconnect error: {e}")

    async def receive(self, text_data):
        print(f"=== Received: {text_data} ===")
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "subscribe":
                print("=== Subscribe action received ===")
                # Здесь можно вернуть последние данные из БД
                await self.send(
                    text_data=json.dumps(
                        {"type": "initial_data", "candles": [], "zigzag": []}
                    )
                )
        except Exception as e:
            print(f"=== Receive error: {e} ===")

    async def ohlcv_update(self, event):
        try:
            await self.send(
                text_data=json.dumps(
                    {"type": "candle_update", "candle": event["candle"]}
                )
            )
        except Exception as e:
            print(f"Send error: {e}")
