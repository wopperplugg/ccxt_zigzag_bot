from typing import List, Dict
from .base import Indicator


class ZigZagCalculator(Indicator):
    def __init__(self, deviation: float = 0.05):
        self.deviation = deviation

    def calculate(self, data: List[Dict]) -> List[Dict]:
        if not data:
            return []

        zigzag_points = []

        # Инициализируем первой свечой
        first_candle = data[0]
        last_p = {
            "time": first_candle["candle_time"],
            "price": float(first_candle["close"]),
        }
        zigzag_points.append(last_p)

        trend = 0  # 1 - вверх, -1 - вниз, 0 - ожидание

        for candle in data[1:]:
            high = float(candle["high"])
            low = float(candle["low"])

            # Расчет отклонений от последней точки
            dev_up = (high - last_p["price"]) / last_p["price"]
            dev_down = (last_p["price"] - low) / last_p["price"]

            if trend == 0:
                if dev_up >= self.deviation:
                    trend = 1
                    last_p = {"time": candle["candle_time"], "price": high}
                    zigzag_points.append(last_p)
                elif dev_down >= self.deviation:
                    trend = -1
                    last_p = {"time": candle["candle_time"], "price": low}
                    zigzag_points.append(last_p)

            elif trend == 1:
                # Если в восходящем тренде цена ставит новый максимум — обновляем последнюю точку
                if high > last_p["price"]:
                    last_p["price"] = high
                    last_p["time"] = candle["candle_time"]
                # Если цена упала ниже порога — разворот вниз
                elif dev_down >= self.deviation:
                    trend = -1
                    last_p = {"time": candle["candle_time"], "price": low}
                    zigzag_points.append(last_p)

            elif trend == -1:
                # Если в нисходящем тренде ставим новый минимум — обновляем последнюю точку
                if low < last_p["price"]:
                    last_p["price"] = low
                    last_p["time"] = candle["candle_time"]
                # Если цена выросла выше порога — разворот вверх
                elif dev_up >= self.deviation:
                    trend = 1
                    last_p = {"time": candle["candle_time"], "price": high}
                    zigzag_points.append(last_p)

        return zigzag_points
