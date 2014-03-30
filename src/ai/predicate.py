class Predicate(object):
	def __init__(self, subj, obj):
		self.subj = subj
		self.obj = obj

class In(Predicate):
	def __str__(self):
		return '%s is in %s' % (self.subj, self.obj)
