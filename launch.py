#!/usr/bin/env python

import pygame
import pygame.locals
import sys
import os
import cProfile
import pstats

sys.path.append(os.path.join('.', 'src'))

import world

PROFILE = False

if __name__=='__main__':
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    screen.fill((255, 255, 255))

    #room = Room('start', 'A boring starting room')
    world = world.World()
    #world.add_objective(MainQuest(world))
    if PROFILE:
        cProfile.run('world.main_loop(screen)', 'profiledump')
        p = pstats.Stats('profiledump')
        p.sort_stats('cumtime').print_stats(.5)
    else:
        world.main_loop(screen)

    #table = load_tile_table("/home/fish/Pictures/M_BISON_YESSSSSSS.jpg", 24, 16)
    #for x, row in enumerate(table):
    #    for y, tile in enumerate(row):
    #        screen.blit(tile, (x*32, y*24))
