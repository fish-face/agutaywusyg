### Base class for the player and NPCs

import random

from objects import GameObject


class Actor(GameObject):
    def __init__(self, name, description='', location=None, *args, **kwargs):
        self.map_memory = {}

        GameObject.__init__(self, name=name, description=description, location=location, *args, **kwargs)

        self.knowledge = []
        self.wants = []
        self.relationships = None
        self.hp = 1
        self.block_move = True

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if value and value not in self.map_memory:
            self.map_memory[value] = [None] * value.height
            for y in xrange(value.height):
                self.map_memory[value][y] = [None] * value.width
        GameObject.level.fset(self, value)

    def ask(self, other, topic):
        """Ask another Actor about topic"""
        wants = [fact for fact in self.knowledge if fact.obj in other.wants]
        topic = random.choice([fact.subj.name for fact in self.knowledge] + ['hello'])
        if topic == 'hello':
            result = 'Hello, my name is ' + self.name
        else:
            facts = [fact for fact in self.knowledge if fact.subj.name == topic]
            if wants:
                result = random.choice(wants)
            if facts:
                result = random.choice(facts)
            else:
                result = "I don't know anything about '%s.'" % topic

        #self.world.describe('%s says: %s' % (self.name, result))
        return unicode(result)

    def hit(self, other, damage):
        """I was hit by other for some damage"""
        self.hp -= damage
        if self.hp <= 0:
            self.die(other)

    def bumped(self, other):
        if self.flag('hostile'):
            self.hit(other, 1)
        else:
            self.ask(other, 'hello')

        return self.block_move

    def die(self, killer):
        """I died, somehow."""
        self.world.describe('%s killed %s!' % (killer.definite(), self.definite()))
        self.destroy()

    def update_fov(self):
        self.fov = self.level.get_fov(self.location)
        for p in self.fov:
            self.map_memory[self.level][p[1]][p[0]] = self.level[p]


class Player(Actor):
    def __init__(self, *args, **kwargs):
        Actor.__init__(self, char='@', *args, **kwargs)

    def definite(self):
        return self.name

    def indefinite(self):
        return self.name

    def on_moved(self):
        Actor.on_moved(self)
        if self.location:
            self.update_fov()


class Rodney(Actor):
    def __init__(self, *args, **kwargs):
        Actor.__init__(self, name='Wizard of Yendor', char='W', *args, **kwargs)
        self.flags['hostile'] = True


class Villager(Actor):
    def __init__(self, *args, **kwargs):
        Actor.__init__(self, char='P', *args, **kwargs)
