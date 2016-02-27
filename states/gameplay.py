import pygame as pg
from base_state import GameState
from os import path, pardir
import Queue
Vector = pg.math.Vector2

from level import Level

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
tower_dir = path.join(path.dirname(__file__), pardir, "assets", "towers")


class Button(object):
    def __init__(self):
        super(Button, self).__init__()
        self.image = "tower_1_button.png"
        
# path.join(ui_dir,


class GamePlay(GameState):
    def __init__(self):
        super(GamePlay, self).__init__()
        self.next_state = "LEVEL"   

        self.ui = pg.image.load(path.join(ui_dir, "uitemplate.png")).convert_alpha()
        self.tower_ui_1 = pg.image.load(path.join(ui_dir, "tower_1_button.png")).convert_alpha()
        self.tower_ui_1_rect = self.tower_ui_1.get_rect(topleft = (0+21, 512+19))

        self.tower_ui_2 = pg.image.load(path.join(ui_dir, "tower_2_button.png")).convert_alpha()
        self.tower_ui_2_rect = self.tower_ui_2.get_rect(topleft = (0+110, 512+19))

        self.tower_ui_3 = pg.image.load(path.join(ui_dir, "tower_2_button.png")).convert_alpha()
        self.tower_ui_3_rect = self.tower_ui_3.get_rect(topleft=(0+193, 512+19))

        self.tower_ui_4 = pg.image.load(path.join(ui_dir, "tower_2_button.png")).convert_alpha()
        self.tower_ui_4_rect = self.tower_ui_3.get_rect(topleft=(0+280, 512+19))

        self.button_1 = pg.image.load(path.join(ui_dir, "upgrade_button.png")).convert_alpha()
        self.button_1_rect = self.button_1.get_rect()

        self.button_2 = pg.image.load(path.join(ui_dir, "upgrade_button_2.png")).convert_alpha()
        self.button_2_rect = self.button_2.get_rect()

        self.button_3 = pg.image.load(path.join(ui_dir, "upgrade_button_3.png")).convert_alpha()



        self.selected = None
        self.selected_tower = None

        self.tower_info = []
        self.money_ui = None
        self.level = None

    def startup(self, persistent):
        self.level = Level()

        self.tile_list = []
        start = 0
        end = 0
        for x in range(self.level.tile_renderer.tmx_data.width):
            for y in range(self.level.tile_renderer.tmx_data.height):
                tile_property = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 1)
                if "node" in tile_property:
                    if tile_property["node"] == "True":
                        self.tile_list.append([x, y])
                tile_property_2 = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if "start" in tile_property_2:
                    start = [x, y]
                if "end" in tile_property_2:
                    end = [x, y]
        #print self.tile_list
        #print start

        pathing = Queue.Queue()
        pathing.put(start)
        came = {}
        came[str(start)] = None
        while not pathing.empty():
            current = pathing.get()

            if current == end:
                break

            for next in self.get_neighbors(current):
                if str(next) not in came:
                    pathing.put(next)
                    came[str(next)] = current

        current = end
        final_path = [current]
        while current != start:
            current = came[str(current)]
            final_path.append(current)
        final_path.reverse()
        print final_path

        self.pathing = final_path
        self.level.creep_path = self.pathing





    def get_neighbors(self, node):
        dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        result = []
        for direct in dirs:
            neighbor = [node[0] + direct[0], node[1] + direct[1]]
            if neighbor in self.tile_list:
                result.append(neighbor)
        return result





            #self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 1)

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        if event.type == pg.MOUSEMOTION:

            x, y = pg.mouse.get_pos()
            x = x // self.level.tile_renderer.tmx_data.tilewidth
            y = y // self.level.tile_renderer.tmx_data.tileheight
            try:
                self.props = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 1)
                self.cursor_x = x
                self.cursor_y = y

            # pytmx library throws "Exception" when trying to access a non existent tile
            except Exception:
                self.props = {}

        if event.type == pg.MOUSEBUTTONDOWN:
            pressed = pg.mouse.get_pressed()
            if pressed[0]:
                x, y = pg.mouse.get_pos()

                self.select_tower(x, y)
                self.upgrade_tower(x, y)
                self.place_tower(x, y)

            if pressed[1]:
                print "middle"
            if pressed[2]:
                self.selected = None
                self.selected_tower = None

    def update(self, dt):
        if self.level.game_over:
            self.done = True
        self.update_money()
        self.level.update(dt)

    def update_money(self):
        self.money_ui = self.create_text(str(self.level.money) + " shekels")

    def create_tower_info(self):
        self.tower_info = []
        attack = self.selected_tower.damage
        range = self.selected_tower.radius
        up_cost = self.selected_tower.upgrade_cost
        if type(self.selected_tower).__name__ == "FireTower":
            tick_frequency = self.selected_tower.tick_frequency

        if self.selected_tower.tier <= self.selected_tower.max_tier:
            self.tower_info.append(self.create_text("Damage: " + str(attack)))
            if type(self.selected_tower).__name__ == "FireTower":
                self.tower_info.append(self.create_text("Damage every " + str(tick_frequency) + "ms"))
            else:
                self.tower_info.append(self.create_text("Range: " + str(range)))
            self.tower_info.append(self.create_text("Cost to Upgrade: " + str(up_cost)))
        else:
            self.tower_info.append(self.create_text("Damage: " + str(attack)))
            if type(self.selected_tower).__name__ == "FireTower":
                self.tower_info.append(self.create_text("Damage every " + str(tick_frequency) + "ms"))
            else:
                self.tower_info.append(self.create_text("Range: " + str(range)))
            self.tower_info.append(self.create_text("Max upgrade tier reached"))

    def create_text(self, text):
        text = str(text)
        font = pg.font.Font(None, 24)
        render_text = font.render(text, True, pg.Color("black"))
        return render_text

    def draw_tower_preview(self, screen):
        try:

            if self.props["can_build"] == "True" and self.selected is not None:
                radius = self.level.tower_list[self.selected].radius
                pg.draw.rect(self.screen, pg.Color("black"), [self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth,
                                                              self.cursor_y * self.level.tile_renderer.tmx_data.tileheight,
                                                              self.level.tile_renderer.tmx_data.tilewidth,
                                                              self.level.tile_renderer.tmx_data.tileheight
                                                              ], 1
                             )

                pg.draw.circle(screen, pg.Color("black"), ([self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth + 16,
                                                                  self.cursor_y * self.level.tile_renderer.tmx_data.tileheight + 16]), radius, 1)
                screen.blit(pg.image.load(path.join(tower_dir, "tower" + str(self.selected+1) + ".png")), (self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth,
                                                                  self.cursor_y * self.level.tile_renderer.tmx_data.tileheight))
        except KeyError:
            pass

    def draw_ui(self, screen):
        screen.blit(self.ui, (0, 512))
        screen.blit(self.tower_ui_1, (0+21, 512+19))
        screen.blit(self.tower_ui_2, (0+110, 512+19))
        screen.blit(self.tower_ui_3, (0+193, 512+19))
        screen.blit(self.tower_ui_4, (0+280, 512+19))

        if self.money_ui is not None:
            screen.blit(self.money_ui, (600, 512 + 40))


        if self.selected_tower is not None:

            pg.draw.rect(screen, pg.Color("black"), [self.selected_tower.rect.x, self.selected_tower.rect.y,
                                                     self.selected_tower.rect.width, self.selected_tower.rect.height], 1)

            self.selected_tower.draw2(screen)

            if self.selected_tower.tier <= self.selected_tower.max_tier:
                screen.blit(self.button_1, (self.selected_tower.rect.x - self.button_1_rect.width, self.selected_tower.rect.y - self.button_1_rect.height))
                self.button_1_rect.x, self.button_1_rect.y = (self.selected_tower.rect.x - self.button_1_rect.width, self.selected_tower.rect.y - self.button_1_rect.height)

                if type(self.selected_tower).__name__ == "FireTower":
                    screen.blit(self.button_3, (self.selected_tower.rect.x + self.selected_tower.rect.width, self.selected_tower.rect.y- self.button_2_rect.height))
                    self.button_2_rect.x, self.button_2_rect.y = (self.selected_tower.rect.x + self.selected_tower.rect.width, self.selected_tower.rect.y- self.button_2_rect.height)

                else:
                    screen.blit(self.button_2, (self.selected_tower.rect.x + self.selected_tower.rect.width, self.selected_tower.rect.y- self.button_2_rect.height))
                    self.button_2_rect.x, self.button_2_rect.y = (self.selected_tower.rect.x + self.selected_tower.rect.width, self.selected_tower.rect.y- self.button_2_rect.height)

            self.create_tower_info()

            for index, text in enumerate(self.tower_info):
                rect = text.get_rect()
                screen.blit(text, (363, 512 + 20 + index * (rect.height + 2)))
        #for location in self.pathing:
         #   pg.draw.rect(screen, pg.Color("black"), [location[0] * 32, location[1] * 32, 32, 32], 1)
    def draw(self, screen):
        screen.fill(pg.Color("white"))
        self.level.draw(screen)
        self.draw_tower_preview(screen)
        self.draw_ui(screen)

    def select_tower(self, x, y):
        if self.selected_tower is None:
            if self.tower_ui_1_rect.collidepoint(x, y):
                self.selected = 0

            elif self.tower_ui_2_rect.collidepoint(x, y):
                self.selected = 1

            elif self.tower_ui_3_rect.collidepoint(x, y):
                self.selected = 2

            elif self.tower_ui_4_rect.collidepoint(x, y):
                self.selected = 3

        if self.selected is None:
            for tower in self.level.tower_group:
                if tower.rect.collidepoint(x, y):
                    self.selected_tower = tower

    def upgrade_tower(self, x, y):
        if self.selected_tower is not None:
            if self.level.money >= self.selected_tower.upgrade_cost and self.selected_tower.tier <= self.selected_tower.max_tier:
                if self.button_1_rect.collidepoint(x, y):
                    self.selected_tower.upgrade_attack()
                    self.level.money -= self.selected_tower.upgrade_cost
                elif self.button_2_rect.collidepoint(x, y):
                    self.level.money -= self.selected_tower.upgrade_cost
                    if type(self.selected_tower).__name__ == "FireTower":
                        self.selected_tower.upgrade_damage_tick_frequency()
                    else:
                        self.selected_tower.upgrade_radius()


    def place_tower(self, x, y):
        try:
            if self.selected is not None and self.props["can_build"] == "True":
                allowed = True
                for tower in self.level.tower_group:
                    if tower.rect.collidepoint(x, y):
                        allowed = False
                        break
                if allowed:
                    if self.selected >= 0:
                        if self.level.money >= self.level.tower_list[self.selected].cost:
                            self.create_tower(x, y, self.selected)
                            self.level.money -= self.level.tower_list[self.selected].cost


        #Catch the keyerror in case the self.props dict wasnt updated yet
        except KeyError:
            print "yey"

    def create_tower(self, x, y, selected):
        x = x // self.level.tile_renderer.tmx_data.tilewidth
        y = y // self.level.tile_renderer.tmx_data.tileheight
        tower = self.level.tower_list[selected](x * self.level.tile_renderer.tmx_data.tilewidth, y * self.level.tile_renderer.tmx_data.tileheight, self.level)
        self.level.tower_group.add(tower)






