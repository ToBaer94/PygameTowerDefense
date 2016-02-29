from os import path, pardir

import pygame as pg

from base_state import GameState
from buttons.button import Button

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
close_button = path.join(ui_dir, "close_button.png")


class RuleState(GameState):

    def __init__(self):
        super(RuleState, self).__init__()

        self.next_state = "MENU"
        self.rules_image = pg.image.load(path.join(ui_dir, "rules.png")).convert_alpha()
        self.close_button = Button(close_button, 70, 500, self)

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            if self.close_button.rect.collidepoint(pos):
                self.done = True

    def draw(self, screen):
        screen.fill(pg.Color("white"))
        screen.blit(self.rules_image, (0, 0))
        screen.blit(self.close_button.image, self.close_button.rect)


