import pygame as pg
import tilerenderer
from tower import Tower, Tower2, ExplosiveTower, FireTower
from creep import Creep
from os import path, pardir

Vector = pg.math.Vector2

level_dir = path.join(path.dirname(__file__), "assets", "levels")


class Level(object):
    def __init__(self):
        self.tmx_file = path.join(level_dir, "map.tmx")
        self.tile_renderer = tilerenderer.Renderer(self.tmx_file)
        self.map_surface = self.tile_renderer.make_map()
        self.map_rect = self.map_surface.get_rect()

        self.tower_group = pg.sprite.Group()
        self.creep_group = pg.sprite.Group()
        self.bullet_group = pg.sprite.Group()
        self.beam_group = pg.sprite.Group()

        self.tower_list = [Tower, Tower2, ExplosiveTower, FireTower]
        self.start_pos = None
        self.end_pos = None
        for x in range(self.tile_renderer.tmx_data.width):
            for y in range(self.tile_renderer.tmx_data.height):
                proper = self.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if "start" in proper:
                    self.start_pos = (x, y)
                if "end" in proper:
                    self.end_pos = (x, y)

        self.spawner = Spawner(self)
        self.waves = [3, 5, 10]
        self.wave_number = 0
        self.wave_length = self.waves[self.wave_number]
        self.last_spawn = pg.time.get_ticks()

        self.money = 2000
        self.creep_path = None

        self.game_over = False

    def update(self, dt):
        print self.wave_length
        if self.wave_length > 0:
            now = pg.time.get_ticks()
            if now - self.last_spawn > 2000:
                self.last_spawn = now
                self.spawner.spawn_standard_enemy()
                self.wave_length -= 1

        self.tower_group.update(dt)
        self.creep_group.update(dt)
        self.bullet_group.update(dt)
        self.beam_group.update(dt)

        if self.wave_length == 0 and self.creep_group.__len__() == 0:
            print "end of wave"
            if self.wave_number < len(self.waves) - 1:
                self.wave_number += 1
                self.wave_length = self.waves[self.wave_number]
            else:
                print "games over"

    def draw(self, screen):
        screen.blit(self.map_surface, (0, 0))
        self.tower_group.draw(screen)
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


    def spawn_standard_enemy(self):
        creep = Creep(self.level, self.level.creep_path)
        self.level.creep_group.add(creep)

