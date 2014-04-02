class Predicate(object):
    def __init__(self, subj, obj):
        self.subj = subj
        self.obj = obj


class In(Predicate):
    def __str__(self):
        return '%s is in %s' % (self.subj, self.obj)


class Wants(Predicate):
    def __str__(self):
        return '%s wants %s' % (self.subj, self.obj)


class Solves(Predicate):
    def __str__(self):
        return '%s solves %s' % (self.subj, self.obj)


class Blocks(Predicate):
    def __str__(self):
        return '%s blocks %s' % (self.subj, self.obj)
