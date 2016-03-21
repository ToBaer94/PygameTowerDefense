import pygame as pg
from os import path, pardir
from bullet import Bullet, ExplosiveBullet, Beam, SlowBullet, AimlessBullet, Laser
from buttons.upgrade_button import UpgradeButton
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK
Vector = pg.math.Vector2

tower_dir = path.join(path.dirname(__file__), "assets", "towers")
ui_dir = path.join(path.dirname(__file__), "assets", "ui")


class Tower(pg.sprite.Sprite):
    name = "Sniper Tower"
    radius = 100
    damage = 1
    tier = 1
    cost = 100
    upgrade_cost = 70
    bullet_cd = 1000
    bullet_speed = 2
    max_tier = 5

    def __init__(self, x, y, level):
        super(Tower, self).__init__()
        self.image = pg.image.load(path.join(tower_dir, "tower.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = Vector(x, y)
        self.level = level
        self.creeps = self.level.creep_group

        self.last_bullet = pg.time.get_ticks()

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_damage.png"), 0+21, 512+19, self, self.upgrade_attack)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_range.png"), 0 + 110, 512 + 19, self, self.upgrade_range)

    def update(self, dt):
        target = None
        shortest_distance = 100000 # "Infinite"

        collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)
        for creep in collision_group:
                new_distance = self.pos.distance_to(creep.pos)
                if new_distance < shortest_distance or target is None:
                    target = creep
                    shortest_distance = new_distance

        now = pg.time.get_ticks()
        if now - self.last_bullet > self.bullet_cd and target is not None:
            self.last_bullet = now
            self.shoot_bullet(target)

    def shoot_bullet(self, target):
        bullet = Bullet(self.rect.x, self.rect.y, self.level, self.damage, self.bullet_speed, target)
        self.level.bullet_group.add(bullet)

    def draw_attack_range(self, screen):
        pg.draw.circle(screen, pg.Color("black"), (self.rect.center), self.radius, 1)

    def upgrade_attack(self):
        if self.tier <= self.max_tier:
            self.damage += 1
            self.tier += 1
            self.upgrade_cost += 100

    def upgrade_range(self):
        if self.tier <= self.max_tier:
            self.radius += 10
            self.tier += 1
            self.upgrade_cost += 100

    def check_collision(self, tower, other):
        tower_vector_pos = Vector(tower.rect.center)
        other_vector_pos = Vector(other.rect.center)
        distance = tower_vector_pos.distance_to(other_vector_pos)
        if tower.radius + other.radius > distance:
            return True
        return False


class CannonTower(Tower):
    name = "Cannon Tower"
    radius = 75
    damage = 2
    tier = 1
    cost = 200
    bullet_cd = 2000
    upgrade_cost = 20
    bullet_speed = 1

    def __init__(self, x, y, level):
        super(CannonTower, self).__init__(x, y, level)
        self.image = pg.image.load(path.join(tower_dir, "tower2.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_damage.png"), 0+21, 512+19, self, self.upgrade_attack)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_range.png"), 0 + 110, 512 + 19, self, self.upgrade_range)


class ExplosiveTower(Tower):
    name = "Explosive Tower"
    radius = 75
    damage = 1.5
    tier = 1
    cost = 200
    bullet_cd = 1500
    upgrade_cost = 120
    speed = 1

    def __init__(self, x, y, level):
        super(ExplosiveTower, self).__init__(x, y, level)
        self.image = pg.image.load(path.join(tower_dir, "tower3.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_damage.png"), 0+21, 512+19, self, self.upgrade_attack)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_range.png"), 0 + 110, 512 + 19, self, self.upgrade_range)


    def shoot_bullet(self, target):
        bullet = ExplosiveBullet(self.rect.x, self.rect.y, self.level, self.damage, self.speed, target)
        self.level.bullet_group.add(bullet)


class FireTower(Tower):
    name = "Fire Tower"
    radius = 100
    damage = 1.5
    tier = 1
    cost = 550
    bullet_cd = 1500
    upgrade_cost = 150
    bullet_speed = 1
    attack_radius = [5, 10, 15, 20, 25]
    tick_frequency = 1000

    def __init__(self, x, y, level):
        super(FireTower, self).__init__(x, y, level)
        self.image = pg.image.load(path.join(tower_dir, "tower4.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))
        self.firing = False
        self.pos = Vector(self.rect.center)
        self.target = None
        self.fired_beam = None

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_damage.png"), 0+21, 512+19, self, self.upgrade_attack)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_dps.png"), 0+110, 512+19, self, self.upgrade_damage_tick_frequency)


    def update(self, dt):
        target = None
        shortest_distance = 100000 # "Infinite"

        collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)
        for creep in collision_group:
                new_distance = self.pos.distance_to(creep.pos)
                if new_distance > shortest_distance or target is None:
                    target = creep
                    shortest_distance = new_distance

        if target is not None and not self.firing:
            self.target = target
            targeting_vec = Vector(target.rect.center) - Vector(self.rect.center)
            targeting_vec = targeting_vec.normalize()
            targeting_vec.scale_to_length(self.radius - 2 * self.tier)
            pos_1 = self.pos + targeting_vec * 1 / 5
            pos_2 = self.pos + targeting_vec * 2 / 5
            pos_3 = self.pos + targeting_vec * 3 / 5
            pos_4 = self.pos + targeting_vec * 4 / 5
            pos_5 = self.pos + targeting_vec * 5 / 5

            pos_list = [pos_1, pos_2, pos_3, pos_4, pos_5]

            self.shoot_beam(target, pos_list, targeting_vec)
            self.firing = True

        if target is not None and self.firing and self.fired_beam is not None:
            self.target = target
            targeting_vec = Vector(target.rect.center) - Vector(self.rect.center)
            targeting_vec = targeting_vec.normalize()
            targeting_vec.scale_to_length(self.radius - 2 * self.tier)
            pos_1 = self.pos + targeting_vec * 1 / 5
            pos_2 = self.pos + targeting_vec * 2 / 5
            pos_3 = self.pos + targeting_vec * 3 / 5
            pos_4 = self.pos + targeting_vec * 4 / 5
            pos_5 = self.pos + targeting_vec * 5 / 5

            pos_list = [pos_1, pos_2, pos_3, pos_4, pos_5]
            self.fired_beam.update_pos(self.rect.x + 0.5 * self.rect.width, self.rect.y + 0.5 * self.rect.height,
                    self.damage, target, pos_list, targeting_vec, self.tick_frequency)

        if target is None:
            if self.fired_beam is not None:
                self.fired_beam.kill()
                self.firing = False

    def shoot_beam(self, target, pos_list, vector):
        if self.fired_beam is not None:
            self.fired_beam.kill()

        beam = Beam(self.rect.x + 0.5 * self.rect.width, self.rect.y + 0.5 * self.rect.height, self.level,
                    self.damage, self.bullet_speed, target, pos_list, vector, self.attack_radius, self.tick_frequency)
        self.fired_beam = beam
        self.level.beam_group.add(beam)

    def upgrade_damage_tick_frequency(self):
        if self.tier <= self.max_tier:
            self.tick_frequency -= 50
            self.tier += 1
            self.upgrade_cost += 100


class SlowTower(Tower):
    name = "Slow Tower"
    radius = 100
    damage = 0
    tier = 1
    cost = 250
    bullet_cd = 1000
    upgrade_cost = 50
    bullet_speed = 1
    speed_mod = 0.8
    slow_duration = 3000

    def __init__(self, x, y, level):
        super(SlowTower, self).__init__(x, y, level)
        self.image = pg.image.load(path.join(tower_dir, "tower5.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_slow_duration.png"), 0+21, 512+19, self, self.upgrade_slow_duration)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_slow_modifier.png"), 0+110, 512+19, self, self.upgrade_slow_modifier)

    def update(self, dt):
        target = None

        collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)
        for creep in collision_group:
                new_distance = self.pos.distance_to(creep.pos)
                if not target:
                    target = creep

                elif target.slowed:
                    target = creep

        now = pg.time.get_ticks()
        if now - self.last_bullet > self.bullet_cd and target is not None:
            self.last_bullet = now
            self.shoot_bullet(target)

    def shoot_bullet(self, target):
        bullet = SlowBullet(self.rect.x, self.rect.y, self.level, self.damage, self.bullet_speed, target, self.speed_mod, self.slow_duration)
        self.level.bullet_group.add(bullet)

    def upgrade_slow_modifier(self):
        if self.tier <= self.max_tier:
            self.speed_mod -= 0.1
            self.tier += 1
            self.upgrade_cost += 100

    def upgrade_slow_duration(self):
        if self.tier <= self.max_tier:
            self.slow_duration += 200
            self.tier += 1
            self.upgrade_cost += 100


class MultiTower(Tower):
    name = "Multi Tower"
    radius = 100
    damage = 1
    tier = 1
    cost = 300
    upgrade_cost = 70
    bullet_cd = 2500
    bullet_speed = 2

    def __init__(self, x, y, level):
        super(MultiTower, self).__init__(x, y, level)
        self.image = pg.image.load(path.join(tower_dir, "tower6.png")).convert_alpha()

        self.direction_list = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]

        self.upgrade_button_1 = UpgradeButton(path.join(ui_dir, "upgrade_damage.png"), 0+21, 512+19, self, self.upgrade_attack)
        self.upgrade_button_2 = UpgradeButton(path.join(ui_dir, "upgrade_range.png"), 0 + 110, 512 + 19, self, self.upgrade_range)

    def update(self, dt):
        collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)

        now = pg.time.get_ticks()
        if now - self.last_bullet > self.bullet_cd and collision_group:
            self.last_bullet = now
            self.shoot_bullets()

    def shoot_bullets(self):
        for direction in self.direction_list:
            bullet = AimlessBullet(self.rect.x, self.rect.y, self.level, self.damage, self.bullet_speed, direction, self.radius)
            self.level.bullet_group.add(bullet)


class LaserTower(Tower):
    name = "Laser Tower"
    radius = 100
    range = 96
    damage = 1
    tier = 1
    cost = 650
    upgrade_cost = 200
    bullet_cd = 1000
    bullet_speed = 2
    max_tier = 5

    def __init__(self, x, y, level):
        super(LaserTower, self).__init__(x, y, level)

        self.image = pg.image.load(path.join(tower_dir, "tower7.png")).convert_alpha()

        self.collision_rects = []
        self.laser_rects = []

        self.offset = 5

        self.create_collision_rects()
        self.create_laser_rects()


    def update(self, dt):
        target = None
        index = 0

        for rect in self.collision_rects:
            for creep in self.creeps:
                collision = rect.colliderect(creep.rect)
                if collision:
                    target = creep
                    index = self.collision_rects.index(rect)
                    break

            if target:
                break

        now = pg.time.get_ticks()
        if now - self.last_bullet > self.bullet_cd and target is not None:
            self.last_bullet = now
            direction_rect = self.laser_rects[index]
            self.shoot_laser(direction_rect)

    def shoot_laser(self, direction_rect):
        laser = Laser(direction_rect.x, direction_rect.y, self.level, self.damage, self.bullet_speed, self.creeps, direction_rect)
        self.level.bullet_group.add(laser)

    def draw_attack_range(self, screen):
        for rect in self.collision_rects:
            pg.draw.rect(screen, BLACK, rect, 1)

    def create_laser_rects(self):
        north_rect = pg.Rect(self.rect.x + self.offset, 0, self.rect.width - 2 * self.offset, self.rect.y)
        west_rect = pg.Rect(0, self.rect.y + self.offset, self.rect.x, self.rect.height - 2 * self.offset)
        south_rect = pg.Rect(self.rect.x + self.offset, self.rect.y + self.rect.height, self.rect.width - 2 * self.offset, SCREEN_HEIGHT - self.rect.y)
        east_rect = pg.Rect(self.rect.x + self.rect.width, self.rect.y + self.offset, SCREEN_WIDTH - self.rect.x, self.rect.height - 2 * self.offset)
        self.laser_rects = [north_rect, west_rect, south_rect, east_rect]

    def create_collision_rects(self):
        self.collision_rects = []

        north_rect = pg.Rect(self.rect.x, self.rect.y - self.range, self.rect.width, self.range)
        west_rect = pg.Rect(self.rect.x - self.range, self.rect.y, self.range, self.rect.height)
        south_rect = pg.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.range)
        east_rect = pg.Rect(self.rect.x + self.rect.width, self.rect.y, self.range, self.rect.height)
        self.collision_rects = [north_rect, west_rect, south_rect, east_rect]

    def upgrade_range(self):
        if self.tier <= self.max_tier:
            self.range += 16
            self.tier += 1
            self.upgrade_cost += 100
            self.create_collision_rects()




