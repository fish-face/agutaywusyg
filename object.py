### Contains definition of Game Objects

class GameObject:
	"""An object in the game world"""
	def __init__(self, name, description='', location=None, char='?'):
		"""Create a new GameObject with the given name, description and location."""
		self.name = name
		self.description = description
		self.location = location
		self.container = None
		self.contained = []
		self.tileindex = (0,0)
		self.char = char

		self.moved_cbs = []
		self.added_cbs = []
		self.removed_cbs = []
		self.destroyed_cbs = []

		if self.name[0].lower() in 'aeiou':
			self.indef_article = 'an'
		else:
			self.indef_article = 'a'

	#TODO: something something locations vs containers
	#TODO: No, really???
	
	def indefinite(self):
		return '%s %s' % (self.indef_article, self.name)

	def describe(self):
		"""Get a description of the object"""
		return self.description

	def move(self, location):
		"""Move the object to location"""
		self.location = location

	def canfit(self, other):
		"""Can other fit inside me?"""
		return True

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
	
	def on_added(self):
		for cb in self.added_cbs:
			cb(self)
	
	def remove(self, other):
		"""Remove other from me"""
		if other in self.contained:
			other.location = [self.location[0], self.location[1]]
			other.container = None
			self.contained.remove(other)

			return True
	
	def removeself(self):
		"""Remove self from any container"""
		if self.container:
			container.remove(self)
	
	def destroy(self):
		#TODO if we get deleted, will there be references to 
		self.removeself()
		for obj in self.contained:
			self.remove(obj)
	
	def __str__(self):
		return self.name
