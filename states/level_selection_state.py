import pygame as pg
import json, pickle
from base_state import GameState
from buttons.level_select_button import LevelButton
from levels import Level01, Level02, Level03, Level04, Level05
from os import pardir, path


level_dir = path.join(path.dirname(__file__), pardir, "assets", "levels")
ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")


class LevelSelect(GameState):
    def __init__(self):
        super(LevelSelect, self).__init__()

        self.background_image = pg.image.load(path.join(ui_dir, "background.png")).convert_alpha()

        self.Level01_button = LevelButton(ui_dir + "\level_1_button.png", 50, 50, self, Level01)
        self.Level02_button = LevelButton(ui_dir + "\level_2_button.png", 50, 150, self, Level02)
        self.Level03_button = LevelButton(ui_dir + "\level_3_button.png", 50, 250, self, Level03)
        self.Level04_button = LevelButton(ui_dir + "\level_4_button.png", 50, 350, self, Level04)
        self.Level05_button = LevelButton(ui_dir + "\level_5_button.png", 50, 450, self, Level05)

        self.level_button_list = [self.Level01_button, self.Level02_button, self.Level03_button, self.Level04_button,
                                  self.Level05_button]

        self.save_game = 0

        self.unlocked_levels = []

        self.next_state = "GAME"

    def startup(self, persistent):
        self.next_state = "GAME"
        self.persist = persistent

        self.load_save()

        self.set_unlocked_levels()

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = pg.mouse.get_pos()

            for button in self.unlocked_levels:
                if button.rect.collidepoint(x, y):
                    button.get_clicked()

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.next_state = "MENU"
                self.done = True

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))

        for button in self.unlocked_levels:
            screen.blit(button.image, button.rect)

    def load_save(self):
        try:
            with open("save_game.txt", "r") as save_game:
                self.save_game = json.load(save_game)
            print "save loaded"

        except IOError:
            print "No save file found"

        if self.save_game:
            self.persist["save_game"] = self.save_game

    def set_unlocked_levels(self):
        self.unlocked_levels = []
        self.unlocked_levels.append(self.level_button_list[0])
        for level_name, status in self.persist["save_game"].iteritems():
            if status == 1:
                if level_name == "Level01":
                    self.unlocked_levels.append(self.level_button_list[1])
                if level_name == "Level02":
                    self.unlocked_levels.append(self.level_button_list[2])
                if level_name == "Level03":
                    self.unlocked_levels.append(self.level_button_list[3])
                if level_name == "Level04":
                    self.unlocked_levels.append(self.level_button_list[4])