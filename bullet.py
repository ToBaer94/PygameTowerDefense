import pygame as pg
from os import path, pardir
import math
from spritesheet_functions import SpriteSheet
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
Vector = pg.math.Vector2

bullet_dir = path.join(path.dirname(__file__), "assets", "bullets")


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, level, damage, speed, target):
        super(Bullet, self).__init__()
        self.image = pg.image.load(path.join(bullet_dir, "bullet.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))
        self.level = level
        self.target = target
        self.creeps = self.level.creep_group

        self.radius = 8
        self.damage = damage
        self.speed = speed

        self.pos = Vector(x, y)
        self.vel = 0

    def set_target(self):
        x_diff = self.target.pos.x - self.pos.x
        y_diff = self.target.pos.y - self.pos.y
        # print x_diff, y_diff
        self.vel = Vector(x_diff, y_diff)

    def update(self, dt):

        if self.target.rect.collidepoint(self.rect.center):
            self.target.take_damage(self.damage)
            self.kill()

        if self.target.dead:
            self.kill()

        self.set_target()
        new_vec = self.vel.normalize()
        self.pos.x += new_vec.x * self.speed * dt
        self.pos.y += new_vec.y * self.speed * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

    def draw_debug(self, screen):
        pg.draw.circle(screen, pg.Color("black"), self.rect.center, self.radius, 1)


class SlowBullet(Bullet):
    def __init__(self, x, y, level, damage, speed, target, speed_modifier, duration):
        super(SlowBullet, self).__init__(x, y, level, damage, speed, target)

        self.image = pg.image.load(path.join(bullet_dir, "slow_bullet.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft = (x, y))

        self.speed_modifier = speed_modifier
        self.slow_duration = duration

    def update(self, dt):

        if self.target.rect.collidepoint(self.rect.center):
            # self.target.take_damage(self.damage)
            self.target.set_slowed(self.speed_modifier, self.slow_duration)
            self.kill()

        if self.target.dead:
            self.kill()

        self.set_target()
        new_vec = self.vel.normalize()
        self.pos.x += new_vec.x * self.speed * dt
        self.pos.y += new_vec.y * self.speed * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y


class ExplosiveBullet(Bullet):
    def __init__(self, x, y, level, damage, speed, target):
        super(ExplosiveBullet, self).__init__(x, y, level, damage, speed, target)

        self.explosion_animation = []
        self.explosion_spritesheet = SpriteSheet(path.join(bullet_dir, "explo.png"))
        self.animation_index = 0

        for x in range(7):
            image = self.explosion_spritesheet.get_image(92 + x * (4 + 30), 9, 30, 30, 96, 96)
            self.explosion_animation.append(image)

        self.exploded = False
        self.exp_radius = 48
        self.animation_timer = None
        self.animation_speed = 50

    def update(self, dt):
        if not self.exploded:
            if self.target.rect.collidepoint(self.rect.center):
                self.vel = Vector(0, 0)
                self.exploded = True
                self.image = self.explosion_animation[self.animation_index]
                self.rect = self.image.get_rect()
                self.pos = Vector(self.target.rect.center)

                self.rect.center = self.pos
                self.radius = self.exp_radius
                self.animation_timer = pg.time.get_ticks()

            if self.exploded:
                collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)
                # print collision_group
                for creep in collision_group:
                    creep.take_damage(self.damage)

                return

            self.set_target()

            if self.target.dead:
                self.kill()

            new_vec = self.vel.normalize()
            self.pos.x += new_vec.x * self.speed * dt
            self.pos.y += new_vec.y * self.speed * dt
            self.rect.x = self.pos.x
            self.rect.y = self.pos.y

        else:
            now = pg.time.get_ticks()
            if now - self.animation_timer > self.animation_speed:
                self.animation_timer = now
                if self.animation_index < len(self.explosion_animation) - 1:
                    self.animation_index += 1
                    self.image = self.explosion_animation[self.animation_index]
                else:
                    self.kill()

    def check_collision(self, bullet, other):
        bullet_vector_pos = Vector(bullet.rect.center)
        other_vector_pos = Vector(other.rect.center)
        distance = bullet_vector_pos.distance_to(other_vector_pos)
        if bullet.radius + other.radius > distance:
            return True
        return False


class Beam(Bullet):
    def __init__(self, x, y, level, damage, speed, target, pos_list, vector, atk_radius, tick_frequency):

        super(Beam, self).__init__(x, y, level, damage, speed, target)
        self.orig_image = pg.image.load(path.join(bullet_dir, "fireball.png")).convert_alpha()
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.positions = pos_list
        self.circle_list = []
        self.vector = vector
        self.comparison_vector = Vector(0, -1)
        self.attack_radius = atk_radius
        self.tick_frequency = tick_frequency

        self.last_hit_check = pg.time.get_ticks()
        self.set_origin(self.rect.midbottom)
        self.rotate_beam()

    def set_origin(self, point):
        self.origin = list(point)
        self.rotator = Rotator(self.rect.center, self.origin, 0)

    def rotate_beam(self):
        new_angle = self.vector.angle_to(self.comparison_vector)
        new_center = self.rotator(new_angle, self.origin)
        self.image = pg.transform.rotate(self.orig_image, new_angle )
        self.rect = self.image.get_rect(center=new_center)

    def create_circles(self):
        self.circle_list = []
        for pos, radius in zip(self.positions, self.attack_radius):
            circle = (pos, radius)
            self.circle_list.append(circle)

    def update_pos(self, x, y, damage, target, pos_list, vector, tick_frequency):
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect(midbottom = (x, y))
        self.positions = pos_list
        self.circle_list = []
        self.vector = vector
        self.comparison_vector = Vector(0, -1)
        self.tick_frequency = tick_frequency
        self.set_origin(self.rect.midbottom)
        self.rotate_beam()

    def update(self, dt):
        hit_list = []
        self.create_circles()
        for circle in self.circle_list:
            for creep in self.level.creep_group:
                if self.check_collision(circle, creep):
                    if creep not in hit_list:
                        hit_list.append(creep)
        now = pg.time.get_ticks()
        if now - self.last_hit_check > self.tick_frequency:
            self.last_hit_check = now
            for creep in hit_list:
                creep.take_damage(self.damage)



    def check_collision(self, circle, other):
        circle_vector_pos = circle[0]
        other_vector_pos = Vector(other.rect.center)
        distance = circle_vector_pos.distance_to(other_vector_pos)
        if circle[1] + other.radius > distance:
            return True
        return False


class AimlessBullet(Bullet):

    def __init__(self, x, y, level, damage, speed, direction, bullet_range, target=None):
        super(AimlessBullet, self).__init__(x, y, level, damage, speed, target)

        self.direction = Vector(direction)
        self.direction = self.direction.normalize()
        self.bullet_range = bullet_range
        self.moved_pixels = 0

    def update(self, dt):

        for creep in self.level.creep_group:
            if self.rect.colliderect(creep):
                creep.take_damage(self.damage)
                self.kill()

        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        self.moved_pixels += abs(self.direction.x * self.speed * dt) + abs(self.direction.y * self.speed * dt)
        if self.moved_pixels >= self.bullet_range:
            self.kill()


class Laser(Bullet):
    duration = 700.0  # ms

    def __init__(self, x, y, level, damage, speed, creeps, direction_rect):
        super(Laser, self).__init__(x, y, level, damage, speed, creeps)
        self.rect = direction_rect
        self.creeps = creeps

        self.image = pg.Surface((self.rect.width, self.rect.height))
        self.image.fill(pg.Color("blue"))

        self.has_hit = False
        self.timer = pg.time.get_ticks()

    def update(self, dt):
        if not self.has_hit:
            hit_list = pg.sprite.spritecollide(self, self.creeps, False)
            for creep in hit_list:
                creep.take_damage(self.damage)
            self.has_hit = True

        now = pg.time.get_ticks()
        if now - self.timer > self.duration:
            self.kill()


class Crescent(Bullet):
    def __init__(self, x, y, level, damage, speed, target):
        super(Crescent, self).__init__(x, y, level, damage, speed, target)

        self.orig_image = pg.image.load(path.join(bullet_dir, "crescent.png")).convert_alpha()

        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        self.pos = Vector(x, y)

        self.direction = Vector(0, 0)
        self.comparison_vector = Vector(-1, 0)
        self.set_target()

        self.set_origin(self.rect.center)
        self.rotate_sprite()

        self.hit_list = []

    def update(self, dt):

        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        for creep in self.level.creep_group:
            if self.rect.colliderect(creep.rect):
                if creep not in self.hit_list:
                    creep.take_damage(self.damage)
                    self.hit_list.append(creep)

        if self.rect.x < 0 - self.rect.width or self.rect.x > SCREEN_WIDTH + self.rect.width:
            self.kill()
        if self.rect.y < 0 - self.rect.height or self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.kill()

    def set_target(self):
        x_diff = self.target.pos.x - self.pos.x
        y_diff = self.target.pos.y - self.pos.y
        # print x_diff, y_diff
        self.direction = Vector(x_diff, y_diff).normalize()

    def set_origin(self, point):
        self.origin = list(point)
        self.rotator = Rotator(self.rect.center, self.origin, 0)

    def rotate_sprite(self):
        new_angle = self.direction.angle_to(self.comparison_vector)
        new_center = self.rotator(new_angle, self.origin)
        self.image = pg.transform.rotate(self.orig_image, new_angle)
        self.rect = self.image.get_rect(center=new_center)
        self.pos = Vector(self.rect.x, self.rect.y)

    def draw_debug(self, screen):
        pg.draw.rect(screen, pg.Color("black"), self.rect)






class Rotator(object):
    def __init__(self,center,origin,image_angle=0):
        x_mag = center[0]-origin[0]
        y_mag = center[1]-origin[1]
        self.radius = math.hypot(x_mag,y_mag)
        self.start_angle = math.atan2(-y_mag,x_mag)-math.radians(image_angle)

    def __call__(self,angle,origin):
        new_angle = math.radians(angle)+self.start_angle
        new_x = origin[0] + self.radius*math.cos(new_angle)
        new_y = origin[1] - self.radius*math.sin(new_angle)
        return (new_x,new_y)