import pygame as pg
from os import path, pardir
import copy
Vector = pg.math.Vector2


creep_dir = path.join(path.dirname(__file__), "assets", "creeps")

RED = pg.Color("red")
YELLOW = pg.Color("yellow")
GREEN = pg.Color("green")
BLACK = pg.Color("black")


class Creep(pg.sprite.Sprite):
    health = 10
    speed = 0.3

    def __init__(self, level, pathing):
        super(Creep, self).__init__()

        self.image = pg.image.load(path.join(creep_dir, "enemy.png")).convert_alpha()

        self.level = level
        self.start_pos = self.level.start_pos
        self.end_pos = self.level.end_pos

        self.rect = self.image.get_rect(topleft = (32 * self.start_pos[0], 32 * self.start_pos[1]))
        self.radius = 16

        self.pos = Vector(32 * self.start_pos[0], 32 * self.start_pos[1])

        self.end = (32 * self.end_pos[0] + 16, 32 * self.end_pos[1] + 16)

        self.dead = False

        self.pathing = pathing
        self.start_index = 1
        self.moved_pixels = 0
        self.color = GREEN


    def set_movement(self):
        target_vector = Vector(self.pathing[self.start_index][0] - self.pathing[self.start_index-1][0], self.pathing[self.start_index][1] - self.pathing[self.start_index-1][1]) #self.pathing[self.start_index][1])

        target_vector = target_vector.normalize()


        if self.moved_pixels > 32:
            self.start_index += 1
            self.moved_pixels = 0
        return target_vector


    def update(self, dt):
        self.set_ui()

        if self.health <= 0:
            self.dead = True
            self.level.money += 20
            self.kill()

        if self.rect.collidepoint(self.end):
            self.level.game_over = True

        velocity = self.set_movement()
        velocity.x *= self.speed
        velocity.y *= self.speed
        self.pos.x += velocity.x * dt
        self.pos.y += velocity.y * dt
        self.moved_pixels += abs(velocity.x * dt) + abs(velocity.y * dt)
        if self.moved_pixels > 32 or self.moved_pixels <= self.speed * dt:
            self.pos.x = self.level.tile_renderer.tmx_data.tilewidth * ((self.pos.x + self.speed + 1) // self.level.tile_renderer.tmx_data.tilewidth)
            self.pos.y = self.level.tile_renderer.tmx_data.tileheight * ((self.pos.y + self.speed + 1) // self.level.tile_renderer.tmx_data.tileheight)
        self.rect.topleft = self.pos

    def draw_debug(self, screen):
        pg.draw.circle(screen, BLACK, self.rect.center, self.radius, 1)

    def set_ui(self):
        if self.health >= 7:
            self.color = GREEN
        elif self.health >= 4:
            self.color = YELLOW
        else:
            self.color = RED

    def draw_ui(self, screen):
        pg.draw.rect(screen, BLACK, [self.rect.x + 0.3 * self.rect.width - 3,
                                                 self.rect.y - 5, self.rect.width // 2 + 6, 5])
        pg.draw.rect(screen, self.color, [self.rect.x + 0.3 * self.rect.width - 2, self.rect.y - 4,
                                          (float(self.health) / 10 * self.rect.width // 2) + 4, 3])


