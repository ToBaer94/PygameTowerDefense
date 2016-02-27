import pygame as pg
from os import path, pardir
import math
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
            self.target.health -= self.damage
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

        self.exploded = False
        self.exp_radius = 32
        self.exp_image = pg.image.load(path.join(bullet_dir, "bullet_explo.png")).convert_alpha()
        self.explosion_time = None

    def update(self, dt):
        if not self.exploded:
            if self.target.rect.collidepoint(self.rect.center):
                self.vel = Vector(0, 0)
                self.exploded = True
                self.image = self.exp_image
                self.rect = self.image.get_rect()
                self.pos = Vector(self.target.rect.center)

                self.rect.center = self.pos
                self.radius = self.exp_radius
                self.explosion_time = pg.time.get_ticks()

            if self.exploded:
                collision_group = pg.sprite.spritecollide(self, self.creeps, False, self.check_collision)
                print collision_group
                for creep in collision_group:
                    creep.health -= 1

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
            if now - self.explosion_time > 500:
                self.kill()

    def check_collision(self, bullet, other):
        bullet_vector_pos = Vector(bullet.rect.center)
        other_vector_pos = Vector(other.rect.center)
        distance = bullet_vector_pos.distance_to(other_vector_pos)
        print bullet.radius + other.radius, distance
        if bullet.radius + other.radius > distance:
            return True
        return False

    def draw2(self, screen):
        pg.draw.circle(screen, pg.Color("black"), self.rect.center, self.radius, 1)


class Beam(Bullet):
    def __init__(self, x, y, level, damage, speed, target, pos_list, vector, atk_radius, tick_frequency):

        super(Beam, self).__init__(x, y, level, damage, speed, target)
        self.orig_image = pg.image.load(path.join(bullet_dir, "fireball.png")).convert_alpha()
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect(midbottom = (x, y))
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
                creep.health -= 1



    def check_collision(self, circle, other):
        circle_vector_pos = circle[0]
        other_vector_pos = Vector(other.rect.center)
        distance = circle_vector_pos.distance_to(other_vector_pos)
        if circle[1] + other.radius > distance:
            return True
        return False


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