from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime
from .models import OHLCV
from .serializers import OHLCVSerializer
from apps.trading_tools.indicators.zigzag import ZigZagCalculator
from apps.trading_tools.patterns.head_and_shoulders import HeadAndShouldersDetector
from apps.trading_tools.strategies.simple_strategy import SimpleStrategy


class CoinListView(APIView):
    """возвращает список уникальных монет"""

    def get(self, request):
        coins = OHLCV.objects.values_list("symbol", flat=True).distinct()
        return Response(list(coins))


class OHLCVPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class OHLCVAPIView(APIView):
    def get(self, request, symbol_encoded: str, timeframe: str) -> Response:
        # Просто заменяем дефис на слэш — НИКАКОГО BASE64!
        symbol = symbol_encoded.replace("-", "/")

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = OHLCV.objects.filter(symbol=symbol, timeframe=timeframe).order_by(
            "candle_time"
        )

        if start_date and end_date:
            if start_date > end_date:
                start_date, end_date = end_date, start_date
            try:
                start_date = datetime.fromisoformat(start_date)
                end_date = datetime.fromisoformat(end_date)
                queryset = queryset.filter(candle_time__range=(start_date, end_date))
            except ValueError:
                return Response(
                    {"detail": "Неверный формат даты. Используйте ISO 8601."},
                    status=400,
                )

        if not queryset.exists():
            return Response(
                {"detail": f"Данные для {symbol} {timeframe} не найдены"},
                status=404,
            )

        paginator = OHLCVPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OHLCVSerializer(result_page, many=True)

        candles = [
            {
                "candle_time": item["candle_time"],
                "open": item["open"],
                "high": item["high"],
                "low": item["low"],
                "close": item["close"],
            }
            for item in serializer.data
        ]

        try:
            zigzag_calculator = ZigZagCalculator(deviation=0.01)
            zigzag_points = zigzag_calculator.calculate(candles)
            pattern_detector = HeadAndShouldersDetector()
            pattern_detected = pattern_detector.detect(zigzag_points)
            strategy_executor = SimpleStrategy()
            signal = strategy_executor.execute(zigzag_points)
        except Exception as e:
            zigzag_points = []
            pattern_detected = False
            signal = None

        # Создаем ответ вручную, используя пагинацию
        response_data = {
            "ohlcv": serializer.data,
            "zigzag": zigzag_points,
            "signals": {
                "pattern": "head and shoulders" if pattern_detected else None,
                "trade_signal": signal,
            },
        }

        # Возвращаем пагинированный ответ
        return paginator.get_paginated_response(response_data)
