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
        rects = [Rect(p[0], p[1], 1, 1) for p in self.points]
        growing = [[True, True, True, True] for p in self.points]
        changed = True
        # Expand rectangles around the points we picked
        while changed:
            changed = False
            for i, r in enumerate(rects):
                for d in [UP, DOWN, LEFT, RIGHT]:
                    changed |= self.grow_rect(r, growing[i], rects, d)

        return rects

    def grow_rect(self, rect, growth, rects, direction):
        """Tries to grow a rectangle in the specified direction

        Returns whether the growth succeeded"""
        changed = False
        if growth[direction]:
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
            if not (set(util.points_in(new)) - self.space) and len(new.collidelistall(rects)) == 1:
                rect.left = left
                rect.width = width
                rect.top = top
                rect.height = height
                changed = True
                #if rect.width >= 8 and rect.height >= 8 and random.randrange(5) == 0:
                #    growth[direction] = False
            else:
                growth[direction] = False

        return changed

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
            nearest[p] |= set(util.points_in(rect))

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
        self.level.draw_square(-self.width/2-self.turret_project-10,
                               -self.turret_project-10,
                               self.width/2-self.turret_project+11,
                               self.height+self.turret_project+10, grass)
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
            self.level.translate(0, (self.height-k_h)/2)
        elif keep_style == KEEP_SIDE:
            side = random.choice((-1, 1))
            self.level.translate((self.width-k_w)/2*side, (self.height-k_h))

        # Draw keep
        self.fourwalls(k_w, k_h,
                       self.turretsize,
                       self.wallwidth+1,
                       self.turret_project,
                       k_gs, 0, 4)

        # Calculate valid space for buildings
        interior = Rect(-self.width/2+self.wallwidth+1, self.wallwidth,
                        self.width-self.wallwidth*2, self.height-self.wallwidth*2+1)
        space = set(util.points_in(interior))

        margin = 6
        if keep_style == KEEP_CENTRE:
            self.level.translate(0, -((self.height-k_h)/2))
            around_keep = Rect(-k_w/2-(self.wallwidth+margin), self.height/2-k_h/2-self.wallwidth-margin,
                               k_w+(self.wallwidth+margin)*2, k_h+(self.wallwidth+margin)*2)
            space -= set(util.points_in(around_keep))
        elif keep_style == KEEP_SIDE:
            self.level.translate(-((self.width-k_w)/2*side), -(self.height-k_h))
            if side == -1:
                left = -self.width/2+self.wallwidth
                width = k_w + margin
            else:
                left = self.width/2-self.wallwidth-k_w-margin
                width = k_w + margin
            around_keep = Rect(left, self.height/2-self.wallwidth-margin,
                               width, self.height)
            space -= set(util.points_in(around_keep))

        #for p in space:
        #    self.level.set_terrain(p, grass)

        # Create buildings
        graph = BuildingGraph(Rect(-self.width/2+self.wallwidth, self.wallwidth,
                                   self.width-2*self.wallwidth, self.height-2*self.wallwidth), space, 20, 1)

        # Draw building walls
        for border in graph.borders:
            self.level.draw_line(border.left, border.top,
                                 border.left, border.bottom, wall)
            self.level.draw_line(border.left, border.bottom,
                                 border.right, border.bottom, wall)
            self.level.draw_line(border.right, border.bottom,
                                 border.right, border.top, wall)
            self.level.draw_line(border.right, border.top,
                                 border.left, border.top, wall)

    def fourwalls(self, width, height, turretsize, wallwidth, turret_project, gatesize, gatehouse_project, turrets):
        turret_inner = turretsize - turret_project

        self.level.draw_square(-width/2+1, 1, width/2, height, floor)
        # Front wall
        self.level.draw_square(-width/2+(turret_inner), 0,
                               width/2-(turret_inner)+1, wallwidth-1, wall)
        self.level.draw_square(-gatesize/2+1, 0, gatesize/2, wallwidth-1, floor)

        # Front left turret
        self.level.translate(-((width+1)/2), 0)
        self.tower(-turret_project+1, -turret_project, turretsize)
        # Left wall
        self.level.draw_square(1, turret_inner, wallwidth, height-turret_inner, wall)
        # Front right turret
        self.level.translate(width+1, 0)
        self.tower(-turret_inner-1, -turret_project, turretsize)
        # Right wall
        self.level.draw_square(-1, turret_inner, -wallwidth, height-turret_inner, wall)

        # Back right turret
        self.level.translate(0, height)
        self.tower(-turret_inner-1, -turret_inner, turretsize)
        # Back left turret
        self.level.translate(-width-1, 0)
        self.tower(-turret_project+1, -turret_inner, turretsize)

        # Back wall
        self.level.draw_square(1+turret_inner, 0, width-turret_inner, -wallwidth+1, wall)

        self.level.translate((width+1)/2, -height)

        gh_width = 2+2*wallwidth+gatesize*3
        gh_width += 2 if gatesize == 1 else 0
        self.gatehouse(gatehouse_project, gh_width, gatesize)

    def tower(self, x, y, size):
        self.level.draw_square(x, y, x+size, y+size, wall)
        self.level.draw_square(x+1, y+1, x+size-1, y+size-1, floor)

    def gatehouse(self, projection, width, gatesize):
        #inner = (width-self.gatesize)/2+1 - 2*self.wallwidth

        # Front walls
        self.level.draw_square(gatesize/2+1, -projection,
                               width/2, -projection+self.wallwidth-1, wall)
        self.level.draw_square(-gatesize/2, -projection,
                               -width/2+1, -projection+self.wallwidth-1, wall)
        # Outer walls
        self.level.draw_square(width/2-self.wallwidth+1, -projection,
                               width/2, 0, wall)
        self.level.draw_square(-width/2+1+self.wallwidth-1, -projection,
                               -width/2+1, 0, wall)

        # Inner walls
        self.level.draw_square(gatesize/2+1, -projection,
                               gatesize/2+self.wallwidth, 0, wall)
        self.level.draw_square(-gatesize/2, -projection,
                               -gatesize/2-self.wallwidth+1, 0, wall)
        gateheight = max(0, self.wallwidth-projection+1)
        self.level.draw_line(gatesize/2+1, gateheight-1,
                             gatesize/2+self.wallwidth, gateheight-1, floor)
        self.level.draw_line(-gatesize/2, gateheight-1,
                             -gatesize/2-self.wallwidth+1, gateheight-1, floor)
        self.level.set_terrain((-gatesize/2, gateheight-1), window)
        self.level.set_terrain((gatesize/2+1, gateheight-1), window)
        for p in self.level.get_line(-gatesize/2+1, gateheight, gatesize/2, gateheight):
            door = Door(p, level=self.level)
        self.level.set_terrain((width/2-self.wallwidth+1, gateheight-1), wall)
        self.level.set_terrain((-width/2+self.wallwidth, gateheight-1), wall)

        # Part inside main castle
        height = 10
        self.level.draw_square(-width/2+self.wallwidth, gateheight,
                               -gatesize/2, height-projection, wall)
        self.level.draw_square(-width/2+self.wallwidth+1, gateheight-1,
                               -gatesize/2-1, height-projection-1, floor)
        self.level.draw_square(width/2-self.wallwidth+1, gateheight,
                               gatesize/2+1, height-projection, wall)
        self.level.draw_square(width/2-self.wallwidth, gateheight-1,
                               gatesize/2+2, height-projection-1, floor)
