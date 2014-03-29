### Contains definition of Game Objects

class GameObject:
	"""An object in the game world"""
	def __init__(self, name, description='', location=None, char='?'):
		"""Create a new GameObject with the given name, description and location."""
		self.name = name
		self.description = description
		self.location = location
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

	#TODO: something something locations vs containers
	#TODO: No, really???
	
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

	def move(self, location):
		"""Move the object to location"""
		#TODO: Moving between levels. (Don't forget to move contained objects)
		#self.level[self.location].remove(self)
		self.level.move_object(self, location)

		self.location = location
		#self.level[self.location].append(self)

		self.on_moved()

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
			other.move(None)
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
			other.move(self.location)

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
