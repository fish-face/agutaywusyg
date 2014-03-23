#encoding=utf-8
### Maps define the terrain making up an area

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

class Map:
	def __init__(self):
		self.terraintypes = TERRAINS
		self.terrain = TEST_LEVEL
		self.height = len(self.terrain)
		self.width = len(self.terrain[0])

	def get_tile(self, x, y):
		try:
			return self.terraintypes[self.terrain[y][x]]
		except (KeyError, IndexError):
			return None
	
	def get_tiles(self):
		for y in range(self.height):
			for x in range(self.width):
				yield (x, y, self.get_tile(x, y))
	
	def __getitem__(self, location):
		return self.get_tile(location[0], location[1])
