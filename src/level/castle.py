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

class BuildingGraph(object):
    def __init__(self, boundary, space, num_rooms, paths=1):
        points = []
        list_space = list(space)
        # Pick points to draw buildings around
        while len(points) < num_rooms:
            p = random.choice(list_space)
            for q in points:
                if util.manhattan(p, q) < 3:
                    continue
            points.append(p)

        self.space = space
        self.cells = []
        self.interior = []
        self.borders = []
        #self.subdivide(boundary)

        self.points = points
        #self.voronoi_ish(self.get_wrecked(boundary))
        self.borders = self.make_buildings()

        self.edges = [(i,i+1) for i in range(len(points)-1)]

    def make_buildings(self):
        rects = [Rect(p[0], p[1], 0, 0) for p in self.points]
        growing = [[True, True, True, True] for p in self.points]
        amalgamate_limit = 8
        changed = True
        # Expand rectangles around the points we picked
        while changed:
            changed = False
            for i, r in enumerate(rects):
                for d in [UP, DOWN, LEFT, RIGHT]:
                    changed |= self.grow_rect(i, r, growing[i], rects, d)

        # Randomly shrink some rectangles
        #for r in rects:
        #    for d in [UP, DOWN, LEFT, RIGHT]:
        #        if random.randrange(40) == 0:
        #            if d == LEFT:
        #                r.left += 2
        #                r.width -= 2
        #            elif d == RIGHT:
        #                r.width -= 2
        #            elif d == DOWN:
        #                r.height -= 2
        #            elif d == UP:
        #                r.top += 2
        #                r.height -= 2

        # Try and amalgamate small rectangles
        merges = [None] * len(rects)
        for i, r in enumerate(rects):
            if r.height == 1 or r.width == 1:
                r.height = 0
                r.width = 0
            if r.height < amalgamate_limit or random.randrange(6) == -1:
                if self.merge_rect(i, r, merges, growing[i], rects, UP):
                    continue
                if self.merge_rect(i, r, merges, growing[i], rects, DOWN):
                    continue
            if r.width < amalgamate_limit or random.randrange(6) == -1:
                if self.merge_rect(i, r, merges, growing[i], rects, LEFT):
                    continue
                if self.merge_rect(i, r, merges, growing[i], rects, RIGHT):
                    continue
            #print r if isinstance(r, Rect) else 'list', growing[i]

        merged = [[] for i in range(len(rects))]
        for i, r in enumerate(rects):
            if merges[i] == None:
                merged[i].append(r)
            else:
                merged[merges[i]].append(r)

        #rects = [r for i, r in enumerate(rects) if not isinstance(r, Rect) or merges[i] is None]

        return merged

    def merge_rect(self, i, rect, merges, growth, rects, direction):
        if isinstance(growth[direction], list):
            for j in growth[direction]:
                if merges[j] is not None:
                    j = merges[j]
                #if not isinstance(rects[j], Rect) or rects[j].width and rects[j].height:
                #rects[j] = Generator.points_in(rects[j]) + Generator.points_in(rect)
                merges[i] = j
                return True
        return False
    def grow_rect(self, i, rect, growth, rects, direction):
        """Tries to grow a rectangle in the specified direction

        Returns whether the growth succeeded"""
        if growth[direction] == True:
            left, top, width, height = rect.x, rect.y, rect.w, rect.h
            if direction == LEFT:
                left -= 1
                width += 1
            elif direction == RIGHT:
                width += 1
            elif direction == DOWN:
                height += 1
            elif direction == UP:
                top -= 1
                height += 1
            new = Rect(left, top, width, height)
            building_collisions = new.collidelistall(rects)
            try:
                building_collisions.remove(i)
            except ValueError:
                pass
            if not (set(Generator.points_in(new)) - self.space) and len(building_collisions) == 0:
                rect.left = left
                rect.width = width
                rect.top = top
                rect.height = height
                #if rect.width >= 8 and rect.height >= 8 and random.randrange(5) == 0:
                #    growth[direction] = False
                return True
            else:
                if building_collisions:
                    # If we collided with a building, make a note.
                    growth[direction] = building_collisions
                else:
                    growth[direction] = False

        return False

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
            nearest[p] |= set(self.points_in(rect))

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
        self.level = level
        self.size = 80
        self.width = random.randint(self.size*0.4, self.size*0.6) * 2
        self.height = random.randint(self.size*0.4, self.size*0.6) * 2
        self.orientation = random.randint(0,3)
        self.turretsize = random.randint(6,10)
        self.gatesize = random.randint(1,4)
        self.wallwidth = random.randint(2,3)
        self.turret_project = random.randint(2,4)
        self.gatehouse_project = random.randint(0,4)
        if self.gatesize % 2 == 1:
            self.width -= 1

    def generate(self):
        # Fill with grass
        self.fill_rect(-self.width/2-self.turret_project-10,
                               -self.turret_project-10,
                               self.width+2*(self.turret_project+10),
                               self.height+2*(self.turret_project+10), grass)
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
        k_w = (random.randint(int(self.width*0.3), int(self.width*0.5))/2)*2 + k_gs
        k_h = random.randint(int(self.height*0.3), int(self.height*0.5))

        keep_style = random.choice(KEEP_STYLES)
        if keep_style == KEEP_CENTRE:
            k_x, k_y = 0, (self.height-k_h)/2
        elif keep_style == KEEP_SIDE:
            side = random.choice((-1, 1))
            k_x, k_y = (self.width-k_w)/2*side, (self.height-k_h)


        # Draw keep
        self.level.translate(k_x, k_y)

        self.fourwalls(k_w, k_h,
                       self.turretsize,
                       self.wallwidth+1,
                       self.turret_project,
                       k_gs, 0, 4)

        self.level.translate(-k_x, -k_y)

        path_to_keep = self.get_path(0, 1, k_x, k_y, self.gatesize, k_gs)
        for p in path_to_keep:
            self.level.set_terrain(p, path)

        # Calculate valid space for buildings
        interior = Rect(-self.width/2+self.wallwidth+1, self.wallwidth,
                        self.width-self.wallwidth*2-1, self.height-self.wallwidth*2)
        space = set(self.points_in(interior))

        tower = Rect(-self.width/2+1-self.turret_project, -self.turret_project,
                     self.turretsize, self.turretsize)
        space -= set(self.points_in(tower))
        tower = Rect(self.width/2-self.turretsize+self.turret_project, -self.turret_project,
                     self.turretsize, self.turretsize)
        space -= set(self.points_in(tower))
        tower = Rect(-self.width/2+1-self.turret_project, self.height-self.turretsize+self.turret_project,
                     self.turretsize, self.turretsize)
        space -= set(self.points_in(tower))
        tower = Rect(self.width/2-self.turretsize+self.turret_project,
                     self.height-self.turretsize+self.turret_project,
                     self.turretsize, self.turretsize)
        space -= set(self.points_in(tower))

        self.expand(path_to_keep, 2)
        space -= set(path_to_keep)

        margin = 6
        if keep_style == KEEP_CENTRE:
            around_keep = Rect(-k_w/2-(self.wallwidth+margin), self.height/2-k_h/2-self.wallwidth-margin,
                               k_w+(self.wallwidth+margin)*2, k_h+(self.wallwidth+margin)*2)
            space -= set(self.points_in(around_keep))
        elif keep_style == KEEP_SIDE:
            if side == -1:
                left = -self.width/2+self.wallwidth
                width = k_w + margin
            else:
                left = self.width/2-self.wallwidth-k_w-margin
                width = k_w + margin
            around_keep = Rect(left, self.height/2-self.wallwidth-margin,
                               width, self.height)
            space -= set(self.points_in(around_keep))

        # Create buildings
        graph = BuildingGraph(Rect(-self.width/2+self.wallwidth, self.wallwidth,
                                   self.width-2*self.wallwidth, self.height-2*self.wallwidth), space, 20, 1)

        # Draw building walls
        for border in graph.borders:
            #self.draw_points(self.points_in_multiple(border), grass)
            self.draw_points(self.get_outlines(border), wall)

    def fourwalls(self, width, height, turretsize, wallwidth, turret_project, gatesize, gatehouse_project, turrets):
        turret_inner = turretsize - turret_project

        self.fill_rect(-width/2+1, 1, width-1, height-1, floor)
        # Front wall
        self.fill_rect(-width/2+(turret_inner), 0,
                         width-2*(turret_inner), wallwidth, wall)
        self.fill_rect(-gatesize/2+1, 0, gatesize, wallwidth, floor)

        # Front left turret
        self.level.translate(-((width+1)/2), 0)
        self.tower(-turret_project+1, -turret_project, turretsize)
        # Left wall
        self.fill_rect(1, turret_inner, wallwidth, height-2*turret_inner, wall)
        # Front right turret
        self.level.translate(width+1, 0)
        self.tower(-turret_inner-1, -turret_project, turretsize)
        # Right wall
        self.fill_rect(-1-wallwidth, turret_inner, wallwidth, height-2*turret_inner, wall)

        # Back right turret
        self.level.translate(0, height)
        self.tower(-turret_inner-1, -turret_inner, turretsize)
        # Back left turret
        self.level.translate(-width-1, 0)
        self.tower(-turret_project+1, -turret_inner, turretsize)

        # Back wall
        self.fill_rect(1+turret_inner, -wallwidth, width-2*turret_inner-1, wallwidth, wall)

        self.level.translate((width+1)/2, -height)

        gh_width = 2+2*wallwidth+gatesize*3
        gh_width += 2 if gatesize == 1 else 0
        self.gatehouse(gatehouse_project, gh_width, gatesize)

    def tower(self, x, y, size):
        self.fill_rect(x, y, size, size, wall)
        self.fill_rect(x+1, y+1, size-2, size-2, floor)

    def gatehouse(self, projection, width, gatesize):
        inner = (width-gatesize)/2+1 - self.wallwidth

        # Front walls
        self.fill_rect(gatesize/2+1, -projection,
                         width/2-gatesize/2, self.wallwidth, wall)
        self.fill_rect(-width/2+1, -projection,
                         width/2-gatesize/2, self.wallwidth, wall)
        # Outer walls
        self.fill_rect(width/2-self.wallwidth+1, -projection,
                         self.wallwidth, projection, wall)
        self.fill_rect(-width/2+1, -projection,
                         self.wallwidth, projection, wall)

        # Inner walls
        self.fill_rect(gatesize/2+1, -projection,
                         self.wallwidth, projection, wall)
        self.fill_rect(-gatesize/2-self.wallwidth+1, -projection,
                         self.wallwidth, projection, wall)
        gateheight = max(0, self.wallwidth-projection+1)
        self.draw_line(gatesize/2+1, gateheight-1,
                       gatesize/2+self.wallwidth, gateheight-1, floor)
        self.draw_line(-gatesize/2, gateheight-1,
                       -gatesize/2-self.wallwidth+1, gateheight-1, floor)
        self.level.set_terrain((-gatesize/2, gateheight-1), window)
        self.level.set_terrain((gatesize/2+1, gateheight-1), window)
        for p in self.get_line(-gatesize/2+1, gateheight, gatesize/2, gateheight):
            Door(p, level=self.level)
        self.level.set_terrain((width/2-self.wallwidth+1, gateheight-1), wall)
        self.level.set_terrain((-width/2+self.wallwidth, gateheight-1), wall)

        # Part inside main castle
        height = 10
        self.fill_rect(-width/2+self.wallwidth, gateheight,
                         inner, height-projection-gateheight, wall)
        self.fill_rect(-width/2+self.wallwidth+1, gateheight-1,
                         inner-2, height-projection-gateheight, floor)
        self.fill_rect(gatesize/2+1, gateheight,
                         inner, height-projection-gateheight, wall)
        self.fill_rect(gatesize/2+2, gateheight-1,
                         inner-2, height-projection-gateheight, floor)

    def get_path(self, x1, y1, x2, y2, w1, w2):
        path = []
        for offset in range(-w1/2+1, 1+w1/2):
            path += self.get_line(x1+offset, y1, x1+offset, (y1+y2)/2)
            path += self.get_line(x1, (y1+y2)/2+offset, (x1+x2)/2, (y1+y2)/2+offset)
        for offset in range(-w2/2+1, 1+w2/2):
            path += self.get_line((x1+x2)/2, (y1+y2)/2+offset, x2, (y1+y2)/2+offset)
            path += self.get_line(x2+offset, (y1+y2)/2, x2+offset, y2)

        return set(path)
