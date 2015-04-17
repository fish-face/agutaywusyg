#encoding=utf-8

import random
from pygame import Rect
from collections import defaultdict

from level import TerrainInfo, Region, floor, wall
from generator import Generator
from shape import ArbitraryShape, RectShape
from castle import BuildingGraph
from objects import Door
from constants import LEFT, RIGHT, UP, DOWN, HORIZONTAL, VERTICAL, is_horizontal

from util import pathfinding

grass = TerrainInfo('v', 'grass', (3, 0), False, False)
window = TerrainInfo('o', 'window', (0, 1), True, False)
path = TerrainInfo(u'·', 'path', (2, 0), False, False)

TOP_CENTRE, TOP, SIDE, BOTTOM, BOTTOM_CENTRE = range(5)
PLAIN, WIDE, ANTEROOM = range(3)


class Room(RectShape):
    def __init__(self, *args, **kwargs):
        self.rect = None
        kw = {'drawn': True, 'connect': True, 'parent': None, 'reflect': False}
        kw.update(kwargs)
        rect = Rect(args)
        super(Room, self).__init__(rect)
        self.drawn = kw['drawn']
        self.connect = kw['connect']
        self.parent = kw['parent']
        self.reflect = kw['reflect']
        self.openings = set()
        self.doors = set()

    def draw(self, gen, fill, stroke):
        super(Room, self).draw(gen, fill, stroke)
        # gen.fill_rect(self.rect, fill)
        # gen.draw_points(set(gen.get_outline(self.rect)) - self.openings, stroke)
        for p in self.doors:
            Door(p, level=gen.level)
            # if self.reflect:
            # refl = gen.reflect_rect(self.rect, gen.reflect_axis, gen.reflect_centre)
            #     gen.fill_rect(refl, fill)
            #     gen.draw_points(set(gen.get_outline(refl)) - set(gen.reflect(p, gen.reflect_axis, gen.reflect_centre) for p in self.openings), stroke)

    def __getattr__(self, name):
        # A room isn't necessarily a rectangle, but expose the associated
        # rect-interface anyway
        try:
            return getattr(self.rect, name)
        except AttributeError:
            raise AttributeError('Room object has no attribute %s' % name)

    def __setattr__(self, name, value):
        # As for __getattr__
        if name != 'rect':
            try:
                setattr(self.rect, name, value)
            except AttributeError:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return 'Room %s' % (self.rect,)


class FortressGenerator(Generator):
    def __init__(self, level):
        Generator.__init__(self, level)
        self.size = 80
        self.width = random.randint(self.size*0.4, self.size*0.6) * 2
        self.height = random.randint(self.size*0.4, self.size*0.6) * 2
        self.orientation = random.randint(0,3)
        self.corridor_size = random.randint(self.size*0.2, self.size*0.3)
        self.room_size = random.randint(4, 6)
        self.randomness = 0#random.randint(0, 4)
        self.reflect_axis = HORIZONTAL
        self.reflect_centre = 0.5
        #Room shape

    def generate(self):
        # Calculate valid space
        space = Rect(-self.width / 2, 1,
                     self.width / 2 + 1, self.height - 2)
        # Fill with grass
        # self.fill_rect(-self.width/2-2, 0, self.width+5, self.height, grass)
        self.fill_rect(space, grass)
        self.interior_rect = space
        self.interior_space = set(self.get_rect(space))
        self.mirrored_space = set(
            self.get_rect(space) + self.get_rect(self.reflect_rect(space, self.reflect_axis, self.reflect_centre)))
        self.fixed_rooms = [Rect(-1, 0, 3, self.height)]

        # Create buildings
        self.corridors = []
        # self.rooms = []
        self.shapes = []
        self.add_sanctum(0, self.corridor_size * 2)
        self.add_corridors(-1, self.room_size, DOWN)
        # self.add_corridor(Rect(-1,self.room_size/2,3,self.corridor_size), 1, VERTICAL, False, False)

        # for room in self.rooms:
        #     room.draw(self, floor, wall)
        #     # self.fill_rect(room.rect, floor)
        #     # self.draw_points(self.get_outlines([room.rect]), wall)
        #     if room.width == 1 or room.height == 1:
        #         self.draw_points(self.get_rect(room.rect), grass)

        for shape in self.shapes:
            shape.draw(self, floor, wall)
            shape.mirror(self.reflect_axis, self.reflect_centre).draw(self, floor, wall)

            # for door in graph.doors:
            #    self.draw(door, floor)
            #    Door(door, level=self.level)

    def add_sanctum(self, x, y):
        size = int(1.5 * self.room_size)
        self.sanctum = Room(x - size, y - size, 2 * size + 1, 2 * size + 1)
        size = self.room_size - 1
        inner = Room(x - size, y - size, size * 2 + 1, size * 2 + 1)
        self.shapes.append(self.sanctum)
        self.shapes.append(inner)
        self.sanctum_accessible = False

        # Decide the (primary) connection
        entrance_loc = random.choice((TOP_CENTRE, TOP, SIDE, BOTTOM, BOTTOM_CENTRE))
        if entrance_loc == TOP_CENTRE:
            x, y = self.sanctum.midtop
            d = UP
        elif entrance_loc == TOP:
            x = random.randint(self.sanctum.left + 1, -2)
            y = self.sanctum.top
            d = UP
        elif entrance_loc == SIDE:
            x = self.sanctum.left
            y = random.randint(self.sanctum.top + 1, self.sanctum.bottom - 2)
            d = LEFT
        elif entrance_loc == BOTTOM:
            x = random.randint(self.sanctum.left + 1, -2)
            y = self.sanctum.bottom - 1
            d = DOWN
        elif entrance_loc == BOTTOM_CENTRE:
            x, y = self.sanctum.midbottom
            y -= 1
            d = DOWN

        # Pick a connection style
        entrance_style = random.choice((PLAIN, WIDE, ANTEROOM))
        entrance_style = PLAIN
        sanctum_outline = self.get_outline(self.sanctum.rect, False)

        # entrance = Room(x-1, y-1, 3, 3)
        if is_horizontal(d):
            entrance = Room(x, y - 1, 1, 3)
        else:
            entrance = Room(x - 1, y, 3, 1)
        if entrance_style == PLAIN:
            growth = [False] * 4
            growth[d] = True
            while sum(growth):
                self.grow_room(entrance, growth, self.room_size + 1)
            if max(entrance.w, entrance.h) < 3:
                raise ValueError('Entrance Room failed to grow')
            for p in self.get_outline(entrance.rect, False):
                if p in sanctum_outline:
                    entrance.outline_gaps.add(p)
                    entrance.doors.add(p)
            x, y = self.coords_in_dir(x, y, d, max(entrance.size) - 1)
            entrance.outline_gaps.add((x, y))
            entrance.doors.add((x, y))
            x, y = self.coords_in_dir(x, y, d, 1)
        elif entrance_style == WIDE:
            pass

        self.shapes.append(entrance)
        space = self.mirrored_space - set(self.get_rect(self.sanctum.rect.inflate(2 * self.room_size, 2 * self.room_size)))
        self.connect_with_corridor(0, 1, x, y, space, {(0, 0)} | entrance.inner_edges)
        self.main_corridor = self.shapes[-1]

    def connect_with_corridor(self, x1, y1, x2, y2, space, join):
        # Pathfind through the space
        graph = pathfinding.ObstacleGrid(self.interior_rect, self.interior_space - space)
        path = set(pathfinding.pathfind(graph, (x1, y1), (x2, y2), True, (x1, y1 + 1)))

        # The path is 1 tile wide; expand it
        self.expand(path)
        shape = ArbitraryShape(path)
        # Remove places where the corridor should join other things
        shape.add_gaps(shape.inner_edges & join)
        self.shapes.append(shape)

    def add_corridors(self, x, y, d, n=None, parent=None):
        max_depth = 5
        branch_twice = 0.5

        if n is None:
            n = max_depth
        if n == 0:
            return

        if is_horizontal(d):
            w = 1
            h = 3
        else:
            w = 3
            h = 1
        if n == max_depth:
            new = Room(Rect(x, y, 3, self.sanctum.y - y - 5 - 3))
        else:
            new = self.add_corridor(Rect(x, y, w, h), d, False, False)

            if new:
                if is_horizontal(d):
                    new.openings.add((x, y + 1))
                else:
                    new.openings.add((x + 1, y))

                collisions = new.collidelist(self.shapes[:-1])
                for i in collisions:
                    # overlap = set(self.get_outline(new.rect, False)) & set(self.get_outline(self.shapes[i].rect, False))
                    other_outline = self.shapes[i].inner_edges
                    for p in new.inner_edges:
                        if p in other_outline:
                            new.outline_gaps.add(p)
                        elif self.reflect_axis == HORIZONTAL and p[0] > self.reflect_centre:
                            new.outline_gaps.add(p)
                        elif self.reflect_axis == VERTICAL and p[1] > self.reflect_centre:
                            new.outline_gaps.add(p)
                            #for p in overlap:
                            #    new.openings.add(p)
        if new and (not self.sanctum_accessible or random.random() < 0.8):
            length = max(new.w, new.h)
            branchpoint = (random.randint(5, length) + random.randint(5, length)) / 2
            x2, y2 = self.coords_in_dir(x, y, d, branchpoint)
            # if seek_sanctum:
            #     # Maybe make one branch, but always seek the sanctum
            #     if is_horizontal(d):
            #         if y2 > self.sanctum.bottom:
            #             self.add_corridors(x2, y2, UP, n - 1, new)
            #             if random.random() < branch_twice:
            #                 self.add_corridors(x2, y2 + 2, DOWN, n - 1, new)
            #         else:
            #             self.add_corridors(x2, y2 + 2, DOWN, n - 1, new)
            #             if random.random() < branch_twice:
            #                 self.add_corridors(x2, y2, UP, n - 1, new)
            #     else:
            #         if x2 < self.sanctum.left:
            #             self.add_corridors(x2 + 2, y2, RIGHT, n - 1, new)
            #             if random.random() < branch_twice:
            #                 self.add_corridors(x2, y2, LEFT, n - 1, new)
            #         else:
            #             self.add_corridors(x2, y2, LEFT, n - 1, new)
            #             if random.random() < branch_twice:
            #                 self.add_corridors(x2 + 2, y2, RIGHT, n - 1, new)
            # else:
            if n == max_depth:
                branch = (0, 1)
            else:
                branch = random.choice(((1,), (0,), (0, 1)))
            if is_horizontal(d):
                if 0 in branch:
                    self.add_corridors(x2, y2, UP, n - 1, new)
                if 1 in branch:
                    self.add_corridors(x2, y2 + 2, DOWN, n - 1, new)
            else:
                if 0 in branch:
                    self.add_corridors(x2, y2, LEFT, n - 1, new)
                if 1 in branch:
                    self.add_corridors(x2 + 2, y2, RIGHT, n - 1, new)

        if n == max_depth:
            # Add rooms
            pass

    def add_corridor(self, rect, direction=None, both_sides=True, symmetry=None):
        room = Room(rect, reflect=True)
        if room.w > 3 and room.h > 3:
            pass
        else:
            if direction is None:
                direction = random.choice((UP, DOWN, LEFT, RIGHT))
            growth = [False] * 4
            growth[direction] = True
            space = self.interior_space - reduce(set.union, (s.points for s in self.shapes))
            while sum(growth):
                self.grow_room(room, growth, self.corridor_size, space=space)

        if max(room.w, room.h) <= 5:
            return None

        self.shapes.append(room)

        return room

        if both_sides and symmetry is None:
            symmetry = random.choice((True, False))
        if orientation == HORIZONTAL:
            start = room.x
            stop = room.right
            side_a = room.y - 1
            side_b = room.bottom + 1
        else:
            start = room.y
            stop = room.bottom
            side_a = room.x - 1
            side_b = room.right + 1
        min_room_sep = int((self.room_size) * (1 - self.randomness/16.0))
        points = list(self._rand_points_between(start, stop, min_room_sep, self.room_size))
        #random.shuffle(points)
        if symmetry:
            for x in points:
                if orientation == HORIZONTAL:
                    self.add_room(Rect(x, side_a, 0, 0))
                    self.add_room(Rect(x, side_b, 0, 0))
                else:
                    self.add_room(Rect(side_a, x, 0, 0))
                    self.add_room(Rect(side_b, x, 0, 0))
        else:
            for x in points:
                if orientation == HORIZONTAL:
                    self.add_room(Rect(x, side_a, 0, 0))
                else:
                    if x == start+self.room_size:#random.randint(0, 6) < recursion_chance:
                        self.add_corridor(Rect(side_a, x, 0, 3), symmetry=True, orientation=HORIZONTAL)
                    else:
                        self.add_room(Rect(side_a, x, 0, 0))

            if both_sides:
                points = list(self._rand_points_between(start, stop, min_room_sep, self.room_size))
                #random.shuffle(points)
                for x in points:
                    if orientation == HORIZONTAL:
                        self.add_room(Rect(x, side_a, 0, 0))
                    else:
                        self.add_room(Rect(side_a, x, 0, 0))


    def _rand_points_between(self, start, stop, min_dist, max_dist):
        i = start
        while i < stop:
            yield i
            i += random.randint(min_dist, max_dist)
        raise StopIteration


    def add_room(self, rect):
        room = Room(rect, reflect=True)
        if room.w > 0 and room.h > 0:
            pass
        else:
            growth = [True] * 4
            while sum(growth):
                self.grow_room(room, growth, self.room_size)

        self.shapes.append(room)

    def grow_room(self, room, growing, max_size, pad_v=0, pad_h=0, space=None):
        """Tries to grow a room in the specified direction

        Returns whether the growth succeeded"""
        space = space if space is not None else self.interior_space
        for d, grow in enumerate(growing):
            if not grow:
                continue
            if (((d == LEFT or d == RIGHT) and room.w > max_size) or
                    ((d == UP or d == DOWN) and room.h > max_size)):
                growing[d] = False
                continue
            left, top, width, height = room.x, room.y, room.w, room.h
            if d == LEFT:
                left -= 1
                width += 1
                if room.w <= 1:
                    collision = None
                else:
                    collision = Rect(room.x - pad_h, room.y + 1 - pad_v,
                                     1 + pad_h, max(1, room.h + 2 * pad_v - 2))
            elif d == RIGHT:
                width += 1
                if room.w <= 1:
                    collision = None
                else:
                    collision = Rect(room.right - 1 - pad_h, room.y + 1,
                                     1 + pad_h, max(1, room.h + 2 * pad_v - 2))
            elif d == DOWN:
                height += 1
                if room.h <= 1:
                    collision = None
                else:
                    collision = Rect(room.x + 1 - pad_h, room.bottom - 1,
                                     max(1, room.w - 2 + 2 * pad_h), 1 + pad_v)
            elif d == UP:
                top -= 1
                height += 1
                if room.h <= 1:
                    collision = None
                else:
                    collision = Rect(room.x + 1 - pad_h, room.y - pad_v,
                                     max(1, room.w - 2 + 2 * pad_h), 1 + pad_v)
            if collision is not None:
                building_collisions = collision.collidelistall([r.rect for r in self.shapes if isinstance(r, Room)])
            else:
                building_collisions = []
            if not (set(Generator.get_rect(collision)) - space) and len(building_collisions) == 0:
                room.left = left
                room.width = width
                room.top = top
                room.height = height
            else:
                print room.rect, collision, d, building_collisions, (set(Generator.get_rect(collision)) - space)
                growing[d] = False


pass

