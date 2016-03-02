import pygame as pg
from base_state import GameState
from os import path, pardir
import Queue
Vector = pg.math.Vector2

from level import Level

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
tower_dir = path.join(path.dirname(__file__), pardir, "assets", "towers")


class GamePlay(GameState):
    def __init__(self):
        super(GamePlay, self).__init__()
        self.next_state = "MENU"

        self.ui = pg.image.load(path.join(ui_dir, "uitemplate.png")).convert_alpha()
        self.tower_ui_1 = pg.image.load(path.join(ui_dir, "tower_1_button.png")).convert_alpha()
        self.tower_ui_1_rect = self.tower_ui_1.get_rect(topleft = (0+21, 512+19))

        self.tower_ui_2 = pg.image.load(path.join(ui_dir, "tower_2_button.png")).convert_alpha()
        self.tower_ui_2_rect = self.tower_ui_2.get_rect(topleft = (0+110, 512+19))

        self.tower_ui_3 = pg.image.load(path.join(ui_dir, "tower_3_button.png")).convert_alpha()
        self.tower_ui_3_rect = self.tower_ui_3.get_rect(topleft=(0+193, 512+19))

        self.tower_ui_4 = pg.image.load(path.join(ui_dir, "tower_4_button.png")).convert_alpha()
        self.tower_ui_4_rect = self.tower_ui_4.get_rect(topleft=(0+280, 512+19))

        self.tower_ui_5 = pg.image.load(path.join(ui_dir, "tower_5_button.png")).convert_alpha()
        self.tower_ui_5_rect = self.tower_ui_5.get_rect(topleft=(0+363, 512+19))

        self.trap_ui_1 = pg.image.load(path.join(ui_dir, "trap_1_button.png")).convert_alpha()
        self.trap_ui_1_rect = self.trap_ui_1.get_rect(topleft=(0 + 440, 512 + 19))

        self.button_1 = pg.image.load(path.join(ui_dir, "upgrade_button.png")).convert_alpha() # Up damage
        self.button_1_rect = self.button_1.get_rect()

        self.button_2 = pg.image.load(path.join(ui_dir, "upgrade_button_2.png")).convert_alpha() # Up range
        self.button_2_rect = self.button_2.get_rect()

        self.button_3 = pg.image.load(path.join(ui_dir, "upgrade_button_3.png")).convert_alpha() # Up firetower DPS

        self.button_4 = pg.image.load(path.join(ui_dir, "sell_button.png")).convert_alpha() # Sell Tower
        self.button_4_rect = self.button_4.get_rect()

        self.selected_tower = None
        self.highlighted_tower = None

        self.selected_trap = None

        self.tower_info = []
        self.money_ui = None
        self.level = None

        self.props = {}

    def startup(self, persistent):
        self.level = Level()

        self.selected_tower = None
        self.highlighted_tower = None

        node_list = []
        for x in range(self.level.tile_renderer.tmx_data.width):
            for y in range(self.level.tile_renderer.tmx_data.height):
                tile_property = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if "node" in tile_property:
                    if "node" not in node_list:
                        node_list.append("node")

                for z in range(2, 5):
                    if "node" + str(z) in tile_property:
                        if "node" + str(z) not in node_list:
                            node_list.append("node" + str(z))

        for node in node_list:
            self.create_pathifinding(node)





    def create_pathifinding(self, node):
        self.tile_list = []

        start = 0
        end = 0
        for x in range(self.level.tile_renderer.tmx_data.width):
            for y in range(self.level.tile_renderer.tmx_data.height):
                tile_property = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if node in tile_property:
                    if tile_property[node] == "True":
                        self.tile_list.append([x, y])
                if "bridge" in tile_property:
                    if tile_property["bridge"] == "True":
                        print x, y
                        self.tile_list.append([x, y])

        start = self.tile_list[0]
        end = self.tile_list[-1]
        pathing = Queue.Queue()
        pathing.put(start)
        came_from = {}
        came_from[str(start)] = None
        while not pathing.empty():
            current = pathing.get()
            print current

            if current == end:
                break

            for next_tile in self.get_neighbors(current):
                if str(next_tile) not in came_from:
                    pathing.put(next_tile)
                    came_from[str(next_tile)] = current

        current = end
        final_path = [current]
        while current != start:
            current = came_from[str(current)]
            final_path.append(current)
        final_path.reverse()
        # print final_path

        self.pathing = final_path
        self.level.creep_path.append(self.pathing)


    def get_neighbors(self, node):
        dirs = [[1, 0], [0, 1], [-1, 0], [0, -1]]
        result = []
        for direct in dirs:
            neighbor = [node[0] + direct[0], node[1] + direct[1]]
            if neighbor in self.tile_list:
                result.append(neighbor)
        return result

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True

        if event.type == pg.MOUSEMOTION:

            x, y = pg.mouse.get_pos()
            x = x // self.level.tile_renderer.tmx_data.tilewidth
            y = y // self.level.tile_renderer.tmx_data.tileheight
            try:
                self.props = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                self.cursor_x = x
                self.cursor_y = y

            # pytmx library throws "Exception" when trying to access a non existent tile
            except Exception:
                # print "Tile at location " + "(" + str(x) + " / " + str(y) + ") doesnt exist"
                self.props = {}

        if event.type == pg.MOUSEBUTTONDOWN:
            pressed = pg.mouse.get_pressed()
            if pressed[0]:
                x, y = pg.mouse.get_pos()

                self.select_trap(x, y)
                self.place_trap(x, y)

                self.select_tower(x, y)
                self.upgrade_tower(x, y)
                self.place_tower(x, y)

            if pressed[1]:
                print "middle"
            if pressed[2]:
                self.selected_tower = None
                self.highlighted_tower = None

                self.selected_trap = None

    def update(self, dt):
        if self.level.game_over:
            self.done = True
        self.update_money()
        self.level.update(dt)

    def update_money(self):
        self.money_ui = self.create_text(str(self.level.money) + " Gold")

    def create_tower_info(self):
        self.tower_info = []
        name = self.highlighted_tower.name
        attack = self.highlighted_tower.damage
        range = self.highlighted_tower.radius
        up_cost = self.highlighted_tower.upgrade_cost
        if type(self.highlighted_tower).__name__ == "FireTower":
            tick_frequency = self.highlighted_tower.tick_frequency

        if self.highlighted_tower.tier <= self.highlighted_tower.max_tier:
            self.tower_info.append(self.create_text(str(name)))
            self.tower_info.append(self.create_text("Damage: " + str(attack)))
            if type(self.highlighted_tower).__name__ == "FireTower":
                self.tower_info.append(self.create_text("Damage every " + str(tick_frequency) + "ms"))
            else:
                self.tower_info.append(self.create_text("Range: " + str(range)))
            self.tower_info.append(self.create_text("Cost to Upgrade: " + str(up_cost)))
        else:
            self.tower_info.append(self.create_text(str(name)))
            self.tower_info.append(self.create_text("Damage: " + str(attack)))
            if type(self.highlighted_tower).__name__ == "FireTower":
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

            if self.props["can_build"] == "True" and self.selected_tower is not None:
                radius = self.level.tower_list[self.selected_tower].radius
                pg.draw.rect(self.screen, pg.Color("black"), [self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth,
                                                              self.cursor_y * self.level.tile_renderer.tmx_data.tileheight,
                                                              self.level.tile_renderer.tmx_data.tilewidth,
                                                              self.level.tile_renderer.tmx_data.tileheight
                                                              ], 1
                             )

                pg.draw.circle(screen, pg.Color("black"), ([self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth + 16,
                                                                  self.cursor_y * self.level.tile_renderer.tmx_data.tileheight + 16]), radius, 1)
                screen.blit(pg.image.load(path.join(tower_dir, "tower" + str(self.selected_tower + 1) + ".png")), (self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth,
                                                                                                                   self.cursor_y * self.level.tile_renderer.tmx_data.tileheight))
        except KeyError:
            pass
            # print "Key 'can_build' not in dictionary 'self.props'"
            # print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def draw_ui(self, screen):
        screen.blit(self.ui, (0, 512))
        screen.blit(self.tower_ui_1, (0+21, 512+19))
        screen.blit(self.tower_ui_2, (0+110, 512+19))
        screen.blit(self.tower_ui_3, (0+193, 512+19))
        screen.blit(self.tower_ui_4, (0+277, 512+19))
        screen.blit(self.tower_ui_5, (0+363, 512+19))
        screen.blit(self.trap_ui_1, (self.trap_ui_1_rect))




        if self.highlighted_tower is not None:

            pg.draw.rect(screen, pg.Color("black"), [self.highlighted_tower.rect.x, self.highlighted_tower.rect.y,
                                                     self.highlighted_tower.rect.width, self.highlighted_tower.rect.height], 1)

            self.highlighted_tower.draw2(screen)

            if self.highlighted_tower.tier <= self.highlighted_tower.max_tier:
                screen.blit(self.button_1, (self.highlighted_tower.rect.x - self.button_1_rect.width - 1, self.highlighted_tower.rect.y - self.button_1_rect.height))
                self.button_1_rect.x, self.button_1_rect.y = (self.highlighted_tower.rect.x - self.button_1_rect.width - 1, self.highlighted_tower.rect.y - self.button_1_rect.height)

                if type(self.highlighted_tower).__name__ == "FireTower":
                    screen.blit(self.button_3, (self.highlighted_tower.rect.x + self.highlighted_tower.rect.width + 1, self.highlighted_tower.rect.y - self.button_2_rect.height))
                    self.button_2_rect.x, self.button_2_rect.y = (self.highlighted_tower.rect.x + self.highlighted_tower.rect.width + 1, self.highlighted_tower.rect.y - self.button_2_rect.height)

                else:
                    screen.blit(self.button_2, (self.highlighted_tower.rect.x + self.highlighted_tower.rect.width + 1, self.highlighted_tower.rect.y - self.button_2_rect.height))
                    self.button_2_rect.x, self.button_2_rect.y = (self.highlighted_tower.rect.x + self.highlighted_tower.rect.width + 1, self.highlighted_tower.rect.y - self.button_2_rect.height)

                screen.blit(self.button_4, (self.highlighted_tower.rect.x + 1, self.highlighted_tower.rect.y - self.button_4_rect.height))
                self.button_4_rect.x, self.button_4_rect.y = (self.highlighted_tower.rect.x + 1, self.highlighted_tower.rect.y - self.button_4_rect.height)

            self.create_tower_info()

            if self.highlighted_tower.rect.x < 400:
                pg.draw.rect(screen, pg.Color(255, 233, 114), [800-192, 450 - 2, 192, 200])
                for index, text in enumerate(self.tower_info):
                    rect = text.get_rect()
                    screen.blit(text, (800-192 + 10, 450 + 20 + index * (rect.height + 2)))

            elif self.highlighted_tower.rect.x >= 400:
                pg.draw.rect(screen, pg.Color(255, 233, 114), [0, 312 - 2, 192, 200])
                for index, text in enumerate(self.tower_info):
                    rect = text.get_rect()
                    screen.blit(text, (0 + 10, 312 + 20 + index * (rect.height + 2)))

        if self.money_ui is not None:
            screen.blit(self.money_ui, (800-192 + 10, 512 + 40))

        for x in range(0, 3):
            for location in self.level.creep_path[x]:
                pg.draw.rect(screen, pg.Color("black"), [location[0] * 32, location[1] * 32, 32, 32], 1)
    def draw(self, screen):
        screen.fill(pg.Color("white"))
        self.level.draw(screen)
        self.draw_tower_preview(screen)
        self.draw_ui(screen)

    def select_tower(self, x, y):
        if self.highlighted_tower is None and self.selected_trap is None:
            if self.tower_ui_1_rect.collidepoint(x, y):
                self.selected_tower = 0

            elif self.tower_ui_2_rect.collidepoint(x, y):
                self.selected_tower = 1

            elif self.tower_ui_3_rect.collidepoint(x, y):
                self.selected_tower = 2

            elif self.tower_ui_4_rect.collidepoint(x, y):
                self.selected_tower = 3

            elif self.tower_ui_5_rect.collidepoint(x, y):
                self.selected_tower = 4

        if self.selected_tower is None and self.selected_trap is None:
            for tower in self.level.tower_group:
                if tower.rect.collidepoint(x, y):
                    self.highlighted_tower = tower

    def select_trap(self, x, y):
        if self.highlighted_tower is None and self.selected_tower is None and self.selected_trap is None:
            if self.trap_ui_1_rect.collidepoint(x, y):
                self.selected_trap = 0

    def upgrade_tower(self, x, y):
        if self.highlighted_tower is not None:
            if self.level.money >= self.highlighted_tower.upgrade_cost and self.highlighted_tower.tier <= self.highlighted_tower.max_tier:
                if self.button_1_rect.collidepoint(x, y):
                    self.highlighted_tower.upgrade_attack()
                    self.level.money -= self.highlighted_tower.upgrade_cost
                elif self.button_2_rect.collidepoint(x, y):
                    self.level.money -= self.highlighted_tower.upgrade_cost
                    if type(self.highlighted_tower).__name__ == "FireTower":
                        self.highlighted_tower.upgrade_damage_tick_frequency()
                    else:
                        self.highlighted_tower.upgrade_radius()

            if self.button_4_rect.collidepoint(x, y):
                self.sell_tower()

    def sell_tower(self):
        self.level.money += self.highlighted_tower.cost * 0.8
        self.level.money = int(self.level.money)
        self.highlighted_tower.kill()
        self.highlighted_tower = None

    def place_trap(self, x, y):
        try:
            if self.selected_trap is not None and self.props["can_build"] == "False":
                allowed = True
                for trap in self.level.trap_group:
                    if trap.rect.collidepoint(x, y):
                        allowed = False
                        break

                if allowed:
                    if self.selected_trap >= 0:
                        if self.level.money >= self.level.trap_list[self.selected_trap].cost:
                            self.create_trap(x, y, self.selected_trap)
                            self.level.money -= self.level.trap_list[self.selected_trap].cost

        except KeyError:
            print "Key 'can_build' not in dictionary 'self.props'"
            print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def place_tower(self, x, y):
        try:
            if self.selected_tower is not None and self.props["can_build"] == "True":
                allowed = True
                for tower in self.level.tower_group:
                    if tower.rect.collidepoint(x, y):
                        allowed = False
                        break
                if allowed:
                    if self.selected_tower >= 0:
                        if self.level.money >= self.level.tower_list[self.selected_tower].cost:
                            self.create_tower(x, y, self.selected_tower)
                            self.level.money -= self.level.tower_list[self.selected_tower].cost


        #Catch the keyerror in case the self.props dict wasnt updated yet
        except KeyError:
            print "Key 'can_build' not in dictionary 'self.props'"
            print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def create_tower(self, x, y, selected):
        x = x // self.level.tile_renderer.tmx_data.tilewidth
        y = y // self.level.tile_renderer.tmx_data.tileheight
        tower = self.level.tower_list[selected](x * self.level.tile_renderer.tmx_data.tilewidth, y * self.level.tile_renderer.tmx_data.tileheight, self.level)
        self.level.tower_group.add(tower)

    def create_trap(self, x, y, selected):
        x = x // self.level.tile_renderer.tmx_data.tilewidth
        y = y // self.level.tile_renderer.tmx_data.tileheight
        trap = self.level.trap_list[selected](x * self.level.tile_renderer.tmx_data.tilewidth, y * self.level.tile_renderer.tmx_data.tileheight, self.level)
        self.level.trap_group.add(trap)







