import pygame as pg
from base_state import GameState
from buttons.level_select_button import LevelButton
from os import pardir, path
from constants import WHITE

level_dir = path.join(path.dirname(__file__), pardir, "assets", "levels")
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")


class LevelSelect(GameState):
    def __init__(self):
        super(LevelSelect, self).__init__()


        self.level_list = [level_dir + "\map.tmx", level_dir + "\map2.tmx"]
        self.wave_list = [[[[0, 0], [1, 1, 1, 1, 1, 1, 1], [2]],
                          [[1, 1], [2, 2]],
                          [[1, 1], [2, 2]],
                          [[1, 1], [2, 2]],
                          [[1, 1], [2, 2]]
                          ],
                          [[[0, 0, 0], [1, 1]], [[1, 2], [2, 2]]]
                         ]

        self.money_list = [1000, 2000]

        self.level_1_button = LevelButton(ui_dir + "\close_button.png", 200, 200, self, self.level_list[0], self.wave_list[1], self.money_list[0])

        self.level_2_button = LevelButton(ui_dir + "\close_button.png", 200, 500, self, self.level_list[1], self.wave_list[0], self.money_list[1])

        self.next_state = "GAME"

    def startup(self, persistent):
        pass

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()
            if self.level_1_button.rect.collidepoint(x, y):
                self.level_1_button.get_clicked()
            if self.level_2_button.rect.collidepoint(x, y):
                self.level_2_button.get_clicked()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(WHITE)
        screen.blit(self.level_1_button.image, self.level_1_button.rect)
        screen.blit(self.level_2_button.image, self.level_2_button.rect)