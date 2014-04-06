class Predicate(object):
    instances = []
    def __init__(self, subj, obj):
        self.subj = subj
        self.obj = obj

        type(self).add(self)

    @classmethod
    def add(cls, predicate):
        #print cls, "adding!"
        cls.instances.append(predicate)

    @classmethod
    def remove(cls, predicate):
        cls.instances.remove(predicate)

    def destroy(self):
        type(self).remove(self)

    def __eq__(self, other):
        return type(self) == type(other) and self.obj == other.obj and self.subj == other.subj


class In(Predicate):
    def __str__(self):
        return '%s is in %s' % (self.subj, self.obj)


# Maybe the following should share some behaviour with In
class HeldBy(Predicate):
    def __str__(self):
        return '%s is held by %s' % (self.subj, self.obj)


class Wants(Predicate):
    def __str__(self):
        return '%s wants %s' % (self.subj, self.obj)


class Solves(Predicate):
    def __str__(self):
        return '%s solves %s' % (self.subj, self.obj)


class Blocks(Predicate):
    def __str__(self):
        return '%s blocks %s' % (self.subj, self.obj)
