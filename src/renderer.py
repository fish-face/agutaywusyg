### Renders a level to a pygame surface

import pygame

class Renderer:
    def __init__(self):
        #self.tiles = Tileset("/home/fish/Pictures/M_BISON_YESSSSSSS.jpg", 24, 24)
        self.view_w = 0.75
        self.view_h = 0.75
        self.tiles = AsciiTiles('Deja Vu Sans Mono')
        self.centre = ()

    def render(self, surface, level, player):
        # Calculate viewport
        #TODO: receive surface in init?
        w = surface.get_width()
        h = surface.get_height()
        tw = self.tiles.tile_width
        th = self.tiles.tile_height

        player_view = pygame.Rect(0, 0, self.view_w * w, self.view_w * h)
        player_view.center = (player.location[0] * tw,
                              player.location[1] * th)

        if not self.centre:
            self.centre = player_view.center

        view = pygame.Rect(0, 0, w, h)
        view.center = self.centre

        #Centre view on player
        if not view.contains(player_view):
            view.left = min(view.left, player_view.left)
            view.right = max(view.right, player_view.right)
            view.top = min(view.top, player_view.top)
            view.bottom = max(view.bottom, player_view.bottom)

            self.centre = view.center

        surface.fill((0,0,0))
        #Calculate visible tiles
        x1 = max(0, int(view.left / tw))
        y1 = max(0, int(view.top / th))
        x2 = min(level.width, int(view.right / tw))
        y2 = min(level.height, int(view.bottom / th))

        #TODO: Render order!
        for (x, y, tile) in level.get_tiles(x1, y1, x2, y2):
            for thing in tile:
                surface.blit(self.tiles[thing], (x*tw - view.left,
                                                 y*th - view.top))

        #for obj in objects:
        #   if not obj.location: continue

        #   x, y = obj.location
        #   obj_image = self.tiles[obj]
        #   surface.blit(obj_image, (x*self.tile_width, y*self.tile_height))

class Tileset(object):
    def __init__(self, filename, width, height):
        self.tile_width = 12
        self.tile_height = 12
        self.load_tile_table(filename, width, height)

    def load_tile_table(self, filename, width, height):
        image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        self.tile_table = tile_table

    def __getitem__(self, thing):
        return self.tile_table[thing.tileindex[0]][thing.tileindex[0]]

class AsciiTiles(Tileset):
    def __init__(self, font):
        self.fontname = font
        self.scale = 1/2.0

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.tile_width = 16 * value
        self.tile_height = 16 * value
        self.font = pygame.font.SysFont(self.fontname, int(20 * value))
        self.cache = {}

    def __getitem__(self, thing):
        char = getattr(thing, 'char', '?')
        if char not in self.cache:
            self.cache[char] = self.font.render(char, True, (255,255,255))

        return self.cache[char]
