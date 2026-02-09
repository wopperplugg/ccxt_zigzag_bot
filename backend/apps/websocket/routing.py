from django.urls import path
from .consumers import OHLCVConsumer

websocket_urlpatterns = [
    path("ws/ohlcv/<str:symbol>/<str:timeframe>/", OHLCVConsumer.as_asgi()),
]
