from collections import defaultdict
from grilops import SymbolGrid, get_rectangle_lattice
from grilops.geometry import Point
from grilops.loops import LoopConstrainer, LoopSymbolSet
from z3 import Not, SolverFor
from griddy.puzzles.common.puzzle_base import PuzzleGivens

GENRE_ALIASES = ['simpleloop']


def _parse_url(url: str) -> PuzzleGivens:
    params = url.split('/')
    width = int(params[-3])
    payload = params[-1]

    genre = params[-4].split('?')[-1]
    if genre not in GENRE_ALIASES:
        raise ValueError('Given URL is not a simpleloop')

    shaded: PuzzleGivens = defaultdict(bool)
    cell_num = 0

    for c in payload:
        n = int(c, 32)
        for b in [2**p for p in range(4, -1, -1)]:
            if n & b:
                y = int(cell_num / width)
                x = cell_num % width
                shaded[Point(y, x)] = True
            cell_num += 1

    return shaded


def load_puzzle(url: str) -> SymbolGrid:
    params = url.split('/')
    height = int(params[-2])
    width = int(params[-3])

    givens: PuzzleGivens = _parse_url(url)

    lattice = get_rectangle_lattice(height, width)
    sym = LoopSymbolSet(lattice)
    sym.append('EMPTY', ' ')
    qf_idl_solver = SolverFor('QF_IDL')
    sg = SymbolGrid(lattice, sym, solver=qf_idl_solver)
    lc = LoopConstrainer(sg, single_loop=True)

    set_loop_order_zero = False
    # Construct puzzle from URL
    for p in sg.lattice.points:
        if givens[p]:
            sg.solver.add(sg.cell_is(p, sym.EMPTY))
        else:
            sg.solver.add(Not(sg.cell_is(p, sym.EMPTY)))
            # Restrict loop order to an empty cell
            if not set_loop_order_zero:
                sg.solver.add(lc.loop_order_grid[p] == 0)
                set_loop_order_zero = True

    return sg
