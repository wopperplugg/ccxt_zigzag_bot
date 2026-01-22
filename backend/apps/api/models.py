from django.db import models


class OHLCV(models.Model):
    pk = models.CompositePrimaryKey("symbol", "timeframe", "candle_time")
    symbol = models.CharField(max_length=20, db_index=True)
    timeframe = models.CharField(max_length=10, db_index=True)
    candle_time = models.DateTimeField(db_index=True)

    open = models.DecimalField(max_digits=20, decimal_places=8)
    high = models.DecimalField(max_digits=20, decimal_places=8)
    low = models.DecimalField(max_digits=20, decimal_places=8)
    close = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=20, decimal_places=8)

    class Meta:
        db_table = "ohlcv"
        indexes = [
            models.Index(fields=["symbol", "timeframe", "-candle_time"]),
        ]

    def __str__(self):
        return f"монета:{self.symbol} таймфрейм:{self.timeframe} время свечи: {self.candle_time}"
