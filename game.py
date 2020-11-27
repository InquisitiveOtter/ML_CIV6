# game.py
# Main game file. This file contains





import pygame
import constants
import random
import numpy as np
import class_hex


# ------------------------------
# Base class
# ------------------------------

class C_Sprite(pygame.sprite.Sprite):
    """
    Creatures have health and can damage other objects by attacking them.
    Can also die.
    """

    def __init__(self,
                 x,
                 y,
                 sprite,
                 name_instance,
                 hp=10,
                 hp_max = 100,
                 strength=20):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.name_instance = name_instance
        self.hp_max = hp_max
        self.hp = hp
        self.strength = strength
        self.alive = True
        self.status = 'alive'
        self.status_default = 'alive'

    def draw(self):
        """Draw the unit"""

        global GAME_MAP

        SURFACE_MAIN.blit(self.sprite,
                          (GAME_MAP.grid[(int(self.x), int(self.y))].rect.x,
                          GAME_MAP.grid[(int(self.x), int(self.y))].rect.y - GAME_MAP.grid[(int(self.x), int(self.y))].rect.h / 4))



class C_Unit(C_Sprite):
    def __init__(self,
                 x,
                 y,
                 sprite,
                 name_instance,
                 hp=100,
                 hp_max=100,
                 strength=20):
        super().__init__(x,
                         y,
                         sprite,
                         name_instance,
                         hp,
                         hp_max,
                         strength)

    def move(self,
             dx,
             dy):

        # --- Check to see if the units is still alive!!!!
        if self.alive:
            # Check to see if the movement is still "in bounds"
            if (int(self.x + dx), int(self.y + dy)) not in GAME_MAP.grid:
                tile_is_wall = True
            else:
                tile_is_wall = False


            # --- set unit status to 'hit wall' if it hit the wall
            if tile_is_wall:
                self.status = 'hit wall'

            target = map_check_for_creatures(self.x + dx,
                                             self.y + dy,
                                             exclude_object=self)


            if target and target.__class__ != C_Unit:
                damage_output, damage_taken = attack(self, target)
                #print('taken {}, output {}'.format(damage_taken, damage_output))

                # Take the damage
                if damage_taken > 0:
                    #print('damage_taken', damage_taken)
                    self.take_damage(damage_taken)

                # Have the other object take damage
                if damage_output > 0:
                    target.take_damage(damage_output, self.alive)
                    self.status = 'attacked'

            # --- Heal the unit if it doesn't move
            if dx == 0 and dy == 0:
                self.hp += 10
                self.status = 'healed'
                if self.hp > self.hp_max:
                    self.hp = self.hp_max
                    self.status = self.status_default

            # --- Move the unit if it can
            if not tile_is_wall and target is None:
                self.x += dx
                self.y += dy

    def take_damage(self,
                    damage,
                    aggressor_alive = True):
        # Unit doesn't die if the unit doesn't have enough HP to take it over
        if not aggressor_alive and (self.hp - damage) < 0:
            self.hp = 1
        else:
            self.hp -= damage
        #self.status = 'took damage'


        # --- Unit dies if less than 0 health
        if self.hp <= 0:
            self.death_unit()

    def death_unit(self):
        '''On death, most citys stop moving.'''
        #print(self.name_instance + ' is dead!')
        self.alive = False
        self.status = 'dead'


class C_City(C_Sprite):
    def __init__(self,
                 x,
                 y,
                 sprite,
                 name_instance,
                 hp=1,
                 hp_max=100,
                 wall_hp=100,
                 strength=18,
                 strength_ranged=0,
                 ranged_combat=False,
                 heal=False):
        self.wall_hp = wall_hp
        self.strength_ranged = strength_ranged
        self.ranged_combat = ranged_combat
        self.heal = heal

        super().__init__(x,
                         y,
                         sprite,
                         name_instance,
                         hp,
                         hp_max,
                         strength)

    def take_turn(self):

        global GAME_OBJECTS, GAME_MAP

        if self.ranged_combat:
            # Check for a creature that is within two tiles
            items_within_range = []
            for ii in range(-2, 2):
                for jj in range(-2, 2):
                    temp = map_check_for_creatures(self.x - ii, self.y - jj, exclude_object=self)
                    # print('checked location', self.x - ii, self.y - jj)
                    if temp:
                        # print(temp.__class__, ' within range')
                        if temp.__class__ == C_Unit:
                            # --- Only add alive units
                            if temp.alive:
                                #print('found {} at {} {}'.format(
                                #    temp.name_instance,
                                #    self.x - ii,
                                #    self.y - jj))
                                items_within_range.append(temp)

            # --- Attack a random creature
            if len(items_within_range) > 0:
                rand_numb = random.randint(0, len(items_within_range) - 1)
                damage_output, damage_taken = attack(self, items_within_range[rand_numb], ranged=True)

                # City should not take any damage for the ranged combat
                items_within_range[rand_numb].take_damage(damage_output)

        if self.heal:
            temp = GAME_MAP.grid[(self.x, self.y)].get_neighbors(GAME_MAP.grid)
            tiles_within_range = []
            for ii in range(len(temp)):
                tiles_within_range.append(temp[ii].index)
            # Check to make sure there are three creatures within one tile
            items_within_range = []
            for obj in GAME_OBJECTS:
                for tile in tiles_within_range:
                    if obj.x == tile[0] and obj.y == tile[1] and obj.alive:
                        #print(f'position {obj.x} {obj.y} {obj.name_instance}')
                        items_within_range.append(temp)


            # --- Heal if less than 3 tiles are occupied
            if len(items_within_range) < 3:
                self.hp += 10
                self.status = 'healed'
                if self.hp > self.hp_max:
                    self.hp = self.hp_max
            else:
                pass
                #print(f'Three units are surrounding the city')


    def take_damage(self,
                    damage,
                    aggressor_alive = True):
        # City doesn't die if the unit doesn't have enough HP to take it over
        if not aggressor_alive and (self.hp - damage) < 0:
            self.hp = 1
        else:
            self.hp -= damage
        self.status = 'took damage'

        # --- City dies when it doesn't have HP
        if self.hp <= 0:
            self.hp = 0
            self.death()

    def death(self):
        '''On death, most citys stop moving.'''
        #print(self.name_instance + ' has been defeated!')
        self.alive = False
        self.status = 'dead'


def attack(aggressor,
           target,
           ranged=False):
    '''Base attack definition using the formula found on CivFanatics
    TODO: Attack accounting for walls....'''

    if ranged:
        strength_diff = aggressor.strength_ranged - target.strength
    else:
        strength_diff = aggressor.strength - target.strength

    damage_out = np.round(random.randint(24, 36) * np.exp(strength_diff / 25.0) * (random.randint(75, 100) / 100.0))
    damage_taken = np.round(random.randint(24, 36) * np.exp(-strength_diff / 25.0) * (random.randint(75, 100) / 100.0))

    return damage_out, damage_taken


# ---------------------------------------------
# MAP
# ---------------------------------------------
def map_create():

    new_map = class_hex.HexMap(constants.MAP_HEIGHT,
                                constants.MAP_WIDTH,
                               (constants.HEX_SIZE, constants.HEX_SIZE),
                                constants.EDGE_OFFSET)
    # TODO: block the edge tiles!


    return new_map


def map_check_for_creatures(x,
                            y,
                            exclude_object=None):
    target = None

    # --- check objectlist to find creature at that location that isn't excluded
    if exclude_object:
        for object in GAME_OBJECTS:
            if (object is not exclude_object and
                    object.x == x and
                    object.y == y and
                    object.alive):
                target = object

            if target:
                return target

    # --- check objectlist to find any creature at that location
    else:
        for object in GAME_OBJECTS:
            if (object.x == x and
                    object.y == y and
                    object.alive):
                target = object

            if target:
                return target


# ---------------------------------------------
# DRAWING
# ---------------------------------------------
def draw_game():
    global SURFACE_MAIN, episode_number, TURN_NUMBER

    # --- Clear the surface
    SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)

    # --- Draw the map
    draw_map(GAME_MAP)

    # --- Draw the objects
    for obj in GAME_OBJECTS:
        obj.draw()

    # --- Draw the text
    for obj in GAME_OBJECTS:
        # Draw the HP above the unit
        draw_text(SURFACE_MAIN, "{:.0f}/{:.0f}".format(obj.hp, obj.hp_max),
                  (GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.x + GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.width / 2,
                   GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.y - GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.h*2/7),
                  constants.COLOR_RED, outline=True)

        # Draw the units name
        draw_text(SURFACE_MAIN, obj.name_instance,
                  (GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.x + GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.width / 2,
                   GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.y + GAME_MAP.grid[(int(obj.x), int(obj.y))].rect.h*4/5),
                  constants.COLOR_PURPLE, outline=True)


    # Draw the episode number
    if False:
        draw_text(SURFACE_MAIN, f'Episode: {episode_number}',
                  (constants.EDGE_OFFSET,
                   constants.HEX_SIZE * constants.MAP_HEIGHT - constants.EDGE_OFFSET + constants.HEX_SIZE / 2),
                   constants.COLOR_LIGHT_GREY, outline=True, center=False, font_big = True)

    # Draw the episode number
    draw_text(SURFACE_MAIN, f'Turn: {TURN_NUMBER}',
              (constants.EDGE_OFFSET,
               constants.HEX_SIZE * constants.MAP_HEIGHT - constants.EDGE_OFFSET + constants.HEX_SIZE / 7),
              constants.COLOR_LIGHT_GREY, outline=True, center=False, font_big = True)

    # --- Update game display
    pygame.display.flip()


def draw_map(map_to_draw):

    for loc in GAME_MAP.grid:
        if SURFACE_MAIN is not None:
            SURFACE_MAIN.blit(GAME_MAP.grid[loc].image, (GAME_MAP.grid[loc].rect.x, GAME_MAP.grid[loc].rect.y))
            #SURFACE_MAIN.blit(GAME_MAP.grid[loc].image_outline, (GAME_MAP.grid[loc].rect.x, GAME_MAP.grid[loc].rect.y))

            # Draw the distance between the city and the location on the map,
            if False:
                draw_text(SURFACE_MAIN, f'{hex_distance(loc, [3,3])}',
                      (GAME_MAP.grid[loc].rect.x + int(constants.HEX_SIZE / 2),
                       GAME_MAP.grid[loc].rect.y + int(constants.HEX_SIZE / 2)),
                      constants.COLOR_BLACK)

            # Draw the map location on the tile #f'{loc[0] - 3},{loc[1] - 3}, {-(loc[0]-3) -(loc[1]-3)}',
            if False:
                draw_text(SURFACE_MAIN, f'{loc[0]}, {loc[1]}',
                      (GAME_MAP.grid[loc].rect.x + int(constants.HEX_SIZE / 2),
                       GAME_MAP.grid[loc].rect.y + int(constants.HEX_SIZE / 2)),
                      constants.COLOR_BLACK)

def draw_text(display_surface, text_to_display, T_coordinates, text_color, outline = False, center = True, font_big = False):
    """Definition takes in text and displays the text to the screen"""
    # Outline feature from sloth at: https://stackoverflow.com/questions/54363047/how-to-draw-outline-on-the-fontpygame
    _circle_cache = {}

    def _circlepoints(r):
        r = int(round(r))
        if r in _circle_cache:
            return _circle_cache[r]
        x, y, e = r, 0, 1 - r
        _circle_cache[r] = points = []
        while x >= y:
            points.append((x, y))
            y += 1
            if e < 0:
                e += 2 * y - 1
            else:
                x -= 1
                e += 2 * (y - x) - 1
        points += [(y, x) for x, y in points if x > y]
        points += [(-x, y) for x, y in points if x]
        points += [(x, -y) for x, y in points if y]
        points.sort()
        return points

    # --- Create an outline around the name text so you can read it!
    if outline:
        text_surf, text_rect = helper_text_objects(text_to_display, text_color, font_big=font_big)
        text_surf.convert_alpha()
        if center:
            text_rect.center = T_coordinates
        else:
            text_rect.topleft = T_coordinates
        w = text_surf.get_width() + 2 * constants.OUTLINE_SIZE
        h = text_surf.get_height()
        osurf = pygame.Surface((w, h + 2 * constants.OUTLINE_SIZE)).convert_alpha()
        osurf.fill((0, 0, 0, 0))

        surf = osurf.copy()
        outline_surf, outline_rect = helper_text_objects(text_to_display, constants.COLOR_BLACK, font_big=font_big)
        if center:
            outline_rect.center = T_coordinates
        else:
            outline_rect.topleft = T_coordinates
        osurf.blit(outline_surf.convert_alpha(), (0,0))

        for dx, dy in _circlepoints(constants.OUTLINE_SIZE):
            surf.blit(osurf, (dx + constants.OUTLINE_SIZE, dy + constants.OUTLINE_SIZE))

        surf.blit(text_surf, (constants.OUTLINE_SIZE, constants.OUTLINE_SIZE))
        display_surface.blit(surf, outline_rect)

    else:
        text_surf, text_rect = helper_text_objects(text_to_display, text_color, font_big=font_big)
        text_surf.convert_alpha()
        text_rect.center = T_coordinates
        display_surface.blit(text_surf, text_rect)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
#
# Helper objects
#
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def helper_text_objects(incoming_text,
                        incoming_color,
                        font_big = False):
    if font_big:
        Text_surface = constants.FONT_BIG.render(incoming_text, True, incoming_color)
    else:
        Text_surface = constants.FONT_DEBUG_MESSAGE.render(incoming_text, True, incoming_color)

    return Text_surface, Text_surface.get_rect()

def hex_coords(obj1):
    """This definition will find out how far obj1 is from obj2, using the axial coordinte system"""
    obj1_cube = []
    if obj1[1] % 2 == 0:
        obj1_cube.append(obj1[0] - obj1[1] / 2)
    else:
        obj1_cube.append(obj1[0] - (obj1[1] - 1) / 2)
    obj1_cube.append(-obj1_cube[0] - obj1[1])
    obj1_cube.append(obj1[1])
    return obj1_cube

def hex_distance(obj1, obj2):
    """This definition will find out how hard obj1 is from obj2"""

    obj1_coords = hex_coords(obj1)
    obj2_coords = hex_coords(obj2)

    return max([abs(obj1_coords[0] - obj2_coords[0]),
                abs(obj1_coords[1] - obj2_coords[1]),
                abs(obj1_coords[2] - obj2_coords[2])])

#   _______      ___      .___  ___.  _______
#  /  _____|    /   \     |   \/   | |   ____|
# |  |  __     /  ^  \    |  \  /  | |  |__
# |  | |_ |   /  /_\  \   |  |\/|  | |   __|
# |  |__| |  /  _____  \  |  |  |  | |  |____
#  \______| /__/     \__\ |__|  |__| |_______|
class Game():
    def __init__(self,
                 human=False,
                 ml_ai=False,
                 render = False):
        self.human = human
        self.ml_ai = ml_ai
        self.quit = False
        self.render = render

        global GAME_OBJECTS

        # initialize pygame
        if self.render or self.human:
            pygame.init()

    def game_main_loop(self,
                       action=0):
        """In this function we loop the main game."""
        game_quit = False

        # --- player action definition
        player_action = 'no-action'

        while not game_quit:

            # --- handle player input
            if self.human:
                player_action = self.game_handle_keys_human(GAME_OBJECTS[0])

            if player_action == 'QUIT':
                game_quit = True


            # --- draw the game
            if self.render:
                draw_game()

            #CLOCK.tick(constants.GAME_FPS)

        if self.render:
            pygame.quit()

        exit()

    def step(self,
             action=0):
        """In this function we take a step in the main game."""


        global GAME_OBJECTS, TURN_NUMBER

        TURN_NUMBER += 1

        # --- draw the game
        if self.render:
            draw_game()

        # --- player action definition
        player_action = 'no-action'
        game_quit = False
        reward = 0

        # --- Check for the city location, there has to be a better way...
        # maybe have the city not under GAME_OBJECTS?
        for obj in enumerate(GAME_OBJECTS):
            if obj[1].__class__ == C_City:
                city_loc = obj[0]

        # --- Human loop to control only one unit
        if self.human and not game_quit:
            # --- Loop over each object to take the turn
            for obj in GAME_OBJECTS:
                if obj.__class__ == C_Unit:
                    if obj.status != 'dead':
                        if self.human and not game_quit:
                            waiting_for_input = True
                            while waiting_for_input:
                                # --- handle player input
                                player_action = self.game_handle_keys_human(obj)
                                if player_action == 'player-moved':
                                    waiting_for_input = False

                                if player_action == 'QUIT':
                                    game_quit = True
                                    waiting_for_input = False
                            if self.render:
                                draw_game()

                        # --- Get rewards after each turn, to account for attacking the city each turn
                        reward += self.get_rewards()

                        # --- Check to see if the city is dead or not
                        if GAME_OBJECTS[city_loc].hp <= 0:
                            game_quit = True
                            break


        elif self.ml_ai and not game_quit:
            # --- First perform actions by the units
            player_action = self.game_handle_moves_ml_ai(action)

            if self.render:
                draw_game()

            # --- Check to see if the city is dead or not
            if GAME_OBJECTS[city_loc].hp <= 0:
                game_quit = True


        if player_action == 'QUIT':
            game_quit = True

        # City takes a turn once the HUMAN or ML_AI moves
        elif player_action != 'no-action':
            for obj in GAME_OBJECTS:
                if obj.__class__ == C_City:
                    obj.take_turn()

        # --- Get rewards after the city attacks, in case a unit dies
        reward += self.get_rewards()

        # --- Subtract 1 for the turn penalty
        reward -= 1

        #CLOCK.tick(constants.GAME_FPS)

        return self.get_observation(), reward, game_quit

    def get_rewards(self):
        '''This definition will return the reward status for each step as
        well as the location of the city relative to the units'''
        global GAME_OBJECTS

        reward = 0

        # --- Find the city location in GAME_OBJECTS
        for obj in enumerate(GAME_OBJECTS):
            if obj[1].__class__ == C_City:
                city_loc = obj[0]
                if obj[1].status == 'dead':
                    reward += 3
                    obj[1].status = None
                elif obj[1].status == 'took damage':
                    reward += 0.5
                    obj[1].status = obj[1].status_default
                elif obj[1].status == 'healed':
                    reward -= 0.3
                    obj[1].status = obj[1].status_default


        # --- REWARDS for unit specific actions
        for obj in GAME_OBJECTS:
            if obj.__class__ == C_Unit:
                #print('BEFORE: {} status of {}'.format(obj.name_instance, obj.status))
                if obj.status == 'dead':
                    reward -= 10
                    obj.status = None
                elif obj.status == 'took damage':
                    reward += 0
                    obj.status = obj.status_default
                elif obj.status == 'hit wall':
                    reward -= 1
                    obj.status = obj.status_default
                elif obj.status == 'healed':
                    reward += 0.1
                    obj.status = obj.status_default
                elif obj.status == 'attacked':
                    reward += 0.2
                    obj.status = obj.status_default


                # --- Rewards for how far they are away from the city!
                # - This is a linear reward, 0 for being next to city, -0.5 for maximum distance, per unit
                dist = hex_distance([obj.x, obj.y], [GAME_OBJECTS[city_loc].x,GAME_OBJECTS[city_loc].y])
                dist_reward = float(dist - 1) / (max([constants.MAP_HEIGHT, constants.MAP_WIDTH]) - 2)
                reward -= dist_reward / 0.5


        return reward

    def get_observation(self):
        '''Definition returns the known universe
        positions of each unit and each city
        TODO:
        1) current health of each unit/city
        2) current strength of each unit/city
        '''

        global GAME_OBJECTS

        # --- Find the distance between the unit and the city
        loc = -1 # position around the city -1 if not by, 0/8, 1/8, ..., 8/8 otherwise
        city_loc = -1

        observation = [] # city health, dx unit 1, dy unit 1, hp_norm unit 1, dx unit 2, dy unit 2, hp_nomr unit 2, ...

        # --- Find the city location in GAME_OBJECTS
        for obj in enumerate(GAME_OBJECTS):
            if obj[1].__class__ == C_City:
                city_loc = obj[0]
                observation.append(obj[1].hp / obj[1].hp_max)

        # --- Find the space between each unit and the city
        for obj in GAME_OBJECTS:
            if obj.__class__ == C_Unit:
                dx_norm = (GAME_OBJECTS[city_loc].x - obj.x) / constants.MAP_WIDTH
                dy_norm = (GAME_OBJECTS[city_loc].y - obj.y) / constants.MAP_HEIGHT
                observation.append(dx_norm)
                observation.append(dy_norm)

                # --- Find the positional location around the city, not implimented!
                if np.abs(GAME_OBJECTS[city_loc].x - obj.x) <= 1 and False:

                    if GAME_OBJECTS[city_loc].x - obj.x > 0:
                        if GAME_OBJECTS[city_loc].y - obj.y > 0: loc = 1
                        if GAME_OBJECTS[city_loc].y - obj.y == 0: loc = 8
                        if GAME_OBJECTS[city_loc].y - obj.y < 0: loc = 7

                    if GAME_OBJECTS[city_loc].x - obj.x == 0:
                        if GAME_OBJECTS[city_loc].y - obj.y > 0: loc = 2
                        if GAME_OBJECTS[city_loc].y - obj.y == 0: loc = 91
                        if GAME_OBJECTS[city_loc].y - obj.y < 0: loc = 6

                    if GAME_OBJECTS[city_loc].x - obj.x < 0:
                        if GAME_OBJECTS[city_loc].y - obj.y > 0: loc = 3
                        if GAME_OBJECTS[city_loc].y - obj.y == 0: loc = 4
                        if GAME_OBJECTS[city_loc].y - obj.y < 0: loc = 5
                    if loc != -1:
                        loc /= 8

                # --- Normalized HP
                observation.append(obj.hp / obj.hp_max)

        return np.array(observation)

    def get_current_state(self):
        """Use this to get unit position as well as health, used for rendering in Blender"""
        global GAME_OBJECTS
        temp_data = {}
        for obj in GAME_OBJECTS:
            temp_data[obj.name_instance] = {}
            temp_data[obj.name_instance]['health'] = obj.hp
            temp_data[obj.name_instance]['position'] = [obj.x, obj.y]

        return temp_data


    def game_initialize(self,
                        ep_number = 0):
        """This function initializes the main window, and pygame"""

        global SURFACE_MAIN, GAME_MAP, PLAYER, ENEMY, GAME_OBJECTS, episode_number, TURN_NUMBER#, CLOCK
        #self.episode_number = episode_number

        episode_number = ep_number
        TURN_NUMBER = 0
        #CLOCK = pygame.time.Clock()

        # --- Set sufrace dimensions
        if self.render:
            SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH
                                                    * constants.HEX_SIZE
                                                    + int(constants.HEX_SIZE / 2)
                                                    + constants.EDGE_OFFSET * 2,
                                                    (constants.MAP_HEIGHT
                                                     * constants.HEX_SIZE)
                                                    - (int(constants.MAP_HEIGHT / 2)
                                                       * int(constants.HEX_SIZE / 2))
                                                    + int(constants.HEX_SIZE / 4)
                                                    + constants.EDGE_OFFSET * 2))#, pygame.FULLSCREEN)
            #SURFACE_MAIN = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
        else:
            SURFACE_MAIN = None

        # --- Create the game map. Fills the dictionary with values for each tile
        GAME_MAP = map_create()

        SPRITE_LOCATIONS = random.sample(constants.HEX_LOCATIONS, 3)

        PLAYER = C_Unit(SPRITE_LOCATIONS[0][0],
                        SPRITE_LOCATIONS[0][1],
                        constants.S_PLAYER,
                        "Otto",
                        strength=20,
                        hp=100,
                        hp_max=100)

        PLAYER2 = C_Unit(SPRITE_LOCATIONS[1][0],
                        SPRITE_LOCATIONS[1][1],
                        constants.S_PLAYER,
                        "Fynn",
                        strength=20,
                        hp=100,
                        hp_max=100)

        PLAYER3 = C_Unit(SPRITE_LOCATIONS[2][0],
                        SPRITE_LOCATIONS[2][1],
                        constants.S_PLAYER,
                        "Victor",
                        strength=20,
                        hp=100,
                        hp_max=100)

        CITY = C_City(constants.LOC_CITY[0],
                      constants.LOC_CITY[1],
                      constants.S_CITY,
                      "Ottertopia",
                      hp=100,
                      strength=28,
                      ranged_combat=False,
                      heal=True)

        # Must have units first then the city last!!!
        GAME_OBJECTS = [PLAYER, PLAYER2, PLAYER3, CITY]


    def game_handle_keys_human(self,
                               object):

        # --- check to see if the y coordinate is even or odd
        if object.y % 2 == 0:
            parity = 'EVEN'
            even = True
        else:
            parity = 'ODD'
            even = False

        # get player input
        events_list = pygame.event.get()

        # process input
        for event in events_list:  # loop through all events that have happened
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 'QUIT'

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    object.move(constants.MOVEMENT_DIR['NW'][parity][0], constants.MOVEMENT_DIR['NW'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_a:
                    object.move(constants.MOVEMENT_DIR['W'][parity][0], constants.MOVEMENT_DIR['W'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_z:
                    object.move(constants.MOVEMENT_DIR['SW'][parity][0], constants.MOVEMENT_DIR['SW'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_e:
                    object.move(constants.MOVEMENT_DIR['NE'][parity][0], constants.MOVEMENT_DIR['NE'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_d:
                    object.move(constants.MOVEMENT_DIR['E'][parity][0], constants.MOVEMENT_DIR['E'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_x:
                    object.move(constants.MOVEMENT_DIR['SE'][parity][0], constants.MOVEMENT_DIR['SE'][parity][1])
                    return "player-moved"

                if event.key == pygame.K_SPACE:
                    if object.hp < PLAYER.hp_max:
                        object.hp += 10
                        if object.hp > object.hp_max:
                            object.hp = object.hp_max
                        object.status = 'healed'
                    return "player-moved"

        return 'no-action'

    def game_handle_moves_ml_ai(self,
                                action):

        global GAME_OBJECTS

        # --- determine the number of units on the battlefield
        if len(GAME_OBJECTS) - 1 == 1:
            print('in one')
            # --- Determine the parity
            if GAME_OBJECTS[0].y % 2 == 0:
                parity = 'EVEN'
            else:
                parity = 'ODD'

            # --- Make a movement
            direction = constants.MOVEMENT_ONE_UNIT[action]
            GAME_OBJECTS[0].move(constants.MOVEMENT_DIR[direction][parity][0],
                                 constants.MOVEMENT_DIR[direction][parity][1])
            return "player-moved"



        if len(GAME_OBJECTS) - 1 == 2:
            # --- Determine the parity
            if GAME_OBJECTS[0].y % 2 == 0:
                parity = 'EVEN'
            else:
                parity = 'ODD'
            # --- Determine the parity
            if GAME_OBJECTS[1].y % 2 == 0:
                parity2 = 'EVEN'
            else:
                parity2 = 'ODD'

            # --- Make a movement
            direction = constants.MOVEMENT_TWO_UNITS[action]
            GAME_OBJECTS[0].move(constants.MOVEMENT_DIR[direction[0]][parity][0],
                                 constants.MOVEMENT_DIR[direction[0]][parity][1])
            GAME_OBJECTS[1].move(constants.MOVEMENT_DIR[direction[1]][parity2][0],
                                 constants.MOVEMENT_DIR[direction[1]][parity2][1])
            return "player-moved"


        # --- Movement commands for three units
        if len(GAME_OBJECTS) - 1 == 3:
            # --- Determine the parity
            if GAME_OBJECTS[0].y % 2 == 0:
                parity = 'EVEN'
            else:
                parity = 'ODD'
            # --- Determine the parity
            if GAME_OBJECTS[1].y % 2 == 0:
                parity2 = 'EVEN'
            else:
                parity2 = 'ODD'
            # --- Determine the parity
            if GAME_OBJECTS[2].y % 2 == 0:
                parity3 = 'EVEN'
            else:
                parity3 = 'ODD'
            # --- Make a movement
            direction = constants.MOVEMENT_THREE_UNITS[action]
            GAME_OBJECTS[0].move(constants.MOVEMENT_DIR[direction[0]][parity][0],
                                 constants.MOVEMENT_DIR[direction[0]][parity][1])
            GAME_OBJECTS[1].move(constants.MOVEMENT_DIR[direction[1]][parity2][0],
                                 constants.MOVEMENT_DIR[direction[1]][parity2][1])
            GAME_OBJECTS[2].move(constants.MOVEMENT_DIR[direction[1]][parity3][0],
                                 constants.MOVEMENT_DIR[direction[1]][parity3][1])
            return "player-moved"



if __name__ == "__main__":
    env = Game(human = True, render = True)
    env.game_initialize()
    env.game_main_loop(1)