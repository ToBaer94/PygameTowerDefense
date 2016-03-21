import pygame as pg
import Queue
from os import path, pardir
from base_state import GameState

from buttons.tower_selection_button import TowerButton
from buttons.trap_selection_button import TrapButton
from buttons.sell_button import SellButton
from buttons.arrow_button import ArrowButton

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_WIDTH, TILE_HEIGHT, UI_COLOR, WHITE, BLACK
from level import Level

Vector = pg.math.Vector2

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
tower_dir = path.join(path.dirname(__file__), pardir, "assets", "towers")
trap_dir = path.join(path.dirname(__file__), pardir, "assets", "traps")


class GamePlay(GameState):
    def __init__(self):
        super(GamePlay, self).__init__()
        self.next_state = "LEVEL"

        self.ui = pg.image.load(path.join(ui_dir, "ui_full_template.png")).convert_alpha()
        self.upgrade_ui = pg.image.load(path.join(ui_dir, "ui_upgrade.png")).convert_alpha()

        self.sniper_button_ui = TowerButton(path.join(ui_dir, "tower_1_button.png"), 0 + 21, 512 + 19, self, 0)
        self.cannon_button_ui = TowerButton(path.join(ui_dir, "tower_2_button.png"), 0 + 110, 512 + 19, self, 1)
        self.explosive_button_ui = TowerButton(path.join(ui_dir, "tower_3_button.png"), 0 + 193, 512 + 19, self, 2)
        self.fire_button_ui = TowerButton(path.join(ui_dir, "tower_4_button.png"), 0 + 280, 512 + 19, self, 3)
        self.slow_button_ui = TowerButton(path.join(ui_dir, "tower_5_button.png"), 0 + 363, 512 + 19, self, 4)
        self.multi_button_ui = TowerButton(path.join(ui_dir, "tower_6_button.png"), 0 + 440, 512 + 19, self, 5)
        self.laser_button_ui = TowerButton(path.join(ui_dir, "tower_7_button.png"), 0 + 440, 512 + 19, self, 6)

        self.tower_buttons = {"0": self.sniper_button_ui,
                              "1": self.cannon_button_ui,
                              "2": self.explosive_button_ui,
                              "3": self.fire_button_ui,
                              "4": self.slow_button_ui,
                              "5": self.multi_button_ui,
                              "6": self.laser_button_ui
                              }

        self.mine_button_ui = TrapButton(path.join(ui_dir, "trap_1_button.png"), 0 + 525, 512 + 19, self, 0)

        self.trap_buttons = {"0": self.mine_button_ui}

        self.button_1_list = []
        self.button_2_list = []

        self.active_button_list = self.button_1_list

        self.sell_button = SellButton(path.join(ui_dir, "sell_button.png"), 0 + 193, 512 + 19, self)

        self.up_arrow_button = ArrowButton(path.join(ui_dir, "up_arrow.png"), SCREEN_WIDTH - 200, 532, self, self.set_uibar_1)
        self.down_arrow_button = ArrowButton(path.join(ui_dir, "down_arrow.png"), SCREEN_WIDTH - 200, 555, self, self.set_uibar_2)

        self.selected_tower = None
        self.highlighted_tower = None
        self.selected_trap = None

        self.tower_info = []
        self.money_ui = None
        self.level = None

        self.props = {}

    def startup(self, persistent):
        self.persist = persistent
        level_name = self.persist["current_level"].level
        waves = self.persist["current_level"].wave_list
        money = self.persist["current_level"].money
        towers = self.persist["current_level"].towers
        traps = self.persist["current_level"].traps

        self.level = Level(level_name, waves, money)

        for index, tower in enumerate(towers):
            if index <= 6:
                self.button_1_list.append(self.tower_buttons[str(tower)])
            elif index > 6:
                self.button_2_list.append(self.tower_buttons[str(tower)])

        for index, trap in enumerate(traps):
            if len(self.button_1_list) <= 6:
                self.button_1_list.append(self.trap_buttons[str(trap)])
            else:
                self.button_2_list.append(self.trap_buttons[str(trap)])

        for index, button in enumerate(self.button_1_list):
            button.rect.x = (21 + index * (button.rect.width + 4))

        for index, button in enumerate(self.button_2_list):
            button.rect.x = (21 + index * (button.rect.width + 4))

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
            self.create_pathfinding(node)

        print self.persist

    def create_pathfinding(self, node_name):
        self.tile_list = []

        start = 0
        end = 0
        for x in range(self.level.tile_renderer.tmx_data.width):
            for y in range(self.level.tile_renderer.tmx_data.height):
                tile_property = self.level.tile_renderer.tmx_data.get_tile_properties(x, y, 0)
                if node_name in tile_property:
                    if tile_property[node_name] == "True":
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
            #print current

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

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.done = True

        if event.type == pg.MOUSEMOTION:

            x, y = pg.mouse.get_pos()
            x = x // TILE_WIDTH
            y = y // TILE_HEIGHT
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

                self.select_object(x, y)
                self.upgrade_tower(x, y)
                self.place_tower(x, y)
                self.place_trap(x, y)

            if pressed[1]:

                print "buttons switched"
                self.switch_ui()

            if pressed[2]:
                self.selected_tower = None
                self.highlighted_tower = None
                self.selected_trap = None

    def switch_ui(self):
        if self.active_button_list == self.button_1_list:
            self.active_button_list = self.button_2_list
        else:
            self.active_button_list = self.button_1_list

    def set_uibar_1(self):
        self.active_button_list = self.button_1_list

    def set_uibar_2(self):
        self.active_button_list = self.button_2_list

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
        attack_range = self.highlighted_tower.radius
        up_cost = self.highlighted_tower.upgrade_cost

        if self.highlighted_tower.tier <= self.highlighted_tower.max_tier:

            self.tower_info.append(self.create_text(str(name)))
            self.tower_info.append(self.create_text("Damage: " + str(attack)))

            if type(self.highlighted_tower).__name__ == "FireTower":
                tick_frequency = self.highlighted_tower.tick_frequency
                self.tower_info.append(self.create_text("Damage every " + str(tick_frequency) + "ms"))

            elif type(self.highlighted_tower).__name__ == "SlowTower":
                slow = self.highlighted_tower.speed_mod
                duration = self.highlighted_tower.slow_duration
                self.tower_info.append(self.create_text("Slow: " + str(slow * 100) + "% " + "for " + str(duration) + " ms"))

            else:
                self.tower_info.append(self.create_text("Range: " + str(attack_range)))

            self.tower_info.append(self.create_text("Cost to Upgrade: " + str(up_cost)))
        else:

            self.tower_info.append(self.create_text(str(name)))
            self.tower_info.append(self.create_text("Damage: " + str(attack)))

            if type(self.highlighted_tower).__name__ == "FireTower":
                tick_frequency = self.highlighted_tower.tick_frequency
                self.tower_info.append(self.create_text("Damage every " + str(tick_frequency) + "ms"))

            elif type(self.highlighted_tower).__name__ == "SlowTower":
                slow = self.highlighted_tower.speed_mod
                duration = self.highlighted_tower.slow_duration
                self.tower_info.append(self.create_text("Slow: " + str(slow * 100) + "% " + "for " + str(duration) + "ms"))

            else:

                self.tower_info.append(self.create_text("Range: " + str(attack_range)))
            self.tower_info.append(self.create_text("Max upgrade tier reached"))

    def create_text(self, text):
        text = str(text)
        font = pg.font.Font(None, 24)
        render_text = font.render(text, True, BLACK)
        return render_text

    def draw_tower_preview(self, screen):
        if self.selected_tower is not None:

            name_text = self.create_text(str(self.level.all_towers[self.selected_tower].name))
            name_rect = name_text.get_rect()
            cost_text = self.create_text("Cost: " + str(self.level.all_towers[self.selected_tower].cost) + " Gold")
            cost_rect = cost_text.get_rect()

            damage_text = self.create_text("Damage: " + str(self.level.all_towers[self.selected_tower].damage))
            damage_rect = damage_text.get_rect()

            special_text = None
            if self.level.all_towers[self.selected_tower].__name__ == "SlowTower":
                special_text = self.create_text("Slow modifier: " + str(self.level.all_towers[self.selected_tower].speed_mod * 100) + "%")
                special_rect = special_text.get_rect()

            if self.level.all_towers[self.selected_tower].__name__ == "FireTower":
                special_text = self.create_text("every " + str(self.level.all_towers[self.selected_tower].tick_frequency) + "ms")
                special_rect = special_text.get_rect()

            mouse_pos_x = self.cursor_x * TILE_WIDTH
            if mouse_pos_x < 400:
                pg.draw.rect(screen, UI_COLOR, [SCREEN_WIDTH - 192, 412 - 2, 192, 100])
                screen.blit(name_text, (SCREEN_WIDTH - 192 + 10, 412 + name_rect.height))
                screen.blit(cost_text, (SCREEN_WIDTH - 192 + 10, 412 + 20 + cost_rect.height ))
                screen.blit(damage_text, (SCREEN_WIDTH - 192 + 10, 412 + 40 + damage_rect.height ))
                if special_text:
                    screen.blit(special_text, (SCREEN_WIDTH - 192 + 10, 412 + 60 + special_rect.height ))

            elif mouse_pos_x >= 400:
                pg.draw.rect(screen, UI_COLOR, [0, 412 - 2, 192, 100])
                screen.blit(name_text, (0 + 10, 412 + name_rect.height))
                screen.blit(cost_text, (0 + 10, 412 + 20 + cost_rect.height))
                screen.blit(damage_text, (0 + 10, 412 + 40 + damage_rect.height))
                if special_text:
                    screen.blit(special_text, (0 + 10, 412 + 60 + special_rect.height ))

        if "can_build" in self.props:
            if self.props["can_build"] == "True" and self.selected_tower is not None:
                radius = self.level.all_towers[self.selected_tower].radius
                tower_image = pg.image.load(path.join(tower_dir, "tower" + str(self.selected_tower + 1) + ".png"))

                pg.draw.rect(self.screen, BLACK, [self.cursor_x * TILE_WIDTH,
                                                  self.cursor_y * TILE_HEIGHT,
                                                  TILE_WIDTH,
                                                  TILE_HEIGHT
                                                  ], 1
                             )

                pg.draw.circle(screen, BLACK, ([self.cursor_x * TILE_WIDTH + 16,
                                                self.cursor_y * TILE_HEIGHT + 16]), radius, 1)
                screen.blit(tower_image, (self.cursor_x * TILE_WIDTH, self.cursor_y * TILE_HEIGHT))

    def draw_trap_preview(self, screen):
        if self.selected_trap is not None:
            name_text = self.create_text(str(self.level.trap_list[self.selected_trap].name))
            name_rect = name_text.get_rect()
            cost_text = self.create_text("Cost: " + str(self.level.trap_list[self.selected_trap].cost) + " Gold")
            cost_rect = cost_text.get_rect()

            damage_text = self.create_text("Damage: " + str(self.level.trap_list[self.selected_trap].damage))
            damage_rect = damage_text.get_rect()

            mouse_pos_x = self.cursor_x * TILE_WIDTH
            if mouse_pos_x < 400:
                pg.draw.rect(screen, UI_COLOR, [SCREEN_WIDTH - 192, 412 - 2, 192, 100])
                screen.blit(name_text, (SCREEN_WIDTH - 192 + 10, 412 + name_rect.height))
                screen.blit(cost_text, (SCREEN_WIDTH - 192 + 10, 412 + 20 + cost_rect.height ))
                screen.blit(damage_text, (SCREEN_WIDTH - 192 + 10, 412 + 40 + damage_rect.height ))

            elif mouse_pos_x >= 400:
                pg.draw.rect(screen, UI_COLOR, [0, 412 - 2, 192, 100])
                screen.blit(name_text, (0 + 10, 412 + name_rect.height))
                screen.blit(cost_text, (0 + 10, 412 + 20 + cost_rect.height))
                screen.blit(damage_text, (0 + 10, 412 + 40 + damage_rect.height))

            if "can_build" in self.props:
                if self.props["can_build"] == "False" and self.selected_trap is not None:
                    pg.draw.rect(self.screen, BLACK, [self.cursor_x * TILE_WIDTH,
                                                      self.cursor_y * TILE_HEIGHT,
                                                      TILE_WIDTH,
                                                      TILE_HEIGHT
                                                      ], 1
                                 )


                    screen.blit(pg.image.load(path.join(trap_dir, "trap" + str(self.selected_trap + 1) + ".png")),
                                (self.cursor_x * TILE_WIDTH,
                                 self.cursor_y * TILE_HEIGHT))

    def draw_ui(self, screen):
        if self.highlighted_tower is None:
            screen.blit(self.ui, (0, 512))
            for button in self.active_button_list:
                screen.blit(button.image, button.rect)

            if self.active_button_list == self.button_1_list:
                screen.blit(self.down_arrow_button.image, self.down_arrow_button.rect)

            else:
                screen.blit(self.up_arrow_button.image, self.up_arrow_button.rect)

        else:
            screen.blit(self.upgrade_ui, (0, 512))
            pg.draw.rect(screen, BLACK, [self.highlighted_tower.rect.x, self.highlighted_tower.rect.y,
                                         self.highlighted_tower.rect.width, self.highlighted_tower.rect.height], 1)

            self.highlighted_tower.draw_attack_range(screen) # Draw circle in tower range

            self.display_upgrade_ui(screen)
            self.create_tower_info()
            self.display_tower_info(screen)

        if self.money_ui is not None:
            screen.blit(self.money_ui, (800-150 + 10, 512 + 40))

    def display_upgrade_ui(self, screen):
        if self.highlighted_tower.tier <= self.highlighted_tower.max_tier:

            screen.blit(self.highlighted_tower.upgrade_button_1.image, self.highlighted_tower.upgrade_button_1.rect)
            screen.blit(self.highlighted_tower.upgrade_button_2.image, self.highlighted_tower.upgrade_button_2.rect)
        screen.blit(self.sell_button.image, self.sell_button.rect)

    def display_tower_info(self, screen):
        if self.highlighted_tower.rect.x < 400:
            pg.draw.rect(screen, UI_COLOR, [SCREEN_WIDTH - 230, 412 - 2, 230, 100])
            for index, text in enumerate(self.tower_info):
                rect = text.get_rect()
                screen.blit(text, (SCREEN_WIDTH - 230 + 10, 412 + 20 + index * (rect.height + 2)))

        elif self.highlighted_tower.rect.x >= 400:
            pg.draw.rect(screen, UI_COLOR, [0, 412 - 2, 230, 100])
            for index, text in enumerate(self.tower_info):
                rect = text.get_rect()
                screen.blit(text, (0 + 10, 412 + 20 + index * (rect.height + 2)))

    def draw(self, screen):
        screen.fill(WHITE)
        self.level.draw(screen)
        self.draw_tower_preview(screen)
        self.draw_trap_preview(screen)
        self.draw_ui(screen)
        # self.draw_debug_pathfinding(screen)

    def select_object(self, x, y):
        if self.highlighted_tower is None and self.selected_trap is None and self.selected_tower is None:
            for button in self.active_button_list:
                if button.rect.collidepoint(x, y):
                    button.get_clicked()
            if self.up_arrow_button.rect.collidepoint(x, y) and self.active_button_list == self.button_2_list:
                self.up_arrow_button.get_clicked()
            elif self.down_arrow_button.rect.collidepoint(x, y) and self.active_button_list == self.button_1_list:
                self.down_arrow_button.get_clicked()

        if self.selected_tower is None and self.selected_trap is None:
            for tower in self.level.tower_group:
                if tower.rect.collidepoint(x, y):
                    self.highlighted_tower = tower

    def upgrade_tower(self, x, y):
        if self.highlighted_tower is not None:
            if self.level.money >= self.highlighted_tower.upgrade_cost \
                    and self.highlighted_tower.tier <= self.highlighted_tower.max_tier:

                cost = self.highlighted_tower.upgrade_cost
                button_1 = self.highlighted_tower.upgrade_button_1
                button_2 = self.highlighted_tower.upgrade_button_2

                if button_1.rect.collidepoint(x, y):
                    self.level.money -= cost
                    button_1.get_clicked()

                elif button_2.rect.collidepoint(x, y):
                    self.level.money -= cost
                    button_2.get_clicked()

            if self.sell_button.rect.collidepoint(x, y):
                self.sell_button.get_clicked()

    def sell_tower(self):
        self.level.money += self.highlighted_tower.cost * 0.8
        self.level.money = int(self.level.money)
        self.highlighted_tower.kill()
        self.highlighted_tower = None

    def place_trap(self, x, y):

        if "can_build" in self.props:
            if self.selected_trap is not None and self.props["can_build"] == "False":
                allowed = True
                for trap in self.level.trap_group:
                    if trap.rect.collidepoint(x, y):
                        allowed = False
                        break

                if allowed:
                    if self.selected_trap >= 0:
                        trap = self.selected_trap
                        cost = self.level.trap_list[self.selected_trap].cost
                        if self.level.money >= cost:
                            self.create_trap(x, y, trap)
                            self.level.money -= cost

    def place_tower(self, x, y):
        if "can_build" in self.props:
            if self.selected_tower is not None and self.props["can_build"] == "True":
                allowed = True
                for tower in self.level.tower_group:
                    if tower.rect.collidepoint(x, y):
                        allowed = False
                        break
                if allowed:
                    if self.selected_tower >= 0:
                        tower = self.selected_tower
                        cost = self.level.all_towers[self.selected_tower].cost
                        if self.level.money >= cost:
                            self.create_tower(x, y, tower)
                            self.level.money -= cost

    def create_tower(self, x, y, selected):
        x = x // TILE_WIDTH
        y = y // TILE_HEIGHT

        tower = self.level.all_towers[selected](x * TILE_WIDTH,
                                                y * TILE_HEIGHT,
                                                self.level)
        self.level.tower_group.add(tower)

    def create_trap(self, x, y, selected):
        x = x // TILE_WIDTH
        y = y // TILE_HEIGHT
        trap = self.level.trap_list[selected](x * TILE_WIDTH,
                                              y * TILE_HEIGHT,
                                              self.level)
        self.level.trap_group.add(trap)

    def draw_debug_pathfinding(self, screen):
        for x in range(0, len(self.level.creep_path)):
            for location in self.level.creep_path[x]:
                pg.draw.rect(screen, BLACK, [location[0] * TILE_WIDTH, location[1] * TILE_HEIGHT,
                                                         TILE_WIDTH, TILE_HEIGHT], 1)

