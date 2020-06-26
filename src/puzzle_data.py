from dataclasses import dataclass
from typing import List

@dataclass
class PuzzleData:
    genre: str
    width: int
    height: int
    payload: List[str]
