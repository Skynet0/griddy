from remote_utils import get_puzzle_data
from puzzles.puzzle_base import Puzzle

sl = get_puzzle_data('https://puzz.link/p?mashu/5/5/109032090')

puzz = Puzzle([sl])

print("Solving url: https://puzz.link/p?mashu/5/5/109032090")
if puzz.sg.solve():
    puzz.sg.print()
else:
    print("No soln")