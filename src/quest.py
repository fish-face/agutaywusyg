from ai.predicate import Wants

class Objective:
    def __init__(self, world, name, description=''):
        self.name = name
        self.description = description
        self.world = world
        world.add_objective(self)

        self.active = False
        self.succeeded = False
        self.failed = False

    def activate(self):
        self.active = True

    def success(self):
        self.succeeded = True
        self.active = False

    def fail(self):
        self.failed = True
        self.active = False


class MainQuest(Objective):
    def __init__(self, world):
        Objective.__init__(self, world, 'Retrieve the Amulet', 'Take the Amulet of Yendor from the Wizard and Sacrifice it to your God.')
        self.activate()

        amulet = world.get_object_by_name('Amulet of Yendor')
        if amulet is None:
            return
        amulet.added_cbs.append(self.amulet_added)
        world.player.wants.append(amulet)
        #world.player.wants.append(Wants(world.player, amulet))

    def amulet_added(self, amulet):
        if amulet.container == self.world.player:
            self.success()

    def success(self):
        Objective.success(self)
        self.world.win()
