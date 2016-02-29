import pygame as pg
from button import Button
from os import path, pardir
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")


rules_button_image = path.join(ui_dir, "rules_button.png")


class RulesButton(Button):
    def __init__(self, x, y, parent):
        super(RulesButton, self).__init__(rules_button_image, x, y, parent)
        self.image = pg.image.load(rules_button_image).convert_alpha()

    def get_clicked(self):
        self.parent.next_state = "RULES"
        self.parent.done = True