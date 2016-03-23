from os import path, pardir
import pygame as pg

from base_state import GameState

from buttons.exit_button import ExitButton
from buttons.start_button import StartButton
from buttons.rules_button import RulesButton

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")


class MenuState(GameState):

    def __init__(self):
        super(MenuState, self).__init__()

        self.next_state = "LEVEL"

        self.start_button = StartButton(200, 100, self)
        self.tutorial_button = RulesButton(200, 250, self)
        self.exit_button = ExitButton(200, 400, self)

        self.background_image = pg.image.load(path.join(ui_dir, "background.png")).convert_alpha()

        self.button_list = [self.start_button, self.tutorial_button, self.exit_button]

    def startup(self, persistent):
        self.persist["save_game"] = {"Level01": 0, "Level02": 0, "Level03": 0, "Level04": 0, "Level05": 0}

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            for button in self.button_list:
                if button.rect.collidepoint(pos):
                    button.get_clicked()

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))

        for button in self.button_list:
            screen.blit(button.image, (button.rect.x, button.rect.y))