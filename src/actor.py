### Base class for the player and NPCs

from object import GameObject

class Actor(GameObject):
	def __init__(self, name, description='', location=None, *args, **kwargs):
		GameObject.__init__(self, name, description, location, *args, **kwargs)

		self.knowledge = None
		self.relationships = None
		self.hp = 1
		self.block_move = True
	
	def ask(self, other, topic):
		"""Ask another Actor about topic"""
		return "Hello, World!"

	def hit(self, other, damage):
		"""I was hit by other for some damage"""
		self.hp -= damage
		if self.hp <= 0:
			self.die(other)

	def die(self, killer):
		"""I died, somehow."""
		self.world.describe('%s kills %s!' % (killer.definite(), self.definite()))
		self.destroy()

class Player(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, char='@', *args, **kwargs)

class Rodney(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, name='Wizard of Yendor', char='W', *args, **kwargs)
		self.flags['hostile'] = True

class Villager(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, char='P', *args, **kwargs)
