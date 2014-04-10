### Base class for the player and NPCs

import random

from objects import GameObject
import util
from ai.predicate import In, Wants, Solves

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
        def match_name(name, string):
            string = util.text_compare_re.sub('', string.lower())
            name = util.text_compare_re.sub('', unicode(name).lower())
            return string == name

        if topic == 'hello':
            result = 'Hello, my name is ' + self.name
        else:
            useful = set()
            for fact in self.knowledge:
                if match_name(fact.subj, topic):
                    useful |= self.infer_useful_facts(fact.subj)
                if match_name(fact.obj, topic):
                    useful |= self.infer_useful_facts(fact.obj)

            if useful:
                result = self.say_fact(random.choice(list(useful)))
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
                elif dist_2 < 4*location.area:
                    result += ', not far to the %s' % (compass)
                elif dist_2 < 16*location.area:
                    result += ', which lies to the %s' % (compass)
                else:
                    result += ', which lies far %s of here' % (compass)

            return result
        return unicode(fact)
    def infer_useful_facts(self, obj, result=None):
        """Given an object, return facts the player might want to know about it"""
        if not result:
            result = set()

        for fact in self.knowledge:
            if fact in result:
                continue

            if type(fact) == In and fact.subj == obj:
                result.add(fact)
                self.infer_useful_facts(fact.obj, result)
            elif type(fact) == Solves and fact.obj == obj:
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
        self.flags['hostile'] = True


class Villager(Actor):
    def __init__(self, *args, **kwargs):
        Actor.__init__(self, char='P', *args, **kwargs)
