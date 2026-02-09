from rest_framework import serializers
from .models import OHLCV
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class OHLCVSerializer(serializers.ModelSerializer):
    candle_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S%z")

    class Meta:
        model = OHLCV
        fields = [
            "symbol",
            "timeframe",
            "candle_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

    def validate_candle_time(self, value):
        """
        проверка что время свечи не из будущего
        """
        if value > timezone.now():
            raise serializers.ValidationError(
                "время свечи не может быть в будущем времени"
            )
        return value

    def validate_volume(self, value):
        if value < 0:
            raise serializers.ValidationError("обьем не может быть отрицательным")
        return value

    def validate(self, data):
        try:
            open_price = data.get("open")
            high_price = data.get("high")
            low_price = data.get("low")
            close_price = data.get("close")

            if high_price < low_price:
                raise serializers.ValidationError("high не может быть меньше low")
            if not (low_price <= open_price <= high_price):
                raise serializers.ValidationError("open должно быть между low и high")
            if not (low_price <= close_price <= high_price):
                raise serializers.ValidationError("close должно быть между low и high")
            return data
        except Exception as e:
            logger.error(f"Ошибка валидации OHLCV: {e}")
            raise
