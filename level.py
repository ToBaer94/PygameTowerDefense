import pygame as pg
import tilerenderer
from tower import Tower, Tower2, ExplosiveTower, FireTower, SlowTower, MultiTower
from trap import Mine
from creep import Creep, Worm, Behemoth, SwiftWalker
from os import path, pardir

import random

Vector = pg.math.Vector2

level_dir = path.join(path.dirname(__file__), "assets", "levels")

CREEP = 0
WORM = 1
BEHEMOTH = 2
SWIFTWALKER = 3


class Level(object):
    def __init__(self):
        self.tmx_file = path.join(level_dir, "map3.tmx")
        self.tile_renderer = tilerenderer.Renderer(self.tmx_file)
        self.map_surface = self.tile_renderer.make_map()
        self.map_rect = self.map_surface.get_rect()

        self.tower_group = pg.sprite.Group()
        self.trap_group = pg.sprite.Group()
        self.creep_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.beam_group = pg.sprite.Group()

        self.tower_list = [Tower, Tower2, ExplosiveTower, FireTower, SlowTower, MultiTower]
        self.trap_list = [Mine]
        """
        self.start_pos = None
        self.end_pos = None
        for x in range(self.tile_renderer.tmx_data.width):
            for y in range(self.tile_renderer.tmx_data.height):
                proper = self.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if "start" in proper:
                    self.start_pos = (x, y)
                if "end" in proper:
                    self.end_pos = (x, y)
        """

        self.spawner = Spawner(self)
        self.waves = [[3, 3, 3, 3],
                      [0, 1, 1, 1],
                      [0, 1, 0, 1, 0, 1],
                      [1, 1, 2, 2, 2, 2, 3, 1, 0, 1, 3, 1],
                      [0, 0]
                     ]
        self.wave_number = 0
        self.current_wave = self.waves[self.wave_number]
        self.current_spawn = 0
        self.last_spawn = pg.time.get_ticks()

        self.money = 2000
        self.creep_path = []

        self.game_over = False

    def update(self, dt):
        # print self.current_spawn, self.current_wave
        if len(self.current_wave) > self.current_spawn:
            now = pg.time.get_ticks()
            if now - self.last_spawn > 1000:
                self.last_spawn = now
                enemy = self.current_wave[self.current_spawn]
                self.spawner.spawn_enemy(enemy)
                self.current_spawn += 1

        self.tower_group.update(dt)
        self.trap_group.update(dt)
        self.creep_group.update(dt)
        self.bullet_group.update(dt)
        self.beam_group.update(dt)

        if self.current_spawn == len(self.current_wave) and self.creep_group.__len__() == 0:
            print "end of wave"
            if self.wave_number < len(self.waves) - 1:
                self.wave_number += 1
                self.current_wave = self.waves[self.wave_number]
                self.current_spawn = 0
            else:
                print "games over"

    def draw(self, screen):
        screen.blit(self.map_surface, (0, 0))
        self.tower_group.draw(screen)
        self.trap_group.draw(screen)
        self.creep_group.draw(screen)
        self.bullet_group.draw(screen)
        self.beam_group.draw(screen)

        for creep in self.creep_group:
            creep.draw_ui(screen)
            # creep.draw_debug(screen)

        #self.debug_beam(screen)



    def debug_beam(self, screen):
        for cir in self.beam_group:
            for cle in cir.circle_list:
                pos_x = int(cle[0].x)
                pos_y = int(cle[0].y)
                pg.draw.circle(screen, pg.Color("black"), (pos_x, pos_y), cle[1], 1)


class Spawner(object):
    def __init__(self, level):
        self.level = level

    def spawn_enemy(self, enemy):
        path = random.randint(0, len(self.level.creep_path) - 1)
        if enemy == CREEP:
            creep = Creep(self.level, self.level.creep_path[path])
        elif enemy == WORM:
            creep = Worm(self.level, self.level.creep_path[path])

        elif enemy == BEHEMOTH:
            creep = Behemoth(self.level, self.level.creep_path[path])

        elif enemy == SWIFTWALKER:
            creep = SwiftWalker(self.level, self.level.creep_path[path])
        else:
            print enemy, " is not a defined creep"
        self.level.creep_group.add(creep)

