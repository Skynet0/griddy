from grilops import SymbolGrid, get_rectangle_lattice, SymbolSet
from grilops.geometry import Point
from grilops.regions import RegionConstrainer
import grilops.regions
import itertools
from typing import Callable, Optional, Tuple
from z3 import And, Implies, Int, Not, Or

from griddy.puzzles.common.puzzle_base import PuzzleGivens

GENRE_ALIASES = ['nurikabe']
QMARK = -2


def parse_url(url: str) -> PuzzleGivens:
    params = url.split('/')
    height = int(params[-2])
    width = int(params[-3])
    payload = params[-1]

    genre = params[-4].split('?')[-1]
    if genre not in GENRE_ALIASES:
        raise ValueError('Given URL is not a nurikabe')

    givens: PuzzleGivens = {}
    cell_num = 0

    def parse_char(payload: str, i: int) -> Tuple[int, int]:
        c = payload[i]
        if "0" <= c <= "9" or "a" <= c <= "f":
            return (int(c, 16), 1)
        elif c == "-":
            return (int(payload[i + 1:i + 3], 16), 3)
        elif c == "+":
            return (int(payload[i + 1:i + 4], 16), 4)
        elif c == "=":
            return (int(payload[i + 1:i + 4], 16) + 4096, 4)
        elif c == "%":
            return (int(payload[i + 1:i + 4], 16) + 8192, 4)
        elif c == ".":
            return (-2, 1)
        return (-1, 0)

    idx = 0
    while idx < len(payload) and cell_num < height * width:
        c = payload[idx]
        v, step = parse_char(payload, idx)
        if v != -1:
            y = int(cell_num / width)
            x = cell_num % width
            givens[Point(y, x)] = v
            idx += step
            cell_num += 1
        elif "g" <= c <= "z":
            cell_num += int(c, 36) - 15
            idx += 1
        else:
            idx += 1

    return givens


def load_puzzle(
        url: str) -> Tuple[SymbolGrid, Optional[Callable[[Point, int], str]]]:
    params = url.split('/')
    height = int(params[-2])
    width = int(params[-3])

    givens: PuzzleGivens = parse_url(url)

    lattice = get_rectangle_lattice(height, width)
    sym = SymbolSet([("B", chr(0x2588)), ("W", " ")])
    sg = SymbolGrid(lattice, sym)

    sea_size = None
    min_region_size = None
    max_region_size = None

    # No question marks, so we can compute and constrain sizes
    if QMARK not in givens.values():
        sea_size = height * width - sum(givens.values())
        min_region_size = min(sea_size, *givens.values())
        max_region_size = max(sea_size, *givens.values())

    rc = RegionConstrainer(lattice,
                           solver=sg.solver,
                           min_region_size=min_region_size,
                           max_region_size=max_region_size)

    # Make trivial deductions about shaded cells
    known_shaded = set()
    for p in givens:
        # 1's are surrounded by black squares
        if givens[p] == 1:
            for n in sg.lattice.edge_sharing_points(p):
                if n in sg.grid:
                    sg.solver.add(sg.cell_is(n, sym.B))
                    known_shaded.add(n)
        else:
            # Check two-step lateral offsets
            for _, d in sg.lattice.edge_sharing_directions():
                n = p.translate(d)
                if n.translate(d) in givens:
                    sg.solver.add(sg.cell_is(n, sym.B))
                    known_shaded.add(n)
            # Check two-step diagonal offsets
            for (_, di), (_, dj) in itertools.combinations(
                    sg.lattice.edge_sharing_directions(), 2):
                dn = p.translate(di).translate(dj)
                if dn != p and dn in givens:
                    n1, n2 = p.translate(di), p.translate(dj)
                    sg.solver.add(sg.cell_is(n1, sym.B))
                    sg.solver.add(sg.cell_is(n2, sym.B))
                    known_shaded.update((n1, n2))

    # TODO: Conduct a few more trivial deductions, within reason.
    # Basic reachability (search) is a good one

    # If we found a cell that must be shaded, root the sea to reduce
    # the search space
    sea_root = None
    if len(known_shaded) >= 1:
        p = known_shaded.pop()
        sg.solver.add(rc.parent_grid[p] == grilops.regions.R)
        sg.solver.add(rc.region_size_grid[p] == height * width -
                      sum(givens.values()))
        sea_root = p

    # # Constrain the sea
    sea_id = Int("sea-id")
    island_ids = [sg.lattice.point_to_index(p) for p in givens]
    if sea_root:
        sg.solver.add(sea_id == sg.lattice.point_to_index(sea_root))
    else:
        sg.solver.add(sea_id >= 0)
        sg.solver.add(sea_id < height * width)

    for p in sg.lattice.points:
        if p in givens:
            # Given cells are unshaded by definition
            sg.solver.add(sg.cell_is(p, sym.W))

            # Constrain given to be root of island tree to reduce possibilities
            sg.solver.add(rc.parent_grid[p] == grilops.regions.R)
            sg.solver.add(rc.region_id_grid[p] == sg.lattice.point_to_index(p))

            if not sea_root:
                sg.solver.add(sea_id != sg.lattice.point_to_index(p))
            if givens[p] != QMARK:
                sg.solver.add(rc.region_size_grid[p] == givens[p])

        else:
            # If we placed a sea root, then all regions are accounted for, so
            # and cell that is not a given and not the sea root is not a root.
            if sea_root:
                if p != sea_root:
                    sg.solver.add(rc.parent_grid[p] != grilops.regions.R)
            else:
                # No shaded cells known, so ust say that non given white cells
                # can't be region roots
                sg.solver.add(
                    Implies(sg.cell_is(p, sym.W),
                            rc.parent_grid[p] != grilops.regions.R))

            # Iff a cell is white, it is an island
            sg.solver.add(
                    sg.cell_is(p, sym.W) ==
                    Or(*[rc.region_id_grid[p] == iid for iid in island_ids]))

            # Iff a cell is shaded, it is part of the sea
            sg.solver.add(
                sg.cell_is(p, sym.B) == (rc.region_id_grid[p] == sea_id))

            if sea_size is not None:
                sg.solver.add(
                    Implies(sg.cell_is(p, sym.B),
                            rc.region_size_grid[p] == sea_size))

        # Iff two adjacent cells have the same color, they are part of the same
        # region
        adjacent_cells = [n.symbol for n in sg.edge_sharing_neighbors(p)]
        adjacent_region_ids = [
            n.symbol
            for n in sg.lattice.edge_sharing_neighbors(rc.region_id_grid, p)
        ]
        for cell, region_id in zip(adjacent_cells, adjacent_region_ids):
            sg.solver.add(
                (sg.grid[p] == cell) == (rc.region_id_grid[p] == region_id))

    # The sea cannot contain 2x2 shaded
    for sy in range(height - 1):
        for sx in range(width - 1):
            pool_cells = [
                sg.grid[Point(y, x)]
                for y in range(sy, sy + 2)
                for x in range(sx, sx + 2)
            ]
            sg.solver.add(Not(And(*[cell == sym.B for cell in pool_cells])))

    def print_fn(p: Point, i: int) -> str:
        if p in givens:
            if givens[p] == QMARK:
                return "?"
            return str(givens[p])
        return None

    return sg, print_fn
