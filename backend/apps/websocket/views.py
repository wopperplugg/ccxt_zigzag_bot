from ..api.serializers import OHLCVSerializer
from ..api.models import OHLCV
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views import View


# Create your views here.
class OHLCVBroadcaster:
    """Сервис для трансляции обновлений через WebSockets"""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def broadcast_candle(self, symbol: str, timeframe: str, candle_data: dict):
        group_name = f"ohlcv_{symbol}_{timeframe}"
        async_to_sync(self.channel_layer.group_send)(
            group_name, {"type": "ohlcv_update", "candle": candle_data}
        )


class OHLCVTriggerView(View):
    # Внедряем зависимость (можно через __init__, но в Django проще так)
    broadcaster = OHLCVBroadcaster()

    def post(self, request, symbol, timeframe):
        """Ручной триггер обновления через POST запрос"""

        candle = (
            OHLCV.objects.filter(symbol=symbol, timeframe=timeframe)
            .order_by("-candle_time")
            .first()
        )

        if not candle:
            return JsonResponse({"error": "Candle not found"}, status=404)

        # Сериализация
        serializer = OHLCVSerializer(candle)

        # Отправка через сервис
        self.broadcaster.broadcast_candle(symbol, timeframe, serializer.data)

        return JsonResponse({"status": "updated", "symbol": symbol})
