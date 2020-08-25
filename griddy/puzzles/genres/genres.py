from griddy.puzzles.genres import masyu, simpleloop, nurikabe

_puzzle_genre_modules = [masyu, simpleloop, nurikabe]

puzzle_genres = {}

for genre in _puzzle_genre_modules:
    for alias in genre.GENRE_ALIASES:
        puzzle_genres[alias] = genre
