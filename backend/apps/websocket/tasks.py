import asyncio
import json
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone
from ..api.models import OHLCV
from ..api.serializers import OHLCVSerializer


async def broadcast_ohlcv_updates():
    """
    background task  для переодического обновления данных
    """
    channels_layer = get_channel_layer()

    while True:
        recent_candles = await get_recent_candles()

        for symbol_timeframe, candle_data in recent_candles.items():
            symbol, timeframe = symbol_timeframe.split("_")

            await channels_layer.group_send(
                f"ohlcv_{symbol}_{timeframe}",
                {"type": "ohlcv_update", "candle": candle_data},
            )

        await asyncio.sleep(1)


@sync_to_async
def get_recent_candles():
    from django.db.models import Max, Q
    from datetime import timedelta

    # 1. Сначала находим только нужные ключи (symbol, timeframe, max_time)
    # Это один легкий запрос
    threshold = timezone.now() - timedelta(seconds=30)
    latest_meta = (
        OHLCV.objects.values("symbol", "timeframe")
        .annotate(latest_time=Max("candle_time"))
        .filter(latest_time__gte=threshold)
    )

    if not latest_meta:
        return {}

    # 2. Строим Q-фильтр для получения всех объектов ОДНИМ запросом
    query_filter = Q()
    for item in latest_meta:
        query_filter |= Q(
            symbol=item["symbol"],
            timeframe=item["timeframe"],
            candle_time=item["latest_time"],
        )

    # 3. Выполняем один запрос вместо десятков в цикле
    candles = OHLCV.objects.filter(query_filter)

    return {f"{c.symbol}_{c.timeframe}": OHLCVSerializer(c).data for c in candles}
