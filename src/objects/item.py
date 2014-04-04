from objects import GameObject
from ai.predicate import Wants, Solves


class Key(GameObject):
    def __init__(self, unlocks, *args, **kwargs):
        GameObject.__init__(self, 'key', char='[', *args, **kwargs)
        self.unlocks = unlocks
        self.facts.append(Solves(self, unlocks.blocks_fact.obj))
        for obj in self.world.player.wants:
            if obj.location_fact.obj == self.unlocks.blocks:
                # Todo: player doesn't *want* us until they know about us!
                self.facts.append(Wants(self.world.player, self))
                #self.player.facts.append(Wants(self.world.player, self))
        #if [1 for x in Wants.objs(self.world.player) if x.location in unlocks.blocks_fact.obj]:
