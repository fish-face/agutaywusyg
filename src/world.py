### The World knows about the map, terrain, objects, etc.

import sys
import pygame
import random
from collections import defaultdict

from renderer import Renderer
from level import TestLevel
from actor import Rodney

class World:
    def __init__(self, player):
        #self.objects = []
        #self.objects_map = defaultdict(list)
        self.objectives = []
        self.player = player
        self.level = TestLevel(self)
        #self.level = VillageLevel(self)
        self.level.add_object(player)
        player.location = (self.level.width/2, self.level.height/2)

        pygame.key.set_repeat(1, 50)

        self.quitting = False
        self.interpreter = CommandInterpreter(self)
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()
        self.framerates = []

        self.font = pygame.font.SysFont('Sans', 18)

    #def add_object(self, obj):
    #   if obj in self.objects:
    #       return

    #   self.objects.append(obj)
    #   self.objects_map[obj.location].append(obj)

    #   obj.world = self
    #
    #def remove_object(self, obj):
    #   if obj not in self.objects:
    #       return

    #   self.objects.remove(obj)
    #   self.objects_map[obj.location].remove(obj)
    #   obj.destroy()

    def add_objective(self, objective):
        self.objectives.append(objective)

    def get_objects_at(self, location, test=None):
        #First item at a location is always terrain
        if test is None:
            return self.level[location][1:]
        else:
            return [obj for obj in self.level[location][1:] if test(obj)]

    def get_object_by_name(self, name):
        #TODO this should not just work on the current level
        for obj in self.level.objects:
            if obj.name == name:
                return obj

    def can_move_to(self, obj, location):
        if [1 for x in self.level[location] if x.block_move]:
            return False
        return True

    def win(self):
        self.describe("You win!")
        self.quitting = True

    def main_loop(self, screen):
        while not self.quitting:
            delay = self.clock.tick(1000)
            self.framerates.insert(0, 1000.0/delay)
            self.framerates = self.framerates[:100]
            framerate = sum(self.framerates)/100.0
            self.process_events()
            self.renderer.render(screen, self.level, self.player)
            screen.blit(self.font.render('%d fps' % framerate, True, (255,255,255)),
                        (1, 1))
            pygame.display.flip()

    def process_events(self):
        took_turn = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.quitting = True
                return

            if e.type == pygame.KEYDOWN:
                newloc = list(self.player.location)
                if e.key == pygame.K_LEFT or e.key == pygame.K_h:
                    newloc[0] -= 1
                if e.key == pygame.K_RIGHT or e.key == pygame.K_l:
                    newloc[0] += 1
                if e.key == pygame.K_UP or e.key == pygame.K_k:
                    newloc[1] -= 1
                if e.key == pygame.K_DOWN or e.key == pygame.K_j:
                    newloc[1] += 1
                newloc = tuple(newloc)

                if e.key == pygame.K_COMMA:
                    for obj in self.get_objects_at(self.player.location):
                        if self.player.add(obj):
                            self.describe('You pick up %s' % obj.indefinite())
                            took_turn = True

                if e.key == pygame.K_d:
                    for obj in self.player.contained:
                        if self.player.remove(obj):
                            self.describe('You drop %s' % obj.indefinite())
                            took_turn = True

                if e.key == pygame.K_r:
                    self.level.setup()
                    self.level.add_object(self.player)

                if e.key == pygame.K_0:
                    self.renderer.tiles.scale = 1

                if newloc != self.player.location:
                    if self.can_move_to(self.player, newloc):
                        self.player.location = newloc
                        took_turn = True
                    else:
                        for thing in self.level[newloc]:
                            if thing.bumped(self.player):
                                took_turn = True
                                break
                        #enemies = self.get_objects_at(newloc, lambda o: o.flag('hostile'))
                        #if enemies:
                        #    enemies[0].hit(self.player, 1)
                        #else:
                        #    can_talk = self.get_objects_at(newloc, lambda o: hasattr(o, 'ask'))
                        #    if can_talk:
                        #        self.describe('%s says: %s' % (can_talk[0], can_talk[0].ask(self.player, 'hello')))

            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 4:
                    self.renderer.tiles.scale *= 1.1
                elif e.button == 5:
                    self.renderer.tiles.scale *= 0.9

        if took_turn:
            self.update()

    def describe(self, text):
        print text[0].upper() + text[1:]

    def update(self):
        self.player.update_fov()

class CommandInterpreter:
    def __init__(self, world):
        self.world = world

    def interpret(self, cmd):
        if cmd == 'look':
            self.cmd_look()
        elif cmd == 'quit':
            self.cmd_quit()
        elif cmd.split()[0] == 'take':
            self.cmd_take(cmd.split()[1])
        elif cmd == 'inventory':
            self.cmd_inventory()
        else:
            self.nonsense(cmd)

    def nonsense(self, cmd):
        self.world.describe("I didn't understand '%s'." % cmd)

    def cmd_inventory(self):
        if not self.world.player.contained:
            self.world.describe("You aren't carrying anything.")
            return

        self.world.describe('\n'.join(["You are carrying:"] + [str(x) for x in self.world.player.contained]))

    def cmd_take(self, name):
        objs = self.world.get_objects_in(name, self.world.player.location)
        if not objs:
            self.world.describe("You can't get %s" % name)

        for obj in objs:
            self.world.player.add(obj)
        self.world.describe('You take %s.' % name)

    def cmd_look(self):
        self.world.describe(self.world.player.location.describe())

    def cmd_quit(self):
        self.world.quitting = True
