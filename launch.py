#!/usr/bin/env python

import pygame
import pygame.locals
import sys
import os

sys.path.append(os.path.join('.', 'src'))

import world
from location import *
from actor import *
from object import GameObject
from renderer import Renderer
from quest import MainQuest

if __name__=='__main__':
	pygame.init()
	screen = pygame.display.set_mode((512, 512))
	screen.fill((255, 255, 255))

	#room = Room('start', 'A boring starting room')
	player = Player('you', 'The Player', (60,60))
	world = world.World(player)
	#world.add_objective(MainQuest(world))
	world.main_loop(screen)

    #table = load_tile_table("/home/fish/Pictures/M_BISON_YESSSSSSS.jpg", 24, 16)
    #for x, row in enumerate(table):
    #    for y, tile in enumerate(row):
    #        screen.blit(tile, (x*32, y*24))
