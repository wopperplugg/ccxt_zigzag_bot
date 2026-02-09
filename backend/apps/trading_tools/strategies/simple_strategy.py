from .base import StrategyExecutor
from typing import List, Dict


class SimpleStrategy(StrategyExecutor):
    def execute(self, data: List[Dict]) -> str:
        if len(data) < 2:
            return None
        last_point = data[-1]
        prev_point = data[-2]

        if last_point["price"] > prev_point["price"]:
            return "LONG"
        elif last_point["price"] < prev_point["price"]:
            return "SHORT"
        return None
