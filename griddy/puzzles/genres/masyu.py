from collections import defaultdict
from grilops import SymbolGrid, get_rectangle_lattice
from grilops.geometry import Point, Vector
from grilops.loops import LoopConstrainer, LoopSymbolSet
from typing import Callable, Optional, Tuple
from z3 import Implies, Or, SolverFor

from griddy.puzzles.common.puzzle_base import PuzzleGivens

GENRE_ALIASES = ['masyu', 'mashu']

MASYU_WHITE_PEARL = 1
MASYU_BLACK_PEARL = 2


def parse_url(url: str) -> PuzzleGivens:
    params = url.split('/')
    height = int(params[-2])
    width = int(params[-3])
    payload = params[-1]

    genre = params[-4].split('?')[-1]
    if genre not in GENRE_ALIASES:
        raise ValueError('Given URL is not a masyu')

    circles: PuzzleGivens = defaultdict(int)
    cell_num = 0
    payload_len = min(int((height * width + 2) / 3), len(payload))

    for c in payload[:payload_len]:
        n = int(c, 27)
        for t in [3**p for p in range(2, -1, -1)]:
            v = int(n / t) % 3
            if v > 0:
                y = int(cell_num / width)
                x = cell_num % width
                circles[Point(y, x)] = v
            cell_num += 1

    return circles


def load_puzzle(
    url: str,
    ura_mashu=False
) -> Tuple[SymbolGrid, Optional[Callable[[Point, int], str]]]:
    params = url.split('/')
    height = int(params[-2])
    width = int(params[-3])

    givens: PuzzleGivens = parse_url(url)

    lattice = get_rectangle_lattice(height, width)
    sym = LoopSymbolSet(lattice)
    sym.append('EMPTY', ' ')
    qf_idl_solver = SolverFor('QF_IDL')
    sg = SymbolGrid(lattice, sym, solver=qf_idl_solver)
    lc = LoopConstrainer(sg, single_loop=True)

    straights = [sym.NS, sym.EW]
    turns = [sym.NE, sym.SE, sym.SW, sym.NW]

    # CODE BELOW IS FROM
    # https://github.com/obijywk/grilops/blob/master/examples/masyu.py

    # If we have givens, then restrict a pearl to reduce possibilities
    if not len(givens) == 0:
        sg.solver.add(lc.loop_order_grid[next(iter(givens.keys()))] == 0)

    for p in sg.lattice.points:
        if givens[p]:
            if (givens[p] == MASYU_BLACK_PEARL) == (not ura_mashu):
                # The loop must turn at a black circle.
                sg.solver.add(sg.cell_is_one_of(p, turns))

                # All connected adjacent cells must contain straight segments.
                for n in sg.edge_sharing_neighbors(p):
                    if n.location.y < p.y:
                        sg.solver.add(
                            Implies(sg.cell_is_one_of(p, [sym.NE, sym.NW]),
                                    sg.cell_is(n.location, sym.NS)))
                    if n.location.y > p.y:
                        sg.solver.add(
                            Implies(sg.cell_is_one_of(p, [sym.SE, sym.SW]),
                                    sg.cell_is(n.location, sym.NS)))
                    if n.location.x < p.x:
                        sg.solver.add(
                            Implies(sg.cell_is_one_of(p, [sym.SW, sym.NW]),
                                    sg.cell_is(n.location, sym.EW)))
                    if n.location.x > p.x:
                        sg.solver.add(
                            Implies(sg.cell_is_one_of(p, [sym.NE, sym.SE]),
                                    sg.cell_is(n.location, sym.EW)))
            else:
                # The loop must go straight through a white circle.
                sg.solver.add(sg.cell_is_one_of(p, straights))

                # At least one connected adjacent cell must turn.
                if 0 < p.y < height - 1:
                    sg.solver.add(
                        Implies(
                            sg.cell_is(p, sym.NS),
                            Or(
                                sg.cell_is_one_of(p.translate(Vector(-1, 0)),
                                                  turns),
                                sg.cell_is_one_of(p.translate(Vector(1, 0)),
                                                  turns))))
                if 0 < p.x < width - 1:
                    sg.solver.add(
                        Implies(
                            sg.cell_is(p, sym.EW),
                            Or(
                                sg.cell_is_one_of(p.translate(Vector(0, -1)),
                                                  turns),
                                sg.cell_is_one_of(p.translate(Vector(0, 1)),
                                                  turns))))

    def print_fn(p: Point, i: int) -> str:
        if givens[p] == MASYU_WHITE_PEARL:
            return chr(0x25cb)
        if givens[p] == MASYU_BLACK_PEARL:
            return chr(0x25cf)
        return None

    return sg, print_fn
