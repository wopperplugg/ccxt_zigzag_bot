from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime
from .models import OHLCV
from .serializers import OHLCVSerializer


class CoinListView(APIView):
    """возвращает список уникальных монет"""

    def get(self, request):
        coins = OHLCV.objects.values_list("symbol", flat=True).distinct()
        return Response(list(coins))


class OHLCVPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class OHLCVAPIView(APIView):
    """представление для получения ohlcv данных по символу и таймфрейму"""

    pagination_class = OHLCVPagination

    def get(self, request, symbol: str, timeframe: str) -> Response:
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
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not queryset.exists():
            return Response(
                {"detail": f"данные для {symbol} {timeframe} не найдены"},
                status=status.HTTP_404_NOT_FOUND,
            )
        paginator = self.pagination_class
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = OHLCVSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
