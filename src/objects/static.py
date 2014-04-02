from objects import GameObject

class Door(GameObject):
    def __init__(self, p, locked=False):
        GameObject.__init__(self, 'door', location=p, char='+')
        self.block_move = True
        self.block_sight = True
        self.locked = locked

    def bumped(self, other):
        if self.block_move:
            if self.locked:
                if self.key and self.key in other:
                    self.world.describe('%s unlocked %s' % (other.definite(), self.definite()))
                    self.locked = False
                else:
                    self.world.describe('%s is locked' % (self.definite()))
            else:
                self.world.describe('%s opened %s' % (other.definite(), self.definite()))
                self.block_move = False
                self.block_sight = False
                self.char = 'o'
            return True

        return False


class Key(GameObject):
    def __init__(self, unlocks, *args, **kwargs):
        GameObject.__init__(self, 'key', char='[', *args, **kwargs)
        self.unlocks = unlocks



