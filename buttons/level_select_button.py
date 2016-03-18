import pygame as pg


class LevelButton(pg.sprite.Sprite):
    def __init__(self, image, x, y, parent, level_object):
        super(LevelButton, self).__init__()

        self.image = pg.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.parent = parent
        self.level = level_object


    def get_clicked(self):
        self.parent.persist["current_level"] = self.level
        self.parent.done = True
