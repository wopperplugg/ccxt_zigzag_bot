from .base import PatternDetector
from typing import List, Dict


class HeadAndShouldersDetector(PatternDetector):
    def detect(self, data: List[Dict]) -> bool:
        if len(data) < 5:
            return False
        p1, p2, p3, p4, p5 = data[-5:]
        if (
            p1["price"] < p2["price"] > p3["price"] < p4["price"] > p5["price"]
            and p1["price"] < p5["price"]
            and p3["price"] < p1["price"]
        ):
            return True
        return False
