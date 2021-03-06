### Renders a level to a pygame surface

import pygame

import constants as c
from ai.predicate import Solves

WIN_W = 800
WIN_H = 600
VIEW_W = 512
VIEW_H = 512
MARGIN = 8

class Renderer:
    def __init__(self):
        #self.tiles = Tileset("/home/fish/Pictures/M_BISON_YESSSSSSS.jpg", 24, 24)
        self.level_surf = pygame.Surface((VIEW_W, VIEW_H))
        self.view_w = 0.75
        self.view_h = 0.75
        self.tiles = AsciiTiles('Deja Vu Sans Mono')
        self.tiles = Tileset('graphics/bad%s.png', 16, 16)
        self.font = pygame.font.SysFont('Deja Vu Sans Mono', 12)
        self.title_font = pygame.font.SysFont('Deja Vu Sans Mono', 18)
        self.centre = ()
        self.view = None

    def center_view(self, world):
        w = self.level_surf.get_width()
        h = self.level_surf.get_height()
        tw = self.tiles.tile_width
        th = self.tiles.tile_height

        player_x = world.player.location[0]
        player_y = world.player.location[1]
        player_view = pygame.Rect(0, 0, self.view_w * w, self.view_w * h)
        player_view.center = (player_x * tw, player_y * th)
        player_view.clamp_ip(0, 0, world.level.width * tw, world.level.height * th)

        self.view = pygame.Rect(0, 0, w, h)
        self.view.center = player_view.center
        self.view.clamp_ip(0, 0, world.level.width * tw, world.level.height * th)

    def render(self, world, surface):
        surface.fill((0, 0, 0))
        # Set up areas to render to
        main_surface = surface.subsurface(MARGIN, MARGIN, VIEW_W, VIEW_H)
        sidebar = surface.subsurface(VIEW_W+MARGIN*2, MARGIN,
                                     (WIN_W-VIEW_W-(MARGIN*3)), VIEW_H)
        inventory_surf = sidebar.subsurface(0, 0,
                                            sidebar.get_width(),
                                            sidebar.get_height()/2 - MARGIN/2)
        messages_surf = sidebar.subsurface(0, sidebar.get_height()/2 + MARGIN/2,
                                           sidebar.get_width(),
                                           sidebar.get_height()/2 - MARGIN/2)
        stats_surf = surface.subsurface(MARGIN, VIEW_W+(MARGIN*2),
                                        WIN_W-(MARGIN*2), WIN_H-VIEW_H-(MARGIN*3))

        if world.state == c.STATE_DIALOGUE:
            self.render_dialogue(main_surface, world)
        else:
            main_surface.blit(self.level_surf, (0, 0))

        self.render_inventory(inventory_surf, world.player)
        self.render_messages(messages_surf, world.messages)
        self.render_stats(stats_surf, world.messages)

    def render_level(self, world):
        # Calculate viewport
        #TODO: receive surface in init?
        surface = self.level_surf
        level = world.level
        player = world.player

        w = surface.get_width()
        h = surface.get_height()
        tw = self.tiles.tile_width
        th = self.tiles.tile_height
        player_x = player.location[0]
        player_y = player.location[1]

        player_view = pygame.Rect(0, 0, self.view_w * w, self.view_w * h)
        player_view.center = (player_x * tw, player_y * th)

        player_view.clamp_ip(0, 0, level.width * tw, level.height * th)
        if not self.view:
            self.center_view(world)

        if player_view.right > self.view.right:
            self.view.right = player_view.right
        elif player_view.left < self.view.left:
            self.view.left = player_view.left

        if player_view.bottom > self.view.bottom:
            self.view.bottom = player_view.bottom
        elif player_view.top < self.view.top:
            self.view.top = player_view.top

        view = self.view
        #if not self.centre:
        #    self.centre = player_view.center

        #view = pygame.Rect(0, 0, w, h)
        #view.center = self.centre

        # Centre view on player
        #if not view.contains(player_view):
        #    view.left = min(view.left, player_view.left)
        #    view.right = max(view.right, player_view.right)
        #    view.top = min(view.top, player_view.top)
        #    view.bottom = max(view.bottom, player_view.bottom)

        #    self.centre = view.center

        surface.fill((0,0,0))
        # Calculate visible tiles
        x1 = max(0, int(view.left / tw))
        y1 = max(0, int(view.top / th))
        x2 = min(level.width, 1+int(view.right / tw))
        y2 = min(level.height, 1+int(view.bottom / th))

        # TODO: Render order!
        radius2 = 20.0 ** 2
        map_memory = player.map_memory[level]
        # NOTE: 1.5x speedup available here by iterating directly
        #for (x, y, tile) in level.get_tiles(x1, y1, x2, y2):
        for y in xrange(y1, y2):
            row = map_memory[y]
            for x in xrange(x1, x2):
                if row[x]:
                    tile = row[x]
                    if (x, y) in player.fov:
                        for thing in tile:
                            surface.blit(self.tiles[thing], (x*tw - view.left, y*th - view.top))
                        #dist2 = max(1,(x - player_x)**2 + (y - player_y)**2)
                        self.tiles.dim_overlay.set_alpha(64 * player.fov[(x,y)]/radius2)
                        #self.tiles.dim_overlay.set_alpha(0)
                        surface.blit(self.tiles.dim_overlay,
                                    (x*tw - view.left, y*th - view.top))
                    else:
                        # First tile is terrain (at the moment...)
                        surface.blit(self.tiles[tile[0]], (x*tw - view.left,
                                                        y*th - view.top))
                        self.tiles.dim_overlay.set_alpha(64)
                        surface.blit(self.tiles.dim_overlay,
                                    (x*tw - view.left, y*th - view.top))

        if world.state == c.STATE_PICK:
            x, y = world.pick_location
            surface.blit(self.tiles.picker, (x*tw-view.left, y*th - view.top))

    def render_dialogue(self, surface, world):
        interlocutor = world.talking_to
        title = 'Talking to: %s' % (interlocutor.name)
        self.draw_text(surface, title, (255, 255, 255), surface.get_rect(), self.title_font)
        title_height = self.title_font.get_linesize()
        input_height = 2 * self.font.get_linesize()
        convo_area = (MARGIN*2, title_height+MARGIN,
                      surface.get_width()-MARGIN*3,
                      surface.get_height()-title_height-MARGIN*2-input_height)
        input_area = (MARGIN*2, surface.get_height()-MARGIN-input_height,
                      surface.get_width()-MARGIN*3, input_height)

        convo_text = '\n'.join(world.conversation)
        self.draw_text(surface, convo_text, (255, 255, 255), convo_area, self.font, align_top=False)
        input_text = 'Ask about: %s' % (world.input_text)
        self.draw_text(surface, input_text, (255, 255, 255), input_area, self.font)

    def render_inventory(self, surface, player):
        surface.fill((25, 25, 25))
        text = []
        #text = '\n'.join([obj.indefinite() for obj in player.contained])
        for obj in player.contained:
            line = obj.indefinite()
            for fact in player.knowledge:
                if type(fact) == Solves and fact.subj == obj:
                    line += ' (solves %s)' % fact.obj
            text.append(line)
        text = '\n'.join(text)
        self.draw_text(surface, text,
                       (255, 255, 255), surface.get_rect(), self.font)

    def render_messages(self, surface, messages):
        surface.fill((25, 25, 25))
        text = '\n'.join(messages[-100:])
        self.draw_text(surface, text,
                       (255, 255, 255), surface.get_rect(), self.font, False)

    def render_stats(self, surface, messages):
        surface.fill((25, 25, 25))

    def draw_text(self, surface, text, color, rect, font, align_top=True):
        """Draw text on surface, wrapped to fit inside rect"""
        if isinstance(text, str):
            text = text.decode('utf-8')
        rect = pygame.Rect(rect)
        line_height = font.get_linesize()
        y = rect.top
        msgs = self.wrap_text(text, rect.width, font)
        max_msgs = rect.height/line_height

        if align_top:
            msgs = msgs[:max_msgs]
        elif len(msgs) >= max_msgs:
            msgs = msgs[len(msgs)-max_msgs:]

        for s in msgs:
            image = font.render(s, True, color)
            surface.blit(image, (rect.left, y))
            y += line_height

        return text

    def wrap_text(self, text, width, font):
        """Break text up into a list of strings which, when rendered with font, fit in width"""
        result = []

        while text:
            i = 1

            # determine if the row of text will be outside our area
            #if y + line_height > rect.bottom:
            #    break

            # determine maximum width of line
            while text[i-1] != '\n' and font.size(text[:i])[0] < width and i < len(text):
                i += 1

            if text[i-1] == '\n':
                result.append(text[:i-1])
            else:
                if i < len(text) and ' ' in text[:i]:
                    i = text.rfind(" ", 0, i) + 1
                result.append(text[:i])
            text = text[i:]

        return result


class BaseTileset(object):
    def __init__(self, width, height):
        self.base_width = width
        self.base_height = height
        self.scale = 1.0

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        value = min(value, 4)
        value = max(value, 0.0625)
        self._scale = value
        self.tile_width = int(self.base_width * value)
        self.tile_height = int(self.base_height * value)
        self.dim_overlay = pygame.Surface((self.tile_width,
                                           self.tile_height))
        self.dim_overlay.fill((0,0,0))
        self.picker = pygame.surface.Surface((int(self.tile_width), int(self.tile_height)), pygame.SRCALPHA)
        self.picker.fill((0, 0, 0, 0))
        pygame.draw.rect(self.picker,
                         (255, 255, 255),
                         (0, 0, self.tile_width, self.tile_height), 1)

class Tileset(BaseTileset):
    def __init__(self, filename, width, height):
        self.filename = filename
        BaseTileset.__init__(self, width, height)

    def load_tile_table(self, filename):
        self.tile_table = []
        for i, name in enumerate(('terrain', 'objects', 'actors')):
            image = pygame.image.load(filename % name).convert_alpha()
            orig_width, orig_height = image.get_size()
            # Scale the image based on how large tiles we want
            image = pygame.transform.scale(image,
                                        (self.tile_width*orig_width/self.base_width,
                                            self.tile_height*orig_height/self.base_height))
            image_width, image_height = image.get_size()
            #image.set_colorkey((255, 255, 255))
            tile_table = []
            for tile_x in range(0, orig_width/self.base_width):
                line = []
                tile_table.append(line)
                for tile_y in range(0, orig_height/self.base_height):
                    rect = (tile_x*self.tile_width, tile_y*self.tile_height,
                            self.tile_width, self.tile_height)
                    line.append(image.subsurface(rect))
            self.tile_table.append(tile_table)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        value = min(value, 4)
        value = max(value, 0.0625)
        # Constrain the real scale value to produce integer values
        constrained = int(self.base_width * value) / float(self.base_width)
        BaseTileset.scale.fset(self, constrained)
        # Store the given scale value to prevent zooming getting stuck
        self._scale = value
        self.load_tile_table(self.filename)
    def __getitem__(self, thing):
        return self.tile_table[thing.tiletype][thing.tileindex[0]][thing.tileindex[1]]

class AsciiTiles(Tileset):
    def __init__(self, font):
        self.fontname = font
        BaseTileset.__init__(self, 20, 20)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        BaseTileset.scale.fset(self, value)
        self.font = pygame.font.SysFont(self.fontname, int(18 * value))
        self.cache = {}

    def __getitem__(self, thing):
        char = getattr(thing, 'char', '?')
        if char not in self.cache:
            rendered = self.font.render(char, True, (255,255,255))
            self.cache[char] = pygame.surface.Surface((self.tile_width, self.tile_height))
            self.cache[char].fill((128, 128, 128))
            self.cache[char].blit(rendered, ((self.tile_width-rendered.get_width())/2,
                                             (self.tile_height-rendered.get_height())/2))
            #pygame.draw.rect(self.cache[char], (32,32,32), (0,0,self.tile_width, self.tile_height+1), 1)

        return self.cache[char]
