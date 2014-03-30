### Base class for the player and NPCs

import random

from object import GameObject

class Actor(GameObject):
	def __init__(self, name, description='', location=None, *args, **kwargs):
		GameObject.__init__(self, name, description, location, *args, **kwargs)

		self.knowledge = []
		self.relationships = None
		self.hp = 1
		self.block_move = True
	
	def ask(self, other, topic):
		"""Ask another Actor about topic"""
		topic = random.choice([fact.subj.name for fact in self.knowledge] + ['hello'])
		if topic == 'hello':
			return 'Hello, my name is ' + self.name
		else:
			facts = [fact for fact in self.knowledge if fact.subj.name == topic]
			if facts:
				return random.choice(facts)
			else:
				return "I don't know anything about '%s.'" % topic


	def hit(self, other, damage):
		"""I was hit by other for some damage"""
		self.hp -= damage
		if self.hp <= 0:
			self.die(other)

	def die(self, killer):
		"""I died, somehow."""
		self.world.describe('%s killed %s!' % (killer.definite(), self.definite()))
		self.destroy()

class Player(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, char='@', *args, **kwargs)
	
	def definite(self):
		return self.name

	def indefinite(self):
		return self.name

class Rodney(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, name='Wizard of Yendor', char='W', *args, **kwargs)
		self.flags['hostile'] = True

class Villager(Actor):
	def __init__(self, *args, **kwargs):
		Actor.__init__(self, char='P', *args, **kwargs)
