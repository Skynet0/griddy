from remote_utils import get_puzzle_data
from puzzles.puzzle_base import Puzzle

sl = get_puzzle_data('https://puzz.link/p?simpleloop/12/12/02000984b880g110o2g0g2id000gg')

puzz = Puzzle([sl])

print("Solving")
if puzz.sg.solve():
    puzz.sg.print()
else:
    print("No soln")