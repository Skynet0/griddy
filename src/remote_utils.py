import atexit
from io import BytesIO
from selenium import webdriver
from PIL import Image
from time import sleep

from puzzle_data import PuzzleData

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
chrome_options.add_argument('--verbose')
driver = webdriver.Chrome('resources/chromedriver.exe', options=chrome_options)

# Preload driver page for fast loading of puzzles later
driver.get("https://puzz.link")

JS_GET_PUZZLE_DATA = 'return ui.puzzle.getFileData(pzpr.parser.FILE_PZPR, {});'
JS_GET_PUZZLE_IMG = 'return ui.puzzle.toBuffer("png", 1, {});'

# Delay slightly for server-side to load JS
PAGE_LOAD_SLEEP = 0.05

# Cleanup
atexit.register(driver.quit)
atexit.register(driver.close)

def get_puzzle_data(url: str) -> PuzzleData:
    driver.get(url)
    sleep(PAGE_LOAD_SLEEP)
    lines = driver.execute_script(JS_GET_PUZZLE_DATA).strip().split('\n')

    return PuzzleData(
        genre=lines[1],
        width=int(lines[2]),
        height=int(lines[3]),
        payload=lines[4:]
    )

def get_puzzle_image(url: str, cellsize: int = 24) -> Image:
    driver.get(url)
    sleep(PAGE_LOAD_SLEEP)
    return Image.open(BytesIO(
        driver.execute_script(JS_GET_PUZZLE_IMG.format(cellsize))))
