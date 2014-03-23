### The World knows about the map, terrain, objects, etc.

import sys
import pygame

from renderer import Renderer
from map import Map

class World:
	def __init__(self, player):
		self.objects = []
		self.player = player
		self.add_object(player)

		self.quitting = False
		self.interpreter = CommandInterpreter(self)
		self.map = Map()
		self.renderer = Renderer()
		self.clock = pygame.time.Clock()

	def add_object(self, obj):
		if obj in self.objects:
			return

		self.objects.append(obj)
		obj.world = self
	
	def remove_object(self, obj):
		if obj not in self.objects:
			return

		self.objects.remove(obj)
		obj.destroy()
	
	def get_objects_at(self, location):
		for obj in self.objects:
			if obj.location == location:
				yield obj

	def can_move_to(self, obj, location):
		return not self.map[location].block_move
	
	def main_loop(self, screen):
		while not self.quitting:
			self.clock.tick(15)
			self.process_events()
			self.update()
			self.renderer.render(screen, self.map, self.objects)
			pygame.display.flip()
	
	def process_events(self):
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				self.quitting = True
				return

			if e.type == pygame.KEYDOWN:
				newloc = [self.player.location[0], self.player.location[1]]
				if e.key == pygame.K_LEFT:
					newloc[0] -= 1
				if e.key == pygame.K_RIGHT:
					newloc[0] += 1
				if e.key == pygame.K_UP:
					newloc[1] -= 1
				if e.key == pygame.K_DOWN:
					newloc[1] += 1

				if e.key == pygame.K_COMMA:
					for obj in self.get_objects_at(self.player.location):
						if self.player.add(obj):
							self.describe('You pick up %s' % obj.indefinite())

				if e.key == pygame.K_d:
					for obj in self.player.contained:
						if self.player.remove(obj):
							self.describe('You drop %s' % obj.indefinite())

				if self.can_move_to(self.player, newloc):
					self.player.move(newloc)

	def process_input(self):
		input = raw_input('> ')
		#self.interpreter.interpret(input)
		if input == 'l':
			self.player.location[0] += 1
	
	def describe(self, text):
		print text

	def update(self):
		pass

class CommandInterpreter:
	def __init__(self, world):
		self.world = world
	
	def interpret(self, cmd):
		if cmd == 'look':
			self.cmd_look()
		elif cmd == 'quit':
			self.cmd_quit()
		elif cmd.split()[0] == 'take':
			self.cmd_take(cmd.split()[1])
		elif cmd == 'inventory':
			self.cmd_inventory()
		else:
			self.nonsense(cmd)

	def nonsense(self, cmd):
		self.world.describe("I didn't understand '%s'." % cmd)
	
	def cmd_inventory(self):
		if not self.world.player.contained:
			self.world.describe("You aren't carrying anything.")
			return

		self.world.describe('\n'.join(["You are carrying:"] + [str(x) for x in self.world.player.contained]))

	def cmd_take(self, name):
		objs = self.world.get_objects_in(name, self.world.player.location)
		if not objs:
			self.world.describe("You can't get %s" % name)

		for obj in objs:
			self.world.player.add(obj)
		self.world.describe('You take %s.' % name)

	def cmd_look(self):
		self.world.describe(self.world.player.location.describe())
	
	def cmd_quit(self):
		self.world.quitting = True
