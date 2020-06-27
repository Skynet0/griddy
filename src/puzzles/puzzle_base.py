from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple
from z3 import Solver


@dataclass
class PuzzleData:
    genre: str
    width: int
    height: int
    payload: List[str]


class Puzzle:
    def __init__(
        self,
        pd: List[PuzzleData],
        solver: Solver = None
    ) -> None:
        self.__height : int = pd[0].height
        self.__width : int = pd[0].width
        for d in pd:
            if d.height != self.__height or d.width != self.__width:
                raise ValueError((
                    'not all PuzzleData have same dimensions:\n' +
                    'expected: ({},{})\n' + 
                    'got ({},{})')
                    .format(self.__height, self.__width, d.height, d.width))
            # Delegate genre, extract symbols
            
    @property
    def solver(self) -> Solver:
        return None

class BasePuzzleGenre(ABC):
    @staticmethod
    @abstractmethod
    def symbols() -> List[Tuple[str, str]]:
        pass

    @staticmethod
    @abstractmethod
    def add_constraints(puzzle: Puzzle) -> None:
        pass
