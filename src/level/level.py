# encoding=utf-8

### Levels define the terrain making up an area

from constants import *

TEST_LEVEL = (
    "##########",
    "#....#...#",
    "#....#...#",
    "#.####...#",
    "#........#",
    "#........#",
    "##########")

class TerrainInfo:
	def __init__(self, char, name, index, block_move, block_sight, **kwargs):
		self.char = char
		self.name = name
		self.tileindex = index
		self.block_move = block_move
		self.block_sight = block_sight

		for key in kwargs:
			setattr(self, key, kwargs[key])

wall = TerrainInfo('#', 'wall', (0,0), True, True)
floor = TerrainInfo(u'·', 'floor', (10,10), False, False)

TERRAINS = {'#' : wall, '.' : floor}

class Level:
	def __init__(self, world):
		self.world = world

		self.terraintypes = TERRAINS
		self.objects = []
		self.map = []
		self.regions = []

		self.set_cursor(0,0)
		self.setup()

	def setup(self, width, height, terrain=floor):
		for obj in self.objects[:]:
			if obj.location:
				obj.destroy()

		self.map = []
		for y in xrange(height):
			self.map.append([])
			for x in xrange(width):
				self.map[-1].append([terrain])

		self.width = width
		self.height = height

	def set_cursor(self, x, y):
		"""Set the level's origin; all terrain-drawing will be translated by this amount"""
		self.x = x
		self.y = y

	def translate(self, x, y):
		"""Like set_cursor but relative"""
		self.x += x
		self.y += y

	def set_terrain(self, p, terrain):
		x = p[0] + self.x
		y = p[1] + self.y

		if x < 0 or y < 0 or x >= self.width or y >= self.height:
			return
		if self.map[y][x]:
			self.map[y][x][0] = terrain
		else:
			self.map[y][x] = [terrain]

		#TODO: Nothing specifies that there must be exactly one terrain
		#      per tile, or even where it is in the tile's list.

	def draw_line(self, x1, y1, x2, y2, terrain):
		for p in self.get_line(x1, y1, x2, y2):
			self.set_terrain(p, terrain)

	def get_line(self, x1, y1, x2, y2):
		points = []
		issteep = abs(y2-y1) > abs(x2-x1)
		if issteep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2
		rev = False
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			rev = True
		deltax = x2 - x1
		deltay = abs(y2-y1)
		error = int(deltax / 2)
		y = y1
		ystep = None
		if y1 < y2:
			ystep = 1
		else:
			ystep = -1
		for x in range(x1, x2 + 1):
			if issteep:
				points.append((y, x))
			else:
				points.append((x, y))
			error -= deltay
			if error < 0:
				y += ystep
				error += deltax
		# Reverse the list if the coordinates were reversed
		if rev:
			points.reverse()
		return points

	def get_square(self, x1, y1, x2, y2):
		"""Get all points in the described rectangle, inclusive"""
		if y1 > y2:
			y1, y2 = y2, y1
		if x1 > x2:
			x1, x2 = x2, x1
		return [(x,y) for x in xrange(x1,x2+1) for y in xrange(y1,y2+1)]

	def draw_square(self, x1, y1, x2, y2, terrain):
		"""Draw a filled rectangle with the given coordinates, inclusive"""
		for p in self.get_square(x1, y1, x2, y2):
			self.set_terrain(p, terrain)

	def is_connected(self, points):
		if not points:
			return False
		connected = []
		self.get_flood(points[0][0], points[0][1], set(points), connected)
		if len(set(connected)) == len(set(points)):
			return True
		else:
			return False

	def get_flood(self, x, y, points, connected):
		if (x,y) in points and (x,y) not in connected:
			connected.append((x,y))
		else:
			return

		self.get_flood(x+1, y, points, connected)
		self.get_flood(x-1, y, points, connected)
		self.get_flood(x, y+1, points, connected)
		self.get_flood(x, y-1, points, connected)

	def coords_in_dir(self, x, y, d, l):
		"""Return coordinates offset by l in cardinal direction d"""
		if d == RIGHT:
			return (x + l, y)
		elif d == UP:
			return (x, y - l)
		elif d == LEFT:
			return (x - l, y)
		elif d == DOWN:
			return (x, y + l)

	def add_object(self, obj):
		if obj in self.objects:
			return

		self.objects.append(obj)
		#Translate by our cursor coords - this should only happen during level generation.
		if obj.location:
			x, y = obj.location
			obj.location = (x+self.x, y+self.y)
			self[obj.location].append(obj)

		obj.level = self
		#TODO: Is there a better way of letting the object do world-things??
		obj.world = self.world

	def remove_object(self, obj):
		"""Should only be called from obj.destroy()"""
		if obj not in self.objects:
			return

		self.objects.remove(obj)
		self.move_object(obj, None)

	def move_object(self, obj, location):
		if obj.location:
			self[obj.location].remove(obj)
		if location:
			self[location].append(obj)

	def get_tile(self, x, y):
		try:
			#return self.terraintypes[self.terrain[y][x]]
			return self.map[y][x]
		except (KeyError, IndexError):
			return None

	def get_tiles(self):
		for y in range(self.height):
			for x in range(self.width):
				yield (x, y, self.map[y][x])

	def __getitem__(self, location):
		return self.get_tile(location[0], location[1]) if location else None


class Region:
	def __init__(self, name, level, points):
		self.name = name
		self.level = level
		self.points = points

	def __in__(self, p):
		return p in self.points

from object import *
from actor import *
from village import *

class TestLevel(Level):
	def setup(self):
		Level.setup(self, 200, 200)

		self.set_cursor(100,100)
		VillageGenerator(self).generate()

		self.add_object(GameObject('apple', 'A tasty apple', (1,2), char='%'))
		amulet = GameObject('Amulet of Yendor', 'Pretty important', char='"')

		house = random.choice(self.regions)
		pos = random.choice(house.points)
		rodney = Rodney(location=pos)
		self.add_object(amulet)
		rodney.add(amulet)
		self.add_object(rodney)

		self.set_cursor(0,0)
