### Contains definition of Game Objects

from ai import predicate

class GameObject(object):
	"""An object in the game world"""
	def __init__(self, name, description='', location=None, char='?'):
		"""Create a new GameObject with the given name, description and location."""
		self.name = name
		self.description = description
		self._location = location
		self.level = None
		self.container = None
		self.contained = []
		self.destroyed = False
		self.flags = {}
		#TODO: There should probably be a better way of doing flags

		self.tileindex = (0,0)
		self.char = char
		self.block_sight = False
		self.block_move = False

		self.moved_cbs = []
		self.added_cbs = []
		self.removed_cbs = []
		self.destroyed_cbs = []

		if self.name[0].lower() in 'aeiou':
			self.indef_article = 'an'
		else:
			self.indef_article = 'a'
		self.def_article = 'the'
		self.prefer_definite = False

		self.setup_facts()

	#TODO: something something locations vs containers
	#TODO: No, really???

	@property
	def location(self):
		return self._location

	@location.setter
	def location(self, value):
		#TODO: Moving between levels. (Don't forget to move contained objects)
		self.level.move_object(self, value)

		self._location = value
		self.location_fact = predicate.In(self, self.location)

		self.on_moved()

	def setup_facts(self):
		self.location_fact = predicate.In(self, self.location)
	
	@property
	def facts(self):
		return [self.location_fact]

	def indefinite(self):
		"""Name of the object with indefinite article"""
		return '%s %s' % (self.indef_article, self.name)

	def definite(self):
		"""Name of the object with definite article"""
		return '%s %s' % (self.def_article, self.name)

	def describe(self):
		"""Get a description of the object"""
		return self.description

	def flag(self, flag):
		if flag not in self.flags or not self.flags[flag]:
			return False
		return True

	def canfit(self, other):
		"""Can other fit inside me?"""
		return True

	def on_added(self):
		for cb in self.added_cbs:
			cb(self)

	def on_removed(self):
		for cb in self.removed_cbs:
			cb(self)

	def on_destroyed(self):
		for cb in self.destroyed_cbs:
			cb(self)

	def on_moved(self):
		for cb in self.moved_cbs:
			cb(self)

	def add(self, other):
		"""Put other inside me, if possible."""
		if other == self:
			return False

		if self.canfit(other):
			other.location = None
			other.removeself()
			self.contained.append(other)
			other.container = self

			other.on_added()

			return True
		else:
			raise NotImplemented

	def remove(self, other):
		"""Remove other from me.

		   Default behaviour is to place in world at current location."""

		if other in self.contained:
			other.container = None
			self.contained.remove(other)
			other.location = self.location

			other.on_removed()

			return True

	def removeself(self):
		"""Remove self from any container"""
		if self.container:
			self.container.remove(self)

	def destroy(self):
		#TODO if we get deleted, will there be references to us hanging around?
		self.removeself()
		for obj in self.contained:
			self.remove(obj)
		self.destroyed = True

		self.on_destroyed()
		self.level.remove_object(self)

	def __str__(self):
		return self.name
