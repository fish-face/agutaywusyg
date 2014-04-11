### Base class for the player and NPCs

import random

from objects import GameObject
import util
from ai.predicate import In, Wants, Solves

class Actor(GameObject):
    def __init__(self, name, description='', location=None, *args, **kwargs):
        self.map_memory = {}

        GameObject.__init__(self, name=name, description=description, location=location, *args, **kwargs)

        self.knowledge = set()
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
        topic = util.canonicalise(topic)
        if topic == 'hello':
            result = 'Hello, my name is ' + self.name
        else:
            useful = set()
            for fact in self.knowledge:
                if topic == util.canonicalise(fact.subj):
                    useful |= self.infer_useful_facts(other, fact.subj)
                if topic == util.canonicalise(fact.obj):
                    useful |= self.infer_useful_facts(other, fact.obj)

            if useful:
                fact = random.choice(list(useful))
                result = self.say_fact(fact)
                if fact.subj in other or fact.obj in other:
                    # They're carrying the object in question, tell them about it
                    other.knowledge.add(fact)
            else:
                result = "I don't know anything about '%s.'" % topic

        return unicode(result)

    def say_fact(self, fact):
        """Produce a sensible rendition of fact to tell the player"""
        if isinstance(fact, In):
            result = fact.subj.indefinite()
            location = fact.obj
            if isinstance(location, tuple):
                # i.e. coordinates
                dist_2 = util.dist_2(self.location, location)
                compass = util.compass_to(self.location, location)
                if dist_2 < 4:
                    result += ' is here'
                elif dist_2 < 25:
                    result += ' is just over there'
                elif dist_2 < 100:
                    result += ' is over there'
                elif dist_2 < 10000:
                    result += ' is nearby, to the %s' % (compass)
                elif dist_2 < 1000000:
                    result += ' is some way %s of here' % (compass)
                else:
                    result += ' is far to the %s' % (compass)
            else:
                result += ' is in %s' % location.name
                dist_2 = util.dist_2(self.location, location.centre)
                compass = util.compass_to(self.location, location.centre)
                if dist_2 < location.area:
                    result += ' which is nearby'
                elif dist_2 < 8*location.area:
                    result += ', not far to the %s' % (compass)
                elif dist_2 < 25*location.area:
                    result += ', which lies to the %s' % (compass)
                else:
                    result += ', which lies far %s of here' % (compass)

            return result
        return unicode(fact)
    def infer_useful_facts(self, other, obj, result=None):
        """Given an object, return facts the player might want to know about it"""
        if not result:
            result = set()

        for fact in self.knowledge:
            if fact in result:
                continue

            if type(fact) == In and fact.subj == obj and not (obj in other):
                result.add(fact)
                self.infer_useful_facts(fact.obj, result)
            elif type(fact) == Solves and (fact.obj == obj or fact.subj == obj):
                result.add(fact)
                self.infer_useful_facts(fact.subj, result)

        return result

    def hit(self, other, damage):
        """I was hit by other for some damage"""
        self.hp -= damage
        if self.hp <= 0:
            self.die(other)

    def bumped(self, other):
        if self.flag('hostile'):
            self.hit(other, 1)
            return True
        else:
            return False

    def die(self, killer):
        """I died, somehow."""
        self.world.describe('%s killed %s!' % (killer.definite(), self.definite()))
        self.destroy()

    def update_fov(self):
        """I moved/level updated and I need to recalculate what I can see"""
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
        self.tileindex=(1,5)
        self.flags['hostile'] = True


class Villager(Actor):
    def __init__(self, *args, **kwargs):
        Actor.__init__(self, char='P', *args, **kwargs)
        self.tileindex = (0,4)
