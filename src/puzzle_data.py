import atexit
from collections import namedtuple
from dataclasses import dataclass
from selenium import webdriver
from typing import List, Text


chrome_options = webdriver.ChromeOptions()
# Don't start browser
chrome_options.add_argument('--headless')
# TODO - determine actually helpful arguments
# TODO - potentially move to HTMLUnit
# Remove load
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-sync')
chrome_options.add_argument('--disable-logging')
driver = webdriver.Chrome('resources/chromedriver.exe', options=chrome_options)

# Preload driver page for fast loading of puzzles later
driver.get("https://puzz.link")

JS_GET_PUZZLE_DATA = 'return ui.puzzle.getFileData(pzpr.parser.FILE_PZPR, {});'

atexit.register(driver.close)

@dataclass
class PuzzleData:
    genre: str
    width: int
    height: int
    data: List[str]


def get_puzzle_data(url: str):
    driver.get(url)
    lines = driver.execute_script(JS_GET_PUZZLE_DATA).strip().split('\n')

    return PuzzleData(
        genre=lines[1],
        width=int(lines[2]),
        height=int(lines[3]),
        data=lines[4:]
    )
