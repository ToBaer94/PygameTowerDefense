import pygame as pg
from base_state import GameState
from buttons.level_select_button import LevelButton
from levels import Level01, Level02, Level03
from os import pardir, path


level_dir = path.join(path.dirname(__file__), pardir, "assets", "levels")
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")


class LevelSelect(GameState):
    def __init__(self):
        super(LevelSelect, self).__init__()

        self.background_image = pg.image.load(path.join(ui_dir, "background.png")).convert_alpha()

        self.level_1_button = LevelButton(ui_dir + "\level_1_button.png", 50, 50, self, Level01)
        self.level_2_button = LevelButton(ui_dir + "\level_2_button.png", 50, 150, self, Level01)
        self.level_3_button = LevelButton(ui_dir + "\level_3_button.png", 50, 250, self, Level01)
        self.level_4_button = LevelButton(ui_dir + "\level_4_button.png", 50, 350, self, Level02)
        self.level_5_button = LevelButton(ui_dir + "\level_5_button.png", 50, 450, self, Level03)

        self.next_state = "GAME"

    def startup(self, persistent):
        self.next_state = "GAME"


    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()
            if self.level_1_button.rect.collidepoint(x, y):
                self.level_1_button.get_clicked()
            if self.level_2_button.rect.collidepoint(x, y):
                self.level_2_button.get_clicked()
            if self.level_3_button.rect.collidepoint(x, y):
                self.level_3_button.get_clicked()
            if self.level_4_button.rect.collidepoint(x, y):
                self.level_4_button.get_clicked()
            if self.level_5_button.rect.collidepoint(x, y):
                self.level_5_button.get_clicked()

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = "MENU"
                self.done = True

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        screen.blit(self.level_1_button.image, self.level_1_button.rect)
        screen.blit(self.level_2_button.image, self.level_2_button.rect)
        screen.blit(self.level_3_button.image, self.level_3_button.rect)
        screen.blit(self.level_4_button.image, self.level_4_button.rect)
        screen.blit(self.level_5_button.image, self.level_5_button.rect)