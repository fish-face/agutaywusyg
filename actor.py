### Base class for the player and NPCs

from object import GameObject

class Actor(GameObject):
	def __init__(self, name, description='', location=None, *args, **kwargs):
		self.knowledge = None
		self.relationships = None
		GameObject.__init__(self, name, description, location, *args, **kwargs)
	
	def ask(self, other, topic):
		"""Ask another Actor about topic"""
		return "Hello, World!"

class Player(Actor):
	def __init__(self, *args, **kwargs):
		kwargs['char'] = '@'
		Actor.__init__(self, *args, **kwargs)

