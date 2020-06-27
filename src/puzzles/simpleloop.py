
import grilops
from grilops import SymbolSet
from grilops.loops import LoopConstrainer
from grilops.geometry import Point
from z3 import Not

from puzzles.puzzle_base import BasePuzzleGenre, Puzzle, PuzzleData

SIMPLE_LOOP_BLACK_CELL = '*'

class SimpleLoop(BasePuzzleGenre):
    @staticmethod
    def symbols() -> SymbolSet:
        return SymbolSet([
            ("BLACK", chr(0x25AE))
        ])

    @staticmethod
    def add_constraints(puzzle: Puzzle, pd: PuzzleData):
        if puzzle.lc is None:
            puzzle.set_lc(LoopConstrainer(puzzle.sg, single_loop=True))

        if len(pd.payload) < puzzle.height:
            raise RuntimeError('too few lines in payload for height {}'
                .format(puzzle.height))

        givens = [r.strip().split(' ') for r in pd.payload[:puzzle.height]]

        for p in puzzle.lattice.points:
            given = givens[p.y][p.x]
            if given == SIMPLE_LOOP_BLACK_CELL:
                puzzle.sg.solver.add(puzzle.sg.cell_is(p, puzzle.sym.BLACK))
            # Explicitly denote that cell is on loop (puzzle might have other symbols)
            else:
                puzzle.sg.solver.add(puzzle.sym.is_loop(puzzle.sg.grid.get(p)))
        