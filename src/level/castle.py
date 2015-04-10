#encoding=utf-8

import random
from collections import defaultdict
from pygame import Rect

from level import TerrainInfo, Region, floor, wall
from generator import Generator
from objects import Door
from constants import UP, DOWN, LEFT, RIGHT
import util

grass = TerrainInfo('v', 'grass', (3,0), False, False)
window = TerrainInfo('o', 'window', (0,1), True, False)
path = TerrainInfo(u'·', 'path', (2,0), False, False)

GH_PROJECT = 0

KEEP_CENTRE = 0
KEEP_SIDE = 1
KEEP_EXTERNAL = 2
KEEP_STYLES = (0,1)

class Way(object):
    def __init__(self, room, door):
        self.room = room
        self.door = door


class BuildingGraph(object):
    def __init__(self, seed_points, seed_rooms, space, num_rooms, paths=1):
        self.seed_points = seed_points
        self.seed_rooms = seed_rooms
        points = seed_points[:]
        points += [room.center for room in seed_rooms]
        self.n_seeds = len(points)
        list_space = list(space)
        # Pick points to draw buildings around
        while len(points) < num_rooms + len(seed_rooms):
            p = random.choice(list_space)
            points.append(p)
            for q in points[:-1]:
                if util.manhattan(p, q) < 4:
                    points.remove(p)
                    break

        self.space = space
        self.cells = []
        self.interior = []
        self.borders = []
        #self.subdivide(boundary)

        self.points = points
        #self.voronoi_ish(self.get_wrecked(boundary))
        self.buildings = self.make_buildings()

        self.edges = [(i,i+1) for i in range(len(points)-1)]

    def make_buildings(self):
        rects = [Rect(p[0], p[1], 1, 1) for p in self.seed_points]
        growing = [[True] * 4 for p in self.seed_points]

        rects += [r for r in self.seed_rooms]
        growing += [[False] * 4 for r in self.seed_rooms]

        rects += [Rect(p[0], p[1], 1, 1) for p in self.points[self.n_seeds:]]
        growing += [[True] * 4 for p in self.points[self.n_seeds:]]

        amalgamate_limit = 10
        changed = True
        adjacency = [[] for p in rects]
        for i in range(len(self.seed_points), self.n_seeds):
            for j in range(i+1, self.n_seeds):
                if set(Generator.get_outline(rects[i])) & set(Generator.get_outline(rects[j])):
                    adjacency[i].append(j)

        # Expand rectangles around the points we picked
        while changed:
            changed = False
            for i, r in enumerate(rects):
                for d in [UP, DOWN, LEFT, RIGHT]:
                    changed |= self.grow_rect(i, r, growing[i], adjacency, rects, d)

        self.connect_rooms(rects, adjacency)

        # Try and amalgamate small rectangles
        #merges = [None] * len(rects)
        #for i, r in enumerate(rects):
        #    if r.height == 1 or r.width == 1:
        #        r.height = 0
        #        r.width = 0
        #    if r.height*r.width < amalgamate_limit**2: # or random.randrange(6) == -1:
        #        if self.merge_rect(i, r, merges, adjacency[i], rects):
        #            continue

        #merged = [[] for i in range(len(rects))]
        #for i, r in enumerate(rects):
        #    if merges[i] == None:
        #        merged[i].append(r)
        #    else:
        #        merged[merges[i]].append(r)

        #return merged

        return [[r] for r in rects]

    def merge_rect(self, i, rect, merges, adjacency, rects):
        for j in adjacency:
            if merges[j] is not None:
                j = merges[j]
            merges[i] = j
            return True
        return False

    def grow_rect(self, i, rect, growth, adjacency, rects, direction):
        """Tries to grow a rectangle in the specified direction

        Returns whether the growth succeeded"""
        if rect.w > 100 or rect.h > 100:
            growth[direction] = False
            return False
        if growth[direction]:
            left, top, width, height = rect.x, rect.y, rect.w, rect.h
            if direction == LEFT:
                left -= 1
                width += 1
                if height > 1:
                    collision = Rect(rect.x, rect.y+1, 1, rect.h-2)
                else:
                    collision = Rect(rect.x, rect.y, 1, 1)
            elif direction == RIGHT:
                width += 1
                if height > 1:
                    collision = Rect(rect.right-1, rect.y+1, 1, rect.h-2)
                else:
                    collision = Rect(rect.right-1, rect.y, 1, 1)
            elif direction == DOWN:
                height += 1
                if width > 1:
                    collision = Rect(rect.x+1, rect.bottom-1, rect.w-2, 1)
                else:
                    collision = Rect(rect.x, rect.bottom-1, 1, 1)
            elif direction == UP:
                top -= 1
                height += 1
                if width > 1:
                    collision = Rect(rect.x+1, rect.y, rect.w-2, 1)
                else:
                    collision = Rect(rect.x, rect.y, 1, 1)
            building_collisions = collision.collidelistall(rects)
            try:
                building_collisions.remove(i)
            except ValueError:
                pass
            if not (set(Generator.get_rect(collision)) - self.space) and len(building_collisions) == 0:
                rect.left = left
                rect.width = width
                rect.top = top
                rect.height = height
                #if rect.width >= 8 and rect.height >= 8 and random.randrange(5) == 0:
                #    growth[direction] = False
                return True
            else:
                growth[direction] = False
                if building_collisions:
                    care_about = [j for j in building_collisions if j < len(self.points)]
                    # If we collided with a building, make a note.
                    adjacency[i] += care_about
                    for j in care_about:
                        adjacency[j].append(i)

        return False

    def connect_rooms(self, rooms, connections):
        def connect(a, b):
            r = rooms[a]
            s = rooms[b]
            edge = list(set(Generator.get_outline(r, eight=False)) &
                        set(Generator.get_outline(s, eight=False)))
            if edge:
                self.doors.append(random.choice(edge))
                self.path[tuple(r)].append(Way(s, self.doors[-1]))
                return True
            return False

        self.path = defaultdict(list)
        self.doors = []
        current = 0
        stack = [0]
        unvisited = range(len(rooms))
        unvisited.remove(current)
        while unvisited:
            neighbours = list(set(connections[current]))
            random.shuffle(neighbours)
            room = None
            for room in neighbours:
                #to-do: remove from neighbours?
                if room in unvisited and connect(current, room):
                    break
            if room in unvisited:
                current = room
                stack.append(room)
                unvisited.remove(current)
            else:
                stack.pop()

            if stack:
                current = stack[-1]
            else:
                current = random.choice(unvisited)
                stack.append(current)
                unvisited.remove(current)

    def get_wrecked(self, boundary):
        horizontals = [boundary.left, boundary.right]
        verticals = [boundary.top, boundary.bottom]
        for i, p in enumerate(self.points):
            left = None
            right = None
            up = None
            down = None
            for q in self.points[i+1:]:
                if q == p:
                    continue
                dx = (q[0] - p[0])/2
                dy = (q[1] - p[1])/2
                if dx > 0:
                    if right is None or right > dx:
                        right = dx
                elif dx < 0:
                    if left is None or left > -dx:
                        left = -dx
                if dy > 0:
                    if down is None or down > dy:
                        down = dy
                elif dy < 0:
                    if up is None or up > -dy:
                        up = -dy
            if left:
                horizontals.append(p[0]-left)
            if right:
                horizontals.append(p[0]+right)
            if down:
                verticals.append(p[1]+down)
            if up:
                verticals.append(p[1]-up)
        horizontals.sort()
        verticals.sort()

        h_old = horizontals[0]
        rects = []
        for h in horizontals:
            v_old = verticals[0]
            for v in verticals:
                rect = Rect(h_old, v_old, h-h_old, v-v_old)
                if rect.width == 0 or rect.height == 0:
                    continue
                rects.append(rect)
                v_old = v
            h_old = h

        return rects

    def voronoi_ish(self, rects):
        nearest = defaultdict(set)
        for rect in rects:
            p = self.points[0]
            dist = util.manhattan(rect.center, p)
            for q in self.points[1:]:
                d = util.manhattan(rect.center, q)
                if d < dist:
                    dist = d
                    p = q
            nearest[p] |= set(self.get_rect(rect))

        for (i, p) in enumerate(self.points):
            for q in self.points[i+1:]:
                self.borders += nearest[p] & nearest[q]

    def subdivide(self, boundary, divisions=3, limit=10):
        if divisions == 0 or boundary.width < limit or boundary.height < limit:
            self.borders.append(boundary)
            return

        x = int(random.triangular(boundary.left+2, boundary.right-1))
        y = int(random.triangular(boundary.top+2, boundary.bottom-1))
        self.subdivide(Rect(boundary.left, boundary.top,
                            x-boundary.left, y-boundary.top), divisions-1, limit)
        self.subdivide(Rect(x, boundary.top,
                            boundary.right-x, y-boundary.top), divisions-1, limit)
        self.subdivide(Rect(boundary.left, y,
                            x-boundary.left, boundary.bottom-y), divisions-1, limit)
        self.subdivide(Rect(x, y,
                            boundary.right-x, boundary.bottom-y), divisions-1, limit)


class CastleGenerator(Generator):
    def __init__(self, level):
        Generator.__init__(self, level)
        self.size = 50
        self.width = random.randint(self.size*0.4, self.size*0.6) * 2
        self.height = random.randint(self.size*0.4, self.size*0.6) * 2
        self.orientation = random.randint(0,3)
        self.turretsize = random.randint(6,10)
        self.gatesize = random.randint(1,4)
        self.wallwidth = random.randint(3,4)
        self.turret_project = random.randint(2, min(4, self.turretsize-3))
        self.gatehouse_project = random.randint(0,4)
        if self.gatesize % 2 == 1:
            self.width -= 1

    def generate(self):
        # Fill with grass
        self.fill_rect(-self.width/2-self.turret_project-10,
                               -self.turret_project-10,
                               self.width+2*(self.turret_project+10),
                               self.height+2*(self.turret_project+10), grass)
        # Calculate valid space for buildings
        quad = Rect(-self.width/2+self.wallwidth+1, self.wallwidth,
                        self.width-self.wallwidth*2-1, self.height-self.wallwidth*2)
        self.interior_space = set(self.get_rect(quad.inflate(2, 2)))
        self.fixed_rooms = []

        # Draw outer walls
        self.fourwalls(self.width,
                       self.height,
                       self.turretsize,
                       self.wallwidth,
                       self.turret_project,
                       self.gatesize,
                       self.gatehouse_project,
                       4)

        # Keep dimensions
        k_gs = (self.gatesize + 2) % 4 if self.gatesize != 2 else 4

        if self.height < 75:
            keep_style = KEEP_SIDE
        else:
            keep_style = random.choice(KEEP_STYLES)

        if keep_style == KEEP_CENTRE:
            k_w = (random.randint(int(self.width*0.3), int(self.width*0.5))/2)*2 + k_gs
            k_h = random.randint(int(self.height*0.3), int(self.height*0.5))
            k_x, k_y = 0, (self.height-k_h)/2
            side = 0
        elif keep_style == KEEP_SIDE:
            k_w = (random.randint(int(self.width*0.4), int(self.width*0.6))/2)*2 + k_gs
            k_h = random.randint(int(self.height*0.4), int(self.height*0.6))
            side = random.choice((-1, 1))
            k_x, k_y = (self.width-k_w)/2*side, (self.height-k_h)


        # Draw keep
        self.translate(k_x, k_y)

        self.fourwalls(k_w, k_h,
                       self.turretsize,
                       self.wallwidth+1,
                       self.turret_project,
                       k_gs, 0, 4)

        self.translate(-k_x, -k_y)

        path_to_keep = self.get_path(0, 1, k_x, k_y, self.gatesize, k_gs)
        for p in path_to_keep:
            self.draw(p, path)

        self.expand(path_to_keep, 2)
        self.interior_space -= set(path_to_keep)

        margin = 6
        if keep_style == KEEP_CENTRE:
            around_keep = Rect(-k_w/2-(self.wallwidth+margin), self.height/2-k_h/2-self.wallwidth-margin,
                               k_w+(self.wallwidth+margin)*2, k_h+(self.wallwidth+margin)*2)
            self.interior_space -= set(self.get_rect(around_keep))
        elif keep_style == KEEP_SIDE:
            if side == -1:
                left = -self.width/2+self.wallwidth
                width = k_w + margin
            else:
                left = self.width/2-self.wallwidth-k_w-margin
                width = k_w + margin
            around_keep = Rect(left, self.height/2-self.wallwidth-margin,
                               width, self.height)
            self.interior_space -= set(self.get_rect(around_keep))

        # Pick alternative entrance
        if keep_style == KEEP_CENTRE:
            alt_entrance_side = random.choice((LEFT, DOWN, RIGHT))
            if alt_entrance_side == LEFT:
                exit_room = (-k_w/2, self.height/2)
                exit_room_space = Rect(-k_w/2-9, self.height/2-5, 10, 10)
            elif alt_entrance_side == RIGHT:
                exit_room = (k_w/2+1, self.height/2)
                exit_room_space = Rect(k_w/2, self.height/2-5, 10, 10)
            elif alt_entrance_side == DOWN:
                exit_room = (0, self.height/2 + k_h/2+1)
                exit_room_space = Rect(-5, self.height/2 + k_h/2, 10, 10)
        elif keep_style == KEEP_SIDE:
            if side == -1:
                exit_room = (-self.width/2+k_w+1, self.height - k_h/2)
                exit_room_space = Rect(-self.width/2+k_w+1, self.height - k_h/2 - 5, 10, 10)
            else:
                exit_room = (self.width/2-k_w, self.height - k_h/2)
                exit_room_space = Rect(self.width/2-k_w-9, self.height - k_h/2 - 5, 10, 10)
        self.interior_space |= set(self.get_rect(exit_room_space))

        # Creaee buildings
        entrance_room = (self.gatesize/2+3, 10)
        graph = BuildingGraph([entrance_room, exit_room], self.fixed_rooms, self.interior_space, 10, 1)

        # Draw building walls
        for building in graph.buildings:
            if building[0] not in self.fixed_rooms:
                self.draw_points(self.get_outlines(building), wall)
                if building[0].width == 1 or building[0].height == 1:
                    self.draw_points(self.get_rect(building[0]), grass)

        for door in graph.doors:
            self.draw(door, floor)
            Door(door, level=self.level)

        self.draw((self.gatesize/2+2, 10), floor)
        Door((self.gatesize/2+2, 10), level=self.level)

        self.lock_doors([x[0] for x in graph.buildings], graph.path)

    def fourwalls(self, width, height, turretsize, wallwidth, turret_project, gatesize, gatehouse_project, turrets):
        turret_inner = turretsize - turret_project
        wall_inner = max(turret_inner, wallwidth - 1)
        half_width = (width-1)/2
        gh_width = 2+2*wallwidth+gatesize*3
        #gh_width += 2 if gatesize == 1 else 0

        self.fill_rect(-half_width, 1, width, height-1, floor)
        # Front wall
        self.fill_rect(-half_width+(turret_inner), 0,
                       width-2*(turret_inner-1), 1, wall)
        self.fill_rect(-half_width+wall_inner, wallwidth-1,
                       width-2*(wall_inner), 1, wall)
        self.fill_rect(-gatesize/2+1, 0, gatesize, wallwidth, floor)
        self.fixed_rooms.append(self.transform(Rect(-width/2+(wall_inner), 0,
                                                    width/2-wall_inner-gh_width/2+2, wallwidth)))
        self.fixed_rooms.append(self.transform(Rect(gh_width/2, 0,
                                                    width/2-wall_inner-gh_width/2+2, wallwidth)))
        self.interior_space -= set(self.transform_points(self.get_rect(-half_width, 0, width, wallwidth)))

        # Front left turret
        self.translate(-half_width, 0)
        self.tower(-turret_project, -turret_project, turretsize)
        #for p in ((1, turret_inner-1), (turret_inner-1, 1)):
        #    self.draw(p, floor)
        #    Door(self.transform(p), level=self.level)
        # Left wall
        self.fill_rect(0, turret_inner, 1, height-2*turret_inner, wall)
        self.fill_rect(wallwidth-1, wall_inner, 1, height-2*wall_inner, wall)
        self.fixed_rooms.append(self.transform(Rect(0, turret_inner-1, wallwidth, height-2*(turret_inner-1))))
        self.interior_space -= set(self.transform_points(self.get_rect(0, 0, wallwidth, height)))
        # Front right turret
        self.translate(width, 0)
        self.tower(-turret_inner, -turret_project, turretsize)
        #for p in ((-2, turret_inner-1), (-turret_inner, 1)):
        #    self.draw(p, floor)
        #    Door(self.transform(p), level=self.level)
        # Right wall
        self.fill_rect(-wallwidth, wall_inner, 1, height-2*wall_inner, wall)
        self.fill_rect(-1, turret_inner, 1, height-2*turret_inner, wall)
        self.fixed_rooms.append(self.transform(Rect(-wallwidth, turret_inner-1, wallwidth, height-2*(turret_inner-1))))
        self.interior_space -= set(self.transform_points(self.get_rect(-wallwidth, 0, wallwidth, height)))

        # Back right turret
        self.translate(0, height)
        self.tower(-turret_inner, -turret_inner, turretsize)
        # Back left turret
        self.translate(-width, 0)
        self.tower(-turret_project, -turret_inner, turretsize)

        # Back wall
        self.fill_rect(wall_inner, -wallwidth, width-2*wall_inner, 1, wall)
        self.fill_rect(turret_inner, -1, width-2*turret_inner, 1, wall)
        self.fixed_rooms.append(self.transform(Rect(turret_inner-1, -wallwidth,
                                                    width-2*(turret_inner-1), wallwidth)))
        self.interior_space -= set(self.transform_points(self.get_rect(0, -wallwidth, width-1, wallwidth)))

        self.translate(half_width, -height)

        self.gatehouse(gatehouse_project, gh_width, gatesize, wallwidth)

    def tower(self, x, y, size):
        self.fill_rect(x, y, size, size, wall)
        self.fill_rect(x+1, y+1, size-2, size-2, floor)
        self.interior_space -= set(self.transform_points(self.get_rect(x, y, size, size)))
        self.fixed_rooms.append(self.transform(Rect(x, y, size, size)))

    def gatehouse(self, projection, width, gatesize, wallwidth):
        turret_size = (width - gatesize)/2
        # Check bottom of gatehouse tower won't abut inner wall
        if turret_size - projection == wallwidth - 1:
            projection -= 1
        gateheight = turret_size/2-projection
        left = -gatesize/2+1
        right = gatesize/2

        self.draw_line(left-1, 0, left-1, self.wallwidth-1, wall)
        self.draw_line(right+1, 0, right+1, self.wallwidth-1, wall)

        self.tower(left-turret_size, gateheight-turret_size/2, turret_size)
        self.tower(right+1, gateheight-turret_size/2, turret_size)
        self.fill_rect(left, -projection, gatesize, turret_size, path)

        self.draw((left-1, gateheight+1), window)
        self.draw((right+1, gateheight+1), window)
        self.draw((left-1, gateheight-1), window)
        self.draw((right+1, gateheight-1), window)
        if turret_size - projection < wallwidth - 1:
            self.draw((left-1, wallwidth-2), window)
            self.draw((right+1, wallwidth-2), window)

        for p in self.get_line(left, gateheight, right, gateheight):
            Door(self.transform(p), level=self.level)

    def get_path(self, x1, y1, x2, y2, w1, w2):
        path = []
        for offset in range(-w1/2+1, 1+w1/2):
            path += self.get_line(x1+offset, y1, x1+offset, (y1+y2)/2)
            path += self.get_line(x1, (y1+y2)/2+offset, (x1+x2)/2, (y1+y2)/2+offset)
        for offset in range(-w2/2+1, 1+w2/2):
            path += self.get_line((x1+x2)/2, (y1+y2)/2+offset, x2, (y1+y2)/2+offset)
            path += self.get_line(x2+offset, (y1+y2)/2, x2+offset, y2)

        return set(path)

    def lock_doors(self, rooms, path):
        def remove_below(room):
            try:
                unlocked.remove(room)
            except:
                pass
            for r in path[tuple(room)]:
                remove_below(r.room)

        unlocked = rooms
        keys_placed = 0
        while unlocked and keys_placed < 4:
            lock_target = random.choice(unlocked)
            remove_below(lock_target)
            keys_placed += 1
