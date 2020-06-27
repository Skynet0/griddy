from grilops import get_rectangle_lattice, SymbolSet
import grilops.loops

def rect_loop_symbols() -> SymbolSet:
    return grilops.loops.LoopSymbolSet(
        grilops.get_rectangle_lattice(1, 1))