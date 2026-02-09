from abc import ABC, abstractmethod
from typing import List, Dict


class StrategyExecutor(ABC):
    @abstractmethod
    def execute(self, data: List[Dict]) -> str:
        """
        выполняет торговую стратегию

        :param точки ZigZag]
        :return: сигнал для открытия позиции("Long", "SHORT", None)
        """
        pass
