# определяет url маршруты для приложения zzBot
from django.urls import path, include
from .views import OHLCVAPIView, CoinListView

app_name = "api"

urlpatterns = [
    path(
        "ohlcv/<str:symbol_encoded>/<str:timeframe>/",
        OHLCVAPIView.as_view(),
        name="ohlcv-data",
    ),
    path("coins/", CoinListView.as_view(), name="coin-list"),
    path("ws/", include("apps.websocket.urls")),
]
