import pygame as pg
from os import path
from constants import RED, YELLOW, GREEN, BLACK
import random
Vector = pg.math.Vector2


creep_dir = path.join(path.dirname(__file__), "assets", "creeps")


class Creep(pg.sprite.Sprite):
    total_health = 15.0
    health = 15.0
    speed = 0.5
    orig_speed = 0.5
    gold = 15

    def __init__(self, level, pathing):
        super(Creep, self).__init__()

        self.image = pg.image.load(path.join(creep_dir, "creep.png")).convert_alpha()

        self.level = level

        self.pathing = pathing

        self.start_pos = self.pathing[0]
        self.end_pos = self.pathing[-1]

        self.rect = self.image.get_rect(topleft = (32 * self.start_pos[0], 32 * self.start_pos[1]))
        self.radius = 16

        self.pos = Vector(32 * self.start_pos[0], 32 * self.start_pos[1])

        self.end = (32 * self.end_pos[0] + 16, 32 * self.end_pos[1] + 16)

        self.dead = False
        self.slowed = False

        self.start_index = 1
        self.moved_pixels = 0
        self.color = GREEN
        self.slow_timer = 0
        self.slow_duration = 1000

    def set_movement(self):
        target_vector = Vector(self.pathing[self.start_index][0] - self.pathing[self.start_index-1][0], self.pathing[self.start_index][1] - self.pathing[self.start_index-1][1]) #self.pathing[self.start_index][1])

        target_vector = target_vector.normalize()

        if self.moved_pixels >= 32:
            self.start_index += 1
            self.moved_pixels = 0
        return target_vector

    def update(self, dt):
        self.set_ui()

        if self.health <= 0:
            self.dead = True
            self.level.money += self.gold
            self.level.earned_money += self.gold
            self.level.killed_creeps += 1
            self.kill()

        if self.rect.collidepoint(self.end):
            self.level.game_over = True

        now = pg.time.get_ticks()
        if now - self.slow_timer > self.slow_duration and self.slowed:
            self.slow_timer = 0
            self.speed = self.orig_speed
            self.slowed = False

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
        if self.health / self.total_health >= 0.7:
            self.color = GREEN
        elif self.health / self.total_health >= 0.4:
            self.color = YELLOW
        else:
            self.color = RED

    def draw_ui(self, screen):
        pg.draw.rect(screen, BLACK, [self.rect.x + 0.3 * self.rect.width - 3,
                                     self.rect.y - 5, self.rect.width // 2 + 6, 5])
        pg.draw.rect(screen, self.color, [self.rect.x + 0.3 * self.rect.width - 2, self.rect.y - 4,
                                          (float(self.health) / self.total_health * self.rect.width // 2) + 4, 3])

    def set_slowed(self, modifier, duration):
        print self.speed
        if not self.slowed:
            self.slowed = True
            self.slow_duration = duration
            self.speed *= modifier
        print self.speed
        self.slow_timer = pg.time.get_ticks()

    def take_damage(self, damage):
        self.health -= damage


class Worm(Creep):
    total_health = 10.0
    health = 10.0
    speed = 0.8
    orig_speed = 0.8

    gold = 20
    def __init__(self, level, pathing):
        super(Worm, self).__init__(level, pathing)

        self.image = pg.image.load(path.join(creep_dir, "worm.png")).convert_alpha()


class Behemoth(Creep):
    total_health = 30.0
    health = 30.0
    speed = 0.3
    orig_speed = 0.3

    gold = 30

    def __init__(self, level, pathing):
        super(Behemoth, self).__init__(level, pathing)

        self.image = pg.image.load(path.join(creep_dir, "behemoth.png")).convert_alpha()

    def take_damage(self, damage):
        self.health -= damage
        self.speed += 0.03
        self.orig_speed += 0.03


class SwiftWalker(Creep):
    total_health = 20.0
    health = 20.0
    speed = 0.4
    orig_speed = 0.4

    gold = 30

    def __init__(self, level, pathing):
        super(SwiftWalker, self).__init__(level, pathing)
        self.image = pg.image.load(path.join(creep_dir, "swiftwalker.png")).convert_alpha()

    def take_damage(self, damage):
        random_number = random.randint(1, 5)
        if random_number == 1:
            print "missed"
        else:
            self.health -= damage



