# constants.py, place to put the game constants

import pygame
pygame.init()

#   ______   ______    __        ______   .______          _______.
#  /      | /  __  \  |  |      /  __  \  |   _  \        /       |
# |  ,----'|  |  |  | |  |     |  |  |  | |  |_)  |      |   (----`
# |  |     |  |  |  | |  |     |  |  |  | |      /        \   \
# |  `----.|  `--'  | |  `----.|  `--'  | |  |\  \----.----)   |
#  \______| \______/  |_______| \______/  | _| `._____|_______/

# Color definitions
COLOR_BLACK = (0, 0, 0)  # RGB for black
COLOR_WHITE = (255, 255, 255)  # RGB for white
COLOR_GREY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_OCEAN = (7, 205, 205)
COLOR_PURPLE = (184,157,207)
COLOR_LIGHT_GREY = (226, 224, 215)


# Game colors
COLOR_DEFAULT_BG = COLOR_OCEAN


#   _______      ___      .___  ___.  _______    .______      ___      .______          ___      .___  ___.
#  /  _____|    /   \     |   \/   | |   ____|   |   _  \    /   \     |   _  \        /   \     |   \/   |
# |  |  __     /  ^  \    |  \  /  | |  |__      |  |_)  |  /  ^  \    |  |_)  |      /  ^  \    |  \  /  |
# |  | |_ |   /  /_\  \   |  |\/|  | |   __|     |   ___/  /  /_\  \   |      /      /  /_\  \   |  |\/|  |
# |  |__| |  /  _____  \  |  |  |  | |  |____    |  |     /  _____  \  |  |\  \----./  _____  \  |  |  |  |
#  \______| /__/     \__\ |__|  |__| |_______|   | _|    /__/     \__\ | _| `._____/__/     \__\ |__|  |__|


# Game sizes
GAME_WIDTH = 2000
GAME_HEIGHT = 2000
CELL_WIDTH = 128
CELL_HEIGHT = 128
HEX_SIZE = 128
EDGE_OFFSET = 128 # To move the map generatation away from the edge

#MAP VARS
MAP_WIDTH = 8
MAP_HEIGHT = 8

# FPS LIMIT
GAME_FPS = 10

# --- Main dictionary to determine movement direction
directions = ['NE', 'E', 'SE', 'SW', 'W', 'NW', 'SPACE']
MOVEMENT_DIR = {}
for dir in directions:
    MOVEMENT_DIR[dir] = {}
    MOVEMENT_DIR[dir]['EVEN'] = []
    MOVEMENT_DIR[dir]['ODD'] = []

MOVEMENT_DIR['NE']['EVEN'] = [0,-1]
MOVEMENT_DIR['NE']['ODD'] = [1,-1]
MOVEMENT_DIR['E']['EVEN'] = [1,0]
MOVEMENT_DIR['E']['ODD'] = [1,0]
MOVEMENT_DIR['SE']['EVEN'] = [0,1]
MOVEMENT_DIR['SE']['ODD'] = [1,1]
MOVEMENT_DIR['SW']['EVEN'] = [-1,1]
MOVEMENT_DIR['SW']['ODD'] = [0,1]
MOVEMENT_DIR['W']['EVEN'] = [-1,0]
MOVEMENT_DIR['W']['ODD'] = [-1,0]
MOVEMENT_DIR['NW']['EVEN'] = [-1,-1]
MOVEMENT_DIR['NW']['ODD'] = [0,-1]
MOVEMENT_DIR['SPACE']['EVEN'] = [0,0]
MOVEMENT_DIR['SPACE']['ODD'] = [0,0]

# --- List of possible actions the multiple units, to be used as the action (aka a number to call them) for the AI
MOVEMENT_ONE_UNIT = []
for dir in directions:
    MOVEMENT_ONE_UNIT.append(dir)

MOVEMENT_TWO_UNITS = []
for dir in directions:
    for dir2 in directions:
        MOVEMENT_TWO_UNITS.append([dir, dir2])

MOVEMENT_THREE_UNITS = []
for dir in directions:
    for dir2 in directions:
        for dir3 in directions:
            MOVEMENT_THREE_UNITS.append([dir, dir2, dir3])


NEIGHBORING_TILES = [(1,0), (1,-1), (0,-1), (-1,0), (1,1), (0,1)]

#  ____             _ _
# / ___| _ __  _ __(_) |_ ___  ___
# \___ \| '_ \| '__| | __/ _ \/ __|
#  ___) | |_) | |  | | ||  __/\__ \
# |____/| .__/|_|  |_|\__\___||___/
#       |_|

#character
S_PLAYER = pygame.transform.scale(pygame.image.load('data/Otter_Warrior.png'), (CELL_WIDTH, CELL_HEIGHT))
S_CITY = pygame.transform.scale(pygame.image.load('data/Ottertopia.png'), (CELL_WIDTH, CELL_HEIGHT))
S_PLAINS = pygame.transform.scale(pygame.image.load('data/plains.png'), (HEX_SIZE, HEX_SIZE))


# Fonts
FONT_DEBUG_MESSAGE = pygame.font.SysFont('georgia', 32, bold=True)
FONT_BIG = pygame.font.SysFont('georgia', 40, bold=True)
OUTLINE_SIZE = 3

# start locations
LOC_CITY = (4,4)
#LOC_SPRITE_1 = (0,1)
#LOC_SPRITE_2 = (1,6)
#LOC_SPRITE_3 = (6,1)

# --- Start with a random start location
HEX_LOCATIONS = []
for ii in range(0, MAP_WIDTH):
    for jj in range(0, MAP_HEIGHT):
        if ii != LOC_CITY[0] or jj != LOC_CITY[1]:
            HEX_LOCATIONS.append([ii,jj])