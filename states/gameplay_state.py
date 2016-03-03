import pygame as pg
from base_state import GameState
from os import path, pardir
import Queue
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, TILE_WIDTH, TILE_HEIGHT, UI_COLOR, WHITE, BLACK
Vector = pg.math.Vector2

from level import Level

ui_dir = path.join(path.dirname(__file__), pardir, "assets", "ui")
tower_dir = path.join(path.dirname(__file__), pardir, "assets", "towers")
trap_dir = path.join(path.dirname(__file__), pardir, "assets", "traps")


class GamePlay(GameState):
    def __init__(self):
        super(GamePlay, self).__init__()
        self.next_state = "MENU"

        self.ui = pg.image.load(path.join(ui_dir, "uitemplate.png")).convert_alpha()
        self.upgrade_ui = pg.image.load(path.join(ui_dir, "ui_upgrade.png")).convert_alpha()
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

        self.tower_ui_6 = pg.image.load(path.join(ui_dir, "tower_6_button.png")).convert_alpha()
        self.tower_ui_6_rect = self.tower_ui_6.get_rect(topleft=(0+525, 512+19))

        self.trap_ui_1 = pg.image.load(path.join(ui_dir, "trap_1_button.png")).convert_alpha()
        self.trap_ui_1_rect = self.trap_ui_1.get_rect(topleft=(0 + 440, 512 + 19))

        self.upgrade_attack_button = pg.image.load(path.join(ui_dir, "upgrade_button.png")).convert_alpha() # Up damage
        self.upgrade_range_button = pg.image.load(path.join(ui_dir, "upgrade_button_2.png")).convert_alpha() # Up range
        self.upgrade_dps_button = pg.image.load(path.join(ui_dir, "upgrade_button_3.png")).convert_alpha() # Up firetower DPS
        self.upgrade_slow_duration_button = pg.image.load(path.join(ui_dir, "upgrade_button_4.png")).convert_alpha()
        self.upgrade_slow_modifier_button = pg.image.load(path.join(ui_dir, "upgrade_button_5.png")).convert_alpha()

        self.sell_button = pg.image.load(path.join(ui_dir, "sell_button.png")).convert_alpha() # Sell Tower

        self.button_1_rect = self.upgrade_attack_button.get_rect()
        self.button_2_rect = self.upgrade_range_button.get_rect()
        self.button_3_rect = self.sell_button.get_rect()

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
            self.create_pathfinding(node)

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

            name_text = self.create_text(str(self.level.tower_list[self.selected_tower].name))
            name_rect = name_text.get_rect()
            cost_text = self.create_text("Cost: " + str(self.level.tower_list[self.selected_tower].cost) + " Gold")
            cost_rect = cost_text.get_rect()

            damage_text = self.create_text("Damage: " + str(self.level.tower_list[self.selected_tower].damage))
            damage_rect = damage_text.get_rect()

            special_text = None
            if self.level.tower_list[self.selected_tower].__name__ == "SlowTower":
                special_text = self.create_text("Slow modifier: " + str(self.level.tower_list[self.selected_tower].speed_mod * 100) + "%")
                special_rect = special_text.get_rect()

            if self.level.tower_list[self.selected_tower].__name__ == "FireTower":
                special_text = self.create_text("every " + str(self.level.tower_list[self.selected_tower].tick_frequency) + "ms")
                special_rect = special_text.get_rect()

            mouse_pos_x = self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth
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

        try:

            if self.props["can_build"] == "True" and self.selected_tower is not None:
                radius = self.level.tower_list[self.selected_tower].radius
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
        except KeyError:
            pass
            # print "Key 'can_build' not in dictionary 'self.props'"
            # print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def draw_trap_preview(self, screen):
        try:

            if self.props["can_build"] == "False" and self.selected_trap is not None:
                pg.draw.rect(self.screen, BLACK, [self.cursor_x * TILE_WIDTH,
                                                  self.cursor_y * TILE_HEIGHT,
                                                  TILE_WIDTH,
                                                  TILE_HEIGHT
                                                  ], 1
                             )

                screen.blit(pg.image.load(path.join(trap_dir, "trap" + str(self.selected_trap + 1) + ".png")), (self.cursor_x * self.level.tile_renderer.tmx_data.tilewidth,
                                                                                                                   self.cursor_y * self.level.tile_renderer.tmx_data.tileheight))
        except KeyError:
            pass
            # print "Key 'can_build' not in dictionary 'self.props'"
            # print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def draw_ui(self, screen):

        if self.highlighted_tower is None:
            screen.blit(self.ui, (0, 512))
            screen.blit(self.tower_ui_1, (0+21, 512+19))
            screen.blit(self.tower_ui_2, (0+110, 512+19))
            screen.blit(self.tower_ui_3, (0+193, 512+19))
            screen.blit(self.tower_ui_4, (0+277, 512+19))
            screen.blit(self.tower_ui_5, (0+363, 512+19))
            screen.blit(self.tower_ui_6, (0+525, 512+19))
            screen.blit(self.trap_ui_1, self.trap_ui_1_rect)

        else:
            screen.blit(self.upgrade_ui, (0, 512))
            pg.draw.rect(screen, BLACK, [self.highlighted_tower.rect.x, self.highlighted_tower.rect.y,
                                                     self.highlighted_tower.rect.width, self.highlighted_tower.rect.height], 1)

            self.highlighted_tower.draw2(screen) # Draw circle in tower range

            self.display_upgrade_ui(screen)

            self.create_tower_info()
            self.display_tower_info(screen)

        if self.money_ui is not None:
            screen.blit(self.money_ui, (800-192 + 10, 512 + 40))

    def display_upgrade_ui(self, screen):
        if self.highlighted_tower.tier <= self.highlighted_tower.max_tier:
            if type(self.highlighted_tower).__name__ != "SlowTower":
                screen.blit(self.upgrade_attack_button, (0 + 21, 512 + 19))
                self.button_1_rect.x, self.button_1_rect.y = (0+21, 512+19)

            elif type(self.highlighted_tower).__name__ == "SlowTower":
                screen.blit(self.upgrade_slow_duration_button, (0 + 21, 512 + 19))
                self.button_1_rect.x, self.button_1_rect.y = (0+21, 512+19)

            else:
                screen.blit(self.upgrade_attack_button, (0 + 21, 512 + 19))
                self.button_1_rect.x, self.button_1_rect.y = (0+21, 512+19)

            if type(self.highlighted_tower).__name__ == "FireTower":
                screen.blit(self.upgrade_dps_button, (0 + 110, 512 + 19))
                self.button_2_rect.x, self.button_2_rect.y = (0+110, 512+19)

            elif type(self.highlighted_tower).__name__ == "SlowTower":
                screen.blit(self.upgrade_slow_modifier_button, (0 + 110, 512 + 19))
                self.button_2_rect.x, self.button_2_rect.y = (0+110, 512+19)

            else:
                screen.blit(self.upgrade_range_button, (0 + 110, 512 + 19))
                self.button_2_rect.x, self.button_2_rect.y = (0+110, 512+19)

            screen.blit(self.sell_button, (0 + 193, 512 + 19))
            self.button_3_rect.x, self.button_3_rect.y = (0 + 193, 512 + 19)

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

            elif self.tower_ui_6_rect.collidepoint(x, y):
                self.selected_tower = 5

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
            if self.level.money >= self.highlighted_tower.upgrade_cost \
                    and self.highlighted_tower.tier <= self.highlighted_tower.max_tier:
                if self.button_1_rect.collidepoint(x, y):
                    self.level.money -= self.highlighted_tower.upgrade_cost
                    if type(self.highlighted_tower).__name__ == "SlowTower":
                        self.highlighted_tower.upgrade_slow_duration()
                    else:
                        self.highlighted_tower.upgrade_attack()

                elif self.button_2_rect.collidepoint(x, y):
                    self.level.money -= self.highlighted_tower.upgrade_cost
                    if type(self.highlighted_tower).__name__ == "FireTower":
                        self.highlighted_tower.upgrade_damage_tick_frequency()
                    elif type(self.highlighted_tower).__name__ == "SlowTower":
                        self.highlighted_tower.upgrade_slow_modifier()
                    else:
                        self.highlighted_tower.upgrade_radius()

            if self.button_3_rect.collidepoint(x, y):
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

        # Catch the keyerror in case the self.props dict wasnt updated yet
        except KeyError:
            print "Key 'can_build' not in dictionary 'self.props'"
            print "Mouse cursor must be outside of the map area (e.g. on top of the UI)"

    def create_tower(self, x, y, selected):
        x = x // self.level.tile_renderer.tmx_data.tilewidth
        y = y // self.level.tile_renderer.tmx_data.tileheight

        tower = self.level.tower_list[selected](x * self.level.tile_renderer.tmx_data.tilewidth,
                                                y * self.level.tile_renderer.tmx_data.tileheight,
                                                self.level)
        self.level.tower_group.add(tower)

    def create_trap(self, x, y, selected):
        x = x // self.level.tile_renderer.tmx_data.tilewidth
        y = y // self.level.tile_renderer.tmx_data.tileheight
        trap = self.level.trap_list[selected](x * self.level.tile_renderer.tmx_data.tilewidth,
                                              y * self.level.tile_renderer.tmx_data.tileheight,
                                              self.level)
        self.level.trap_group.add(trap)

    def draw_debug_pathfinding(self, screen):
        for x in range(0, len(self.level.creep_path)):
            for location in self.level.creep_path[x]:
                pg.draw.rect(screen, BLACK, [location[0] * TILE_WIDTH, location[1] * TILE_HEIGHT,
                                                         TILE_WIDTH, TILE_HEIGHT], 1)







