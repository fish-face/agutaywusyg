from level import *

import random

grass = TerrainInfo('v', 'road', (0,1), False, False)
road = TerrainInfo('.', 'road', (0,1), False, False)
door = TerrainInfo('+', 'door', (0,1), False, False)
tree = TerrainInfo('T', 'tree', (0,1), False, False)

class VillageLevel(Level):
	size = 80
	road_width = 2
	house_size = 9
	road_length = house_size*2
	house_chance = 0.5
	branchiness = 0.8
	num_roads = size/house_size

	def setup(self):
		Level.setup(self)

		for y in xrange(self.size):
			self.map.append([])
			for x in xrange(self.size):
				self.map[y].append([grass])

		#offsetx = random.randint(-4,4)
		#offsety = random.randint(-4,4)
		#self.centre = (self.size / 2 + offsetx, self.size / 2 + offsety)

		x1 = self.size/2
		y1 = self.size/2

		self.occupied = set()
		self.roads = []
		self.roads_h = set()
		self.roads_v = set()

		self.make_roads(x1, y1, self.num_roads)

		#Put houses next to roads whereever possible
		width = self.house_size + random.randint(-3,3)
		depth = self.house_size + random.randint(-3,3)
		for x, y in self.roads:
			#Don't change size every time
			if random.random() < 0.1:
				width = self.house_size + random.randint(-3,3)
			if random.random() < 0.1:
				depth = self.house_size + random.randint(-3,3)
			for d in range(4):
				self.make_house(x, y, d, width, depth)

		self.compute_height()
	
	def make_roads(self, x1, y1, n):
		if n > 0:
			tries = 0
			l = self.road_length + random.randint(-4,self.road_length)
			d = random.randrange(4)
			success = False
			#Try to draw a road in all 4 directions, twice each.
			#This will fail if we try to go parallel to another nearby road or
			#if we go out-of-bounds. To maximise chances of success we shorten
			#the attempted road each time we fail.
			while tries < 8:
				x2, y2 = self.coords_in_dir(x1, y1, d, l)
				if not self.make_road(x1, y1, x2, y2):
					tries += 1
					if l > self.road_length:
						l = int(l * .9)
					d = (d+1) % 4
					x2, y2 = x1, y1
				else:
					success = True
					break

			#Maybe branch. Move away from the tip of this road to avoid the
			#branches being too close and parallel.
			if random.random() < self.branchiness:
				x2, y2 = self.coords_in_dir(x2, y2, (d+1)%4, 1)
				self.make_roads(x2, y2, n/2)
				x2, y2 = self.coords_in_dir(x2, y2, (d-1)%4, 2)
				self.make_roads(x2, y2, n/2)
			else:
				self.make_roads(x2, y2, n-1)

		return n

	def make_road(self, x1, y1, x2, y2):
		path = self.get_line(x1, y1, x2, y2)

		#Don't go out of bounds
		if x2 < 0 or x2 > self.size - 1 or y2 < 0 or y2 > self.size - 1:
			return False

		#Don't go next to other roads (this looks dumb)
		horizontal = (x1 != x2)
		if horizontal and set(path) & self.roads_h:
			return False
		elif not horizontal and set(path) & self.roads_v:
			return False

		#Draw the road
		for x, y in path:
			self.set_terrain((x,y), road)
			self.occupied |= set(((x,y),))

		#These sets are how we know whether we're going parallel to another road

		if horizontal:
			self.roads_h |= set(self.get_square(x1, y1+self.house_size, x2, y1-self.house_size))
		else:
			self.roads_v |= set(self.get_square(x1+self.house_size, y1, x1-self.house_size, y2))

		self.roads += path

		return True

	def make_house(self, x1, y1, direction, width, depth):
		if random.random() > self.house_chance:
			return False

		x1, y1 = self.coords_in_dir(x1, y1, direction, 2)
		x1, y1 = self.coords_in_dir(x1, y1, (direction+1)%4, width/2)
		x2, y2 = self.coords_in_dir(x1, y1, direction, depth)
		x2, y2 = self.coords_in_dir(x2, y2, (direction-1)%4, width)

		if x2 < 0 or x2 >= self.size or y2 < 0 or y2 >= self.size:
			return False

		door_x, door_y = self.coords_in_dir(x1, y1, (direction-1)%4, width/2)

		points = self.get_square(x1, y1, x2, y2)
		if set(points) & self.occupied:
			return False

		if x2 < x1:
			x1, x2 = x2, x1
		if y2 < y1:
			y1, y2 = y2, y1

		self.draw_square(x1, y1, x2, y2, floor)
		self.draw_line(x1, y1, x2, y1, wall)
		self.draw_line(x2, y1, x2, y2, wall)
		self.draw_line(x2, y2, x1, y2, wall)
		self.draw_line(x1, y2, x1, y1, wall)
		self.set_terrain((door_x, door_y), door)
		self.set_terrain(self.coords_in_dir(door_x, door_y, direction, -1), road)

		self.regions.append(Region('Someone\'s House', self, self.get_square(x1+1, y1+1, x2-1, y2-1)))

		self.occupied |= set(self.get_square(x1, y1, x2, y2))

		return True
