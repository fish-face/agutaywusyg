### The World knows about the map, terrain, objects, etc.

import sys
import pygame
import random
from collections import defaultdict

from renderer import Renderer
from level import TestLevel
from actor import Player
from quest import MainQuest
from constants import *

class World:
    def __init__(self):
        #self.objects = []
        #self.objects_map = defaultdict(list)
        self.objectives = []
        self.messages = []
        self.state = STATE_NORMAL

        pygame.key.set_repeat(1, 50)

        self.quitting = False
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()
        self.framerates = []

        self.font = pygame.font.SysFont('Sans', 18)

        self.player = Player(name='you', level=None, description='The Player')
        self.level = TestLevel(self)
        self.player.level = self.level
        self.player.location = (self.level.width/2, self.level.height/2)
        mq = MainQuest(self)

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
            delay = self.clock.tick(15)
            self.framerates.insert(0, 1000.0/delay)
            self.framerates = self.framerates[:100]
            framerate = sum(self.framerates)/100.0
            self.process_events()
            self.renderer.render(self, screen)
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
                took_turn = self.keypressed(e)
            elif e.type == pygame.MOUSEBUTTONUP:
                took_turn = self.clicked(e)

        if took_turn:
            self.update()

    def keypressed(self, e):
        took_turn = False
        if self.state == STATE_PICK:
            if e.key == pygame.K_LEFT or e.key == pygame.K_h:
                self.pick_location[0] -= 1
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_l:
                self.pick_location[0] += 1
            elif e.key == pygame.K_UP or e.key == pygame.K_k:
                self.pick_location[1] -= 1
            elif e.key == pygame.K_DOWN or e.key == pygame.K_j:
                self.pick_location[1] += 1
            elif e.key == pygame.K_PERIOD or e.key == pygame.K_RETURN:
                self.pick_done()
        elif self.state == STATE_DIALOGUE:
            self.do_dialogue(e)
        else:
            newloc = list(self.player.location)
            if e.key == pygame.K_LEFT or e.key == pygame.K_h:
                newloc[0] -= 1
            elif e.key == pygame.K_RIGHT or e.key == pygame.K_l:
                newloc[0] += 1
            elif e.key == pygame.K_UP or e.key == pygame.K_k:
                newloc[1] -= 1
            elif e.key == pygame.K_DOWN or e.key == pygame.K_j:
                newloc[1] += 1
            newloc = tuple(newloc)

            if e.key == pygame.K_COMMA:
                for obj in self.get_objects_at(self.player.location):
                    if self.player.add(obj):
                        self.describe('You pick up %s' % obj.indefinite())
                        took_turn = True

            elif e.key == pygame.K_d:
                for obj in self.player.contained:
                    if self.player.remove(obj):
                        self.describe('You drop %s' % obj.indefinite())
                        took_turn = True

            elif e.key == pygame.K_r:
                loc = self.player.location
                self.player.map_memory = {}
                self.level.setup()
                self.level.add_object(self.player)
                self.player.level = self.level
                self.player.location = loc
                #self.player.update_fov()
                self.messages = []

            elif e.key == pygame.K_0:
                self.renderer.tiles.scale = 1

            elif e.key == pygame.K_t:
                self.pick_target(self.talk)

            elif newloc != self.player.location:
                if self.can_move_to(self.player, newloc):
                    self.player.location = newloc
                    took_turn = True
                else:
                    for thing in self.level[newloc]:
                        if thing.bumped(self.player):
                            took_turn = True
                            break
        return took_turn

    def clicked(self, e):
        if e.button == 1:
            pass
        if e.button == 4:
            self.renderer.tiles.scale *= 1.1
        elif e.button == 5:
            self.renderer.tiles.scale *= 0.9

        return False

    def pick_target(self, handler):
        """Enter targeting mode"""
        self.state = STATE_PICK
        self.pick_handler = handler
        self.pick_location = list(self.player.location)

    def pick_done(self):
        """Targeting mode over, do something at the target"""
        self.state = STATE_NORMAL
        self.pick_handler(self.pick_location)

    def talk(self, target):
        """Try and initiate a conversation with someone"""
        if (abs(target[0] - self.player.location[0]) > 1 or
            abs(target[0] - self.player.location[0]) > 1):
            self.describe('Too far away')
            return

        targets = self.get_objects_at(target)
        valid_targets = [t for t in targets if hasattr(t, 'ask')]
        if not valid_targets:
            if targets:
                self.describe('You get no response from %s' % (targets[-1].definite()))
            else:
                self.describe('There\'s no-one there to talk to')
            return

        self.state = STATE_DIALOGUE
        self.conversation = []
        self.talking_to = valid_targets[-1]
        self.input_text = ''

    def do_dialogue(self, event):
        """Handle having a conversation"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_NORMAL
            elif event.key == pygame.K_RETURN:
                self.conversation.append('> %s' % (self.input_text))
                self.conversation.append(self.talking_to.ask(self.player, self.input_text))
                self.input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                if self.input_text:
                    self.input_text = self.input_text[:-1]
            elif event.unicode:
                self.input_text += event.unicode

    def describe(self, text):
        self.messages.append(text[0].upper() + text[1:])

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
