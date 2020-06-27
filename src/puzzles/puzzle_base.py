from abc import ABC, abstractmethod
from dataclasses import dataclass
import grilops
import grilops.loops
import grilops.regions
import grilops.shapes
from typing import List, Tuple
from z3 import Solver

from puzzles.genres import puzzle_genres

SYMBOL_METHOD = 'symbols'
ADD_CONSTRAINTS = 'add_constraints'

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
    ):
        self.__height : int = pd[0].height
        self.__width : int = pd[0].width

        symbols = {}

        for d in pd:
            if d.height != self.__height or d.width != self.__width:
                raise ValueError((
                    'not all PuzzleData have same dimensions:\n' +
                    'expected: ({},{})\n' + 
                    'got ({},{})')
                    .format(self.__height, self.__width, d.height, d.width))
            # Delegate genre, extract symbols
            genre_module = puzzle_genres.get(d.genre)
            if genre_module is None:
                raise ValueError('Unknown genre: {}'.format(d.genre))
            for sym, val in getattr(genre_module, SYMBOL_METHOD)():
                if sym in symbols and symbols[sym] != val:
                    raise ValueError('Same symbol has different values')
                symbols[sym] = val

        self.__symbol_set = grilops.SymbolSet(symbols.items())
            
        self.__lc: grilops.loops.LoopConstrainer = None
        self.__rc: grilops.regions.RegionConstrainer = None
        self.__sc: grilops.shapes.ShapeConstrainer = None

        self.__lattice = grilops.get_rectangle_lattice(self.height, self.width)
        self.__sg = grilops.SymbolGrid(self.lattice, self.__symbol_set)
        
        for d in pd:
            getattr(genre_module, ADD_CONSTRAINTS)(self, d)

    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def lattice(self) -> grilops.Lattice:
        return self.__lattice

    @property
    def symbol_et(self) -> grilops.SymbolSet:
        return self.__symbol_set

    @property
    def sg(self) -> grilops.SymbolGrid:
        return self.__sg

    @property
    def solver(self) -> Solver:
        return None

SymbolList = List[Tuple[str, str]]

class BasePuzzleGenre(ABC):
    @staticmethod
    @abstractmethod
    def symbols() -> SymbolList:
        pass

    @staticmethod
    @abstractmethod
    def add_constraints(puzzle: Puzzle, pd: PuzzleData) -> None:
        pass
