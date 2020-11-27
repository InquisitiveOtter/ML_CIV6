# File which contains the map classes and information
# Snippets of this code was taken from hexgrid.py at: https://github.com/Mekire/hex_pygame_redit

import pygame
import constants



class HexMap:
    def __init__(self,
                 num_rows,
                 num_columns,
                 cell_size,
                 cell_offset):

        self.num_rows = num_rows
        self.num_columns = num_columns
        self.cell_size = cell_size
        self.cell_offset = cell_offset
        self.make_grid()



    def make_grid(self):
        row_offset = int(constants.HEX_SIZE / 2)
        column_offset = int(constants.HEX_SIZE * 6 / 8)
        w, h  = self.cell_size
        self.grid = {}
        for y in range(self.num_rows):
            for x in range(self.num_columns):
                left = (row_offset * (y%2)) + (w * x) + self.cell_offset
                top = (column_offset * y) + self.cell_offset
                rect = pygame.Rect(left, top, w, h)

                self.grid[(x, y)] = HexCell((x, y), rect, "GRASSLAND")



class HexCell(pygame.sprite.Sprite):
    def __init__(self,
                 index,
                 rect,
                 terrain):
        super(HexCell, self).__init__()
        self.index = index
        self.rect = rect
        self.set_terrain(terrain)

    def set_terrain(self,
                    terrain_type):
        """Terrian defintions"""
        #self.image_outline = constants.S_OUTLINE
        self.terrain_type = terrain_type.upper()

        # --- Terrain type defintions with texture names (TODO)
        if self.terrain_type == 'GRASSLAND':
            self.movement_cost = 2
            self.block_path = False
            self.image = constants.S_PLAINS

        if self.terrain_type == 'MOUNTAIN':
            self.movement_cost = 200
            self.block_path = True

        if self.terrain_type == 'EDGE':
            self.movement_cost = 200
            self.block_path = True

    def get_neighbors(self, grid):
        offset_indices = {
            0: [(-1, 0), (-1, -1), (0, -1), (1, 0), (0, 1), (-1, 1)],
            1: [(-1, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1)]}
        offsets = offset_indices[self.index[1] % 2]
        neighbors = []
        for off in offsets:
            try:
                n = grid[(off[0] + self.index[0], off[1] + self.index[1])]
                neighbors.append(n)
            except KeyError:
                pass
        return neighbors