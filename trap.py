import pygame as pg
from os import pardir, path

trap_dir = path.join(path.dirname(__file__), "assets", "traps")
Vector = pg.math.Vector2


class Trap(pg.sprite.Sprite):
    name = ""
    damage = 0
    cost = 0
    def __init__(self, x, y, level):
        super(Trap, self).__init__()
        # self.image = pg.image.load(path.join(trap_dir, "mine.png")).convert_alpha()
        # self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = Vector(x, y)
        self.level = level
        self.creeps = self.level.creep_group

    def update(self, dt):
        pass


class Mine(Trap):
    name = "Mine"
    damage = 80
    cost = 300

    def __init__(self, x, y, level):
        super(Mine, self).__init__(x, y, level)

        self.image = pg.image.load(path.join(trap_dir, "trap1.png")).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt):
        for creep in self.creeps:
            if self.rect.colliderect(creep):
                creep.health -= self.damage
                self.kill()
