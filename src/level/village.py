from level import *

import random

grass = TerrainInfo('v', 'road', (0,1), False, False)
road = TerrainInfo('.', 'road', (0,1), False, False)
door = TerrainInfo('+', 'door', (0,1), False, False)
tree = TerrainInfo('T', 'tree', (0,1), False, False)

class VillageLevel(Level):
	size = 40
	road_width = 2
	house_size = 10
	house_chance = 0.5
	num_roads = (size/(house_size*2))**2

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
		self.roads = []

		road_length = self.house_size * 2

		for y in xrange(0,self.size,road_length):
			x1 = 0
			y1 = y
			for x in xrange(0,self.size,road_length):
				x2 = x1 + road_length + random.randint(-1,1)
				y2 = max(0,y1 + random.randint(-1,1))
				self.make_road(x1,y1,x2,y2)
				x1 = x2
				y1 = y2
		for x in xrange(0,self.size,road_length):
			x1 = x
			y1 = 0
			for y in xrange(0,self.size,road_length):
				x2 = max(0,x1 + random.randint(-1,1))
				y2 = y1 + road_length + random.randint(-1,1)
				self.make_road(x1,y1,x2,y2)
				x1 = x2
				y1 = y2

		#for y in xrange(0,self.size,road_length):
		#	for x1 in xrange(0,self.size,road_length):
		#		y1 = y + random.randint(-1,2)
		#		x2 = x1 + road_length
		#		self.make_road(x1,y1,x2,y1)

		tries = 0
		untested = self.roads[:]
		test_net = [p for r in self.roads for p in r]
		print self.is_connected(test_net)
		while len(self.roads) > self.num_roads and tries < (self.size/(self.house_size+5))**2 and untested:
			del_road = random.choice(untested)
			test_net = [p for r in self.roads for p in r if r != del_road]
			if self.is_connected(test_net):
				self.roads.remove(del_road)
			untested.remove(del_road)
			tries += 1

		for p in (p for road in self.roads for p in road):
			self.set_terrain(p, road)

		for x, y in [p for r in self.roads for p in r]:
			width = self.house_size + random.randint(-3,3)
			depth = self.house_size + random.randint(-3,3)
			for d in range(4):
				self.make_house(x, y, d, width, depth)

		#for r in xrange(self.num_roads):
		#	length = random.randint(20,30)
		#	d = random.randrange(4)
		#	x2, y2 = self.coords_in_dir(x1, y1, d, length)
		#	done = self.make_road(x1, y1, x2, y2, d)

		#	x1, x2 = random.choice(self.roads)

		self.compute_height()
	
	def make_road(self, x1, y1, x2, y2):
		path = self.get_line(x1, y1, x2, y2)
		#if set(path) & self.occupied:
		#	return False

		for x, y in path:
			#self.set_terrain((x,y), road)
			self.occupied |= set(((x,y),))

		self.roads.append(path)
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

		self.draw_square(x1, y1, x2, y2, floor)
		self.draw_line(x1, y1, x2, y1, wall)
		self.draw_line(x2, y1, x2, y2, wall)
		self.draw_line(x2, y2, x1, y2, wall)
		self.draw_line(x1, y2, x1, y1, wall)
		self.set_terrain((door_x, door_y), door)
		self.set_terrain(self.coords_in_dir(door_x, door_y, direction, -1), road)

		self.occupied |= set(self.get_square(x1, y1, x2, y2))

		return True
