import argparse
import sys
import time
from griddy.puzzles.genres import genres
from grilops.grids import SymbolGrid

parser = argparse.ArgumentParser(
    description='Solve a puzz.link or pzv.pr puzzle.')
parser.add_argument('url', type=str)
parser.add_argument('-t',
                    '--timeout',
                    dest='timeout',
                    type=int,
                    action='store',
                    default=30 * 1000)
parser.add_argument('--check_unique',
                    dest='check_unique',
                    action='store_const',
                    const=True,
                    default=False)


def main():
    args = parser.parse_args()
    g = args.url.split('/')[-4].split('?')[-1]

    if g not in genres.puzzle_genres:
        sys.exit(1)

    sg: SymbolGrid = genres.puzzle_genres[g].load_puzzle(args.url)
    sg.solver.set(timeout=args.timeout)

    start_time = time.process_time()
    solved = sg.solve()
    tot_time = time.process_time() - start_time

    if solved:
        sg.print()
        if args.check_unique:
            if sg.is_unique():
                print("Unique solution")
            else:
                print("Alternate solution")
    else:
        print("No solution")

    print("Total time: {}".format(tot_time))


if __name__ == "__main__":
    main()
