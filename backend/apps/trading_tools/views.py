from rest_framework.views import APIView
from rest_framework.response import Response
from .indicators.zigzag import ZigZagCalculator
from .patterns.head_and_shoulders import HeadAndShouldersDetector
from .strategies.simple_strategy import SimpleStrategy


class ZigZagView(APIView):
    def post(self, request):
        """
        принимает ohlcv и возвращает точки zigzag
        """
        data = request.data.get("data")
        deviation = request.data.get("deviation", 0.01)

        zigzag_calculator = ZigZagCalculator(deviation=deviation)
        zigzag_points = zigzag_calculator.calculate(data)

        return Response({"zigzag": zigzag_points})
