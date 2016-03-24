from os import path, pardir
import pygame as pg

from base_state import GameState
from buttons.button import Button

from constants import BLACK, WHITE

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
close_button = path.join(ui_dir, "close_result_button.png")


class ScoreState(GameState):

    def __init__(self):
        super(ScoreState, self).__init__()

        self.next_state = "LEVEL"

        self.background_image = pg.image.load(path.join(ui_dir, "background.png")).convert_alpha()
        self.result_background_image = pg.image.load(path.join(ui_dir, "result_background.png")).convert_alpha()

        self.close_button = Button(close_button, 230, 480, self)

        self.earned_money = 0
        self.killed_creeps = 0
        self.result = None

        self.result_text = None
        self.money_text = None
        self.creep_text = None

        self.result_text_rect = None
        self.money_text_rect = None
        self.creep_text_rect = None

    def startup(self, persistent):
        self.persist = persistent

        self.result = self.persist["result"]
        self.earned_money = self.persist["earned_money"]
        self.killed_creeps = self.persist["killed_creeps"]

        self.result_text = self.create_text(self.result, 64)
        self.money_text = self.create_text("Gold earned: " + str(self.earned_money))
        self.creep_text = self.create_text("Killed Creeps: " + str(self.killed_creeps))

        self.result_text_rect = self.result_text.get_rect(topleft=(300, 100))
        self.money_text_rect = self.money_text.get_rect(topleft=(300, 200))
        self.creep_text_rect = self.creep_text.get_rect(topleft=(300, 232))

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            if self.close_button.rect.collidepoint(pos):
                self.done = True

    def draw(self, screen):
        screen.blit(self.background_image, (0, 0))
        #screen.fill(WHITE)
        screen.blit(self.result_background_image, (150, 50))
        screen.blit(self.close_button.image, self.close_button.rect)


        if self.money_text and self.creep_text and self.result_text:
            screen.blit(self.result_text, self.result_text_rect)
            screen.blit(self.money_text, self.money_text_rect)
            screen.blit(self.creep_text, self.creep_text_rect)

    def create_text(self, text, size=32):
        text = str(text)
        font = pg.font.Font(None, size)
        render_text = font.render(text, True, BLACK)
        return render_text