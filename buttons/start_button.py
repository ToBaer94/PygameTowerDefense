import pygame as pg
from button import Button
from os import path, pardir
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")

start_button_image = path.join(ui_dir, "start_game_button.png")


class StartButton(Button):
    def __init__(self, x, y, parent):
        super(StartButton, self).__init__(start_button_image, x, y, parent)
        self.image = pg.image.load(start_button_image).convert_alpha()

    def get_clicked(self):
        self.parent.next_state = "LEVEL"
        self.parent.done = True