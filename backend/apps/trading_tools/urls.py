# trading_tools/urls.py
from django.urls import path
from .views import ZigZagView

urlpatterns = [
    path("zigzag/", ZigZagView.as_view(), name="zigzag"),
]
