from django.urls import path, include
from .views import OHLCVTriggerView

urlpatterns = [
    path(
        "api/trigger-update/<str:symbol>/<str:timeframe>/",
        OHLCVTriggerView.as_view(),
        name="trigger-websocket-update",
    ),
]
