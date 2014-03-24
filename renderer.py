### Renders a map to a pygame surface

import pygame

class Renderer:
	def __init__(self):
		self.tile_width = 24
		self.tile_height = 24
		#self.tiles = Tileset("/home/fish/Pictures/M_BISON_YESSSSSSS.jpg", 24, 24)
		self.tiles = AsciiTiles('Deja Vu Sans Mono')

	def render(self, surface, map, objects):
		surface.fill((0,0,0))
		#TODO: Passing all those lists in here sucks, especially for extensions
		for (x, y, tile) in map.get_tiles():
			tile_image = self.tiles[tile]
			surface.blit(tile_image, (x*self.tile_width, y*self.tile_height))

		#TODO: Render order!
		for obj in objects:
			if not obj.location: continue

			x, y = obj.location
			obj_image = self.tiles[obj]
			surface.blit(obj_image, (x*self.tile_width, y*self.tile_height))

class Tileset:
	def __init__(self, filename, width, height):
		self.load_tile_table(filename, width, height)

	def load_tile_table(self, filename, width, height):
		image = pygame.image.load(filename).convert()
		image_width, image_height = image.get_size()
		tile_table = []
		for tile_x in range(0, image_width/width):
			line = []
			tile_table.append(line)
			for tile_y in range(0, image_height/height):
				rect = (tile_x*width, tile_y*height, width, height)
				line.append(image.subsurface(rect))
		self.tile_table = tile_table
	
	def __getitem__(self, thing):
		return self.tile_table[thing.tileindex[0]][thing.tileindex[0]]

class AsciiTiles(Tileset):
	def __init__(self, font):
		self.font = pygame.font.SysFont(font, 21)
		self.cache = {}

	def __getitem__(self, thing):
		char = getattr(thing, 'char', '?')
		if char not in self.cache:
			self.cache[char] = self.font.render(char, True, (255,255,255))

		return self.cache[char]
