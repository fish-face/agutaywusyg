from level import *

import random

grass = TerrainInfo('v', 'road', (0,1), False, False)
road = TerrainInfo('.', 'road', (0,1), False, False)
door = TerrainInfo('+', 'door', (0,1), False, False)
tree = TerrainInfo('T', 'tree', (0,1), False, False)

class VillageLevel(Level):
	size = 120
	road_width = 2
	house_size = 7
	house_chance = 0.5
	num_roads = 3

	def setup(self):
		Level.setup(self)

		for y in xrange(self.size):
			self.map.append([])
			for x in xrange(self.size):
				self.map[y].append([grass])

		offsetx = random.randint(-4,4)
		offsety = random.randint(-4,4)
		self.centre = (self.size / 2 + offsetx, self.size / 2 + offsety)

		x1 = self.centre[0]
		y1 = self.centre[1]

		self.occupied = set()

		for r in xrange(self.num_roads):
			length = random.randint(20,30)
			d = random.randrange(4)
			x2, y2 = self.coords_in_dir(x1, y1, d, length)
			x1, y1 = self.make_road(x1, y1, x2, y2, d)

		self.compute_height()
	
	def make_road(self, x1, y1, x2, y2, d):
		path = self.get_line(x1, y1, x2, y2)

		for x, y in path:
			width = random.randrange(7,15)
			depth = random.randrange(7,15)
			self.make_house(x, y, (d+1) % 4, width, depth)

			self.set_terrain((x,y), road)
			self.occupied |= set(((x,y)))

		return random.choice(path)

	def make_house(self, x1, y1, direction, width, depth):
		if random.random() > self.house_chance:
			return False

		x2, y2 = self.coords_in_dir(x1, y1, direction, depth)
		x2, y2 = self.coords_in_dir(x2, y2, (direction-1)%4, depth)
		x1, y1 = self.coords_in_dir(x1, y1, direction, 2)

		door_x, door_y = self.coords_in_dir(x1, y1, (direction-1)%4, width/2)

		points = self.get_square(x1, y1, x2, y2)
		if set(points) & self.occupied:
			return False

		self.draw_square(x1, y1, x2, y2, floor)
		self.draw_line(x1, y1, x2, y1, wall)
		self.draw_line(x2, y1, x2, y2, wall)
		self.draw_line(x2, y2, x1, y2, wall)
		self.draw_line(x1, y2, x1, y1, wall)
		self.set_terrain((door_x, door_y), door)

		self.occupied |= set(self.get_square(x1, y1, x2, y2))

		return True
