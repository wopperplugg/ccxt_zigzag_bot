# определяет url маршруты для приложения zzBot
from django.urls import path
from .views import OHLCVAPIView, CoinListView

app_name = "api"

urlpatterns = [
    path(
        "ohlcv/<str:symbol>/<str:timeframe>/", OHLCVAPIView.as_view(), name="ohlcv-data"
    ),
    path("coins/", CoinListView.as_view(), name="coin-list"),
]
