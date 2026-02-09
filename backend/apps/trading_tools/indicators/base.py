from abc import ABC, abstractmethod
from typing import List, Dict


class Indicator(ABC):
    @abstractmethod
    def calculate(self, data: List[Dict]) -> List[Dict]:
        """
        вычисляет индикатор на основе входных данных
        """
        pass
