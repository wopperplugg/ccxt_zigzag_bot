from abc import ABC, abstractmethod
from typing import List, Dict


class PatternDetector(ABC):
    @abstractmethod
    def detect(self, data: List[Dict]) -> bool:
        """
        обнаруживает паттерн в данных
        :param точки zigzag
        :return true, если паттерн обнаружен
        """
        pass
