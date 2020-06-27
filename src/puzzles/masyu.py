import grilops
from grilops import SymbolSet
from grilops.loops import LoopConstrainer
from grilops.geometry import Point, Vector
from z3 import Implies, Not, Or

from puzzles.puzzle_base import BasePuzzleGenre, Puzzle, PuzzleData

MASYU_EMPTY = '.'
MASYU_WHITE_CIRCLE = '1'
MASYU_BLACK_CIRCLE = '2'

class Masyu(BasePuzzleGenre):
    @staticmethod
    def symbols() -> SymbolSet:
        return SymbolSet([
            ("EMPTY", " ")
        ])

    @staticmethod
    def add_constraints(puzzle: Puzzle, pd: PuzzleData):
        sg = puzzle.sg
        sym = puzzle.sym

        if puzzle.lc is None:
            puzzle.set_lc(LoopConstrainer(sg, single_loop=True))

        straights = [sym.NS, sym.EW]
        turns = [sym.NE, sym.SE, sym.SW, sym.NW]

        if len(pd.payload) < puzzle.height:
            raise RuntimeError('too few lines in payload for height {}'
                .format(puzzle.height))

        givens = [r.strip().split(' ') for r in pd.payload[:puzzle.height]]

        # CODE BELOW IS FROM
        # https://github.com/obijywk/grilops/blob/master/examples/masyu.py

        p = min(p for p in puzzle.sg.lattice.points
            if givens[p.y][p.x] != MASYU_EMPTY)
        sg.solver.add(puzzle.lc.loop_order_grid[p] == 0)

        for p in puzzle.lattice.points:
            given = givens[p.y][p.x]
            if given == MASYU_BLACK_CIRCLE:
                # The loop must turn at a black circle.
                sg.solver.add(sg.cell_is_one_of(p, turns))

                # All connected adjacent cells must contain straight loop segments.
                for n in sg.edge_sharing_neighbors(p):
                    if n.location.y < p.y:
                        sg.solver.add(Implies(
                            sg.cell_is_one_of(p, [sym.NE, sym.NW]),
                            sg.cell_is(n.location, sym.NS)
                        ))
                    if n.location.y > p.y:
                        sg.solver.add(Implies(
                            sg.cell_is_one_of(p, [sym.SE, sym.SW]),
                            sg.cell_is(n.location, sym.NS)
                        ))
                    if n.location.x < p.x:
                        sg.solver.add(Implies(
                            sg.cell_is_one_of(p, [sym.SW, sym.NW]),
                            sg.cell_is(n.location, sym.EW)
                     ))
                    if n.location.x > p.x:
                        sg.solver.add(Implies(
                            sg.cell_is_one_of(p, [sym.NE, sym.SE]),
                                sg.cell_is(n.location, sym.EW)
                        ))
            elif given == MASYU_WHITE_CIRCLE:
                # The loop must go straight through a white circle.
                sg.solver.add(sg.cell_is_one_of(p, straights))

                # At least one connected adjacent cell must turn.
                if 0 < p.y < len(givens) - 1:
                    sg.solver.add(Implies(
                        sg.cell_is(p, sym.NS),
                        Or(
                            sg.cell_is_one_of(p.translate(Vector(-1, 0)), turns),
                            sg.cell_is_one_of(p.translate(Vector(1, 0)), turns)
                        )
                    ))
                if 0 < p.x < len(givens[0]) - 1:
                    sg.solver.add(Implies(
                        sg.cell_is(p, sym.EW),
                        Or(
                            sg.cell_is_one_of(p.translate(Vector(0, -1)), turns),
                            sg.cell_is_one_of(p.translate(Vector(0, 1)), turns)
                        )
                    ))
        