from level import Level, TerrainInfo

import random

grass = TerrainInfo('v', 'road', (0,1), False, False)
road = TerrainInfo('.', 'road', (0,1), False, False)

class VillageLevel(Level):
	size = 30
	road_width = 2
	house_size = 7
	num_roads = 10

	def setup(self):
		self.map = []
		for y in xrange(self.size):
			self.map.append([])
			for x in xrange(self.size):
				self.map[y].append([grass])

		offsetx = random.randint(-10,10)
		offsety = random.randint(-10,10)
		self.centre = (self.size / 2 + offsetx, self.size / 2 + offsety)

		x1 = self.centre[0]
		y1 = self.centre[1]

		for r in xrange(self.num_roads):
			length = random.randint(10,20)
			d = random.randrange(4)
			if d == 0:
				x2 = x1
				y2 = y1 + length
			elif d == 1:
				x2 = x1
				y2 = y1 - length
			elif d == 2:
				x2 = x1 + length
				y2 = y1
			elif d == 3:
				x2 = x1 - length
				y2 = y1
			path = self.get_line(x1, y1, x2, y2)
			for p in path:
				self.set_terrain(p, road)

			x1, y1 = random.choice(path)

		self.compute_height()
