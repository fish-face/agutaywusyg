from objects import GameObject
from ai.predicate import Blocks

class Door(GameObject):
    def __init__(self, p, locked=False, blocks=None, *args, **kwargs):
        GameObject.__init__(self, 'door', location=p, char='+', *args, **kwargs)
        self.block_move = True
        self.block_sight = True
        self.blocks = blocks
        self.locked = locked

    @property
    def locked(self):
        return self._locked

    @locked.setter
    def locked(self, locked):
        self._locked = locked
        if self.blocks and locked:
            self.blocks_fact = Blocks(self,self.blocks)

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

