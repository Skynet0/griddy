from abc import ABC, abstractmethod
from dataclasses import dataclass
import grilops
from grilops import Symbol, SymbolSet
import grilops.loops
import grilops.regions
import grilops.shapes
from typing import List, Tuple
from z3 import Solver

from puzzles.puzzle_utils import rect_loop_symbols

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

        # Instantiate loop symbols first to get the direction associations
        self.__symbol_set = rect_loop_symbols()
        new_symbols = {}

        for d in pd:
            if d.height != self.__height or d.width != self.__width:
                raise ValueError((
                    'not all PuzzleData have same dimensions:\n' +
                    'expected: ({},{})\n' + 
                    'got ({},{})')
                    .format(self.__height, self.__width, d.height, d.width))

            # Delegate genre, extract symbols
            from puzzles.genres import puzzle_genres
            genre_module = puzzle_genres.get(d.genre)
            if genre_module is None:
                raise ValueError('Unknown genre: {}'.format(d.genre))

            sym: Symbol
            for _, sym in \
                getattr(genre_module, SYMBOL_METHOD)().symbols.items():
                if sym.name in new_symbols and \
                    new_symbols[sym.name] != sym.label:
                    raise ValueError('Same symbol has different labels')
                new_symbols[sym.name] = sym.label
                self.sym.append(name=sym.name, label=sym.label)

        self.__lc: grilops.loops.LoopConstrainer = None
        self.__rc: grilops.regions.RegionConstrainer = None
        self.__sc: grilops.shapes.ShapeConstrainer = None

        self.__lattice = grilops.get_rectangle_lattice(self.height, self.width)
        self.__sg = grilops.SymbolGrid(self.lattice, self.sym)
        
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
    def sym(self) -> grilops.loops.LoopSymbolSet:
        return self.__symbol_set

    @property
    def sg(self) -> grilops.SymbolGrid:
        return self.__sg

    @property
    def lc(self) -> grilops.loops.LoopConstrainer:
        return self.__lc

    def set_lc(self, lc: grilops.loops.LoopConstrainer):
        self.__lc = lc

    @property
    def rc(self) -> grilops.regions.RegionConstrainer:
        return self.__rc

    def set_rc(self, rc: grilops.regions.RegionConstrainer):
        self.__rc = rc

    @property
    def set_sc(self) -> grilops.shapes.ShapeConstrainer:
        return self.__sc

    def sc(self, sc: grilops.shapes.ShapeConstrainer):
        self.__sc = sc

class BasePuzzleGenre(ABC):
    @staticmethod
    @abstractmethod
    def symbols() -> SymbolSet:
        pass

    @staticmethod
    @abstractmethod
    def add_constraints(puzzle: Puzzle, pd: PuzzleData) -> None:
        pass
