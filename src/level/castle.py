import random

from level import TerrainInfo, Region, floor, wall
from generator import Generator
from objects import Door
from constants import UP, DOWN, LEFT, RIGHT

grass = TerrainInfo('v', 'grass', (3,0), False, False)
window = TerrainInfo('o', 'window', (0,1), True, False)

GH_PROJECT = 0

KEEP_CENTRE = 0
KEEP_SIDE = 1
KEEP_EXTERNAL = 2
KEEP_STYLES = (0,1)

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

    def generate(self):
        self.level.draw_square(-self.width/2-self.turret_project-10,
                               -self.turret_project-10,
                               self.width/2-self.turret_project+11,
                               self.height+self.turret_project+10, grass)
        self.fourwalls(self.width,
                       self.height,
                       self.turretsize,
                       self.wallwidth,
                       self.turret_project,
                       self.gatesize,
                       self.gatehouse_project,
                       4)

        k_w = random.randint(int(self.width*0.3), int(self.width*0.5))
        k_h = random.randint(int(self.height*0.3), int(self.height*0.5))
        k_gs = (self.gatesize + 2) % 4 if self.gatesize != 2 else 4

        keep_style = random.choice(KEEP_STYLES)
        if keep_style == KEEP_CENTRE:
            self.level.translate(0, (self.height-k_h)/2)
        elif keep_style == KEEP_SIDE:
            side = random.choice((-1, 1))
            self.level.translate((self.width-k_w)/2*side, (self.height-k_h))

        self.fourwalls(k_w, k_h,
                       self.turretsize,
                       self.wallwidth+1,
                       self.turret_project,
                       k_gs, 0, 4)

    def fourwalls(self, width, height, turretsize, wallwidth, turret_project, gatesize, gatehouse_project, turrets):
        turret_inner = turretsize - turret_project

        if gatesize % 2 == 1:
            width -= 1

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
