import pygame as pg
from button import Button

from os import path, pardir
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")

exit_button_image = path.join(ui_dir, "exit.png")


class ExitButton(Button):
    def __init__(self, x, y, parent):
        super(ExitButton, self).__init__(exit_button_image, x, y, parent)

    def get_clicked(self):
        self.parent.quit = True
