import pygame
import random
import json
import base64
import os

from pygbag.support.cross.aio import temporary

pygame.init()
pygame.mixer.init()

# SCREEN SETTINGS
px = 3
tile_size = px*16
SCREEN_WIDTH = tile_size * 16
SCREEN_HEIGHT = tile_size * 12
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_rect = pygame.Rect(-tile_size*2,-tile_size*2,SCREEN_WIDTH + tile_size*4,SCREEN_HEIGHT+ tile_size*4)
pygame.display.set_caption("Cheese factory")
Icon = pygame.image.load('assets/GUI/icons/cheese_icon.png')
pygame.display.set_icon(Icon)

num_map = open('assets/map.txt')

# FPS
clock = pygame.time.Clock()
FPS = 60

# Game state
play_state = 0
inventory_state = 1
trade_state = 2
market_state = 3
start_state = 4
pause_state = 5
game_state = start_state

# Keys
up_pressed = False
down_pressed = False
left_pressed = False
right_pressed = False

dev_tools = False
allow_dev_tools = True

# FONTS
text_font = pygame.font.Font("assets/fonts/font.ttf", px * 5)
inventory_text_font = pygame.font.Font("assets/fonts/font.ttf", px * 4)
title_font = pygame.font.Font("assets/fonts/font.ttf", px * 13)
mid_title_font = pygame.font.Font("assets/fonts/font.ttf", px * 7)

#COLORS
white = (255, 255, 255)
green = (0, 255, 0)
gray = (128, 128, 128)
red = (225, 0, 0)

run = True


def draw_text(text, font, text_col, x, y, centered = False):
    if "\n" in text or "_" in text:
        text_1 = ""
        for i in text:
            if i != "\n" and i != "_":
                text_1 += i
            else:
                img = font.render(text_1, True, text_col)
                if centered:
                    screen.blit(img, ((SCREEN_WIDTH - img.get_size()[0])/2, y))
                else:
                    screen.blit(img, (x, y))
                text_1 = ""
        img = font.render(text_1, True, text_col)
        if centered:
            screen.blit(img, ((SCREEN_WIDTH - img.get_size()[0])/2, y + px*5))
        else:
            screen.blit(img, (x, y + px*5))
        return
    img = font.render(text, True, text_col)

    if centered:
        screen.blit(img, ((SCREEN_WIDTH - img.get_size()[0]) / 2, y))
    else:
        screen.blit(img, (x, y))

def set_image(file):
    size = (pygame.image.load("assets/" + file + ".png").get_size()[0]*px,
            pygame.image.load("assets/" + file + ".png").get_size()[1]*px)
    return pygame.transform.scale(pygame.image.load("assets/" + file + ".png"), size)

# TILES

class tile:
    def __init__(self, file_name, solid=False, solid_x=0, solid_y=0, solid_size_x=tile_size, solid_size_y=tile_size):
        self.solid_rect = None
        self.image = pygame.transform.scale(pygame.image.load(file_name), (tile_size, tile_size))
        self.solid = solid
        self.solid_x = solid_x
        self.solid_y = solid_y
        self.solid_size_x = solid_size_x
        self.solid_size_y = solid_size_y

    def draw(self, x, y):
        screen.blit(self.image, (x + cam.transform_x, y + cam.transform_y))

    def set_solid_rect(self, x, y):
        self.solid_rect = pygame.Rect(x + cam.transform_x + self.solid_x, y + cam.transform_y + self.solid_y,
                                      self.solid_size_x, self.solid_size_y)
        return self.solid_rect


class tiles:
    def __init__(self):
        self.solid_rects = []
        self.map_size = (50 * tile_size, 32 * tile_size)
        self.start_x = (SCREEN_WIDTH - self.map_size[0]) / 2
        self.start_y = (SCREEN_HEIGHT - self.map_size[1]) / 2
        self.left_border = self.start_x
        self.top_border = self.start_y
        self.right_border = self.map_size[0] + self.start_x
        self.bottom_border = self.map_size[1] + self.start_y
        self.rects = []
        # Tiles
        self.grass_0_tile = tile('assets/tiles/grass_00.png')  # 0
        self.grass_1_tile = tile('assets/tiles/grass_01.png')  # 1
        self.grass_2_tile = tile('assets/tiles/grass_02.png')  # 2
        self.grass_3_tile = tile('assets/tiles/grass_03.png')  # 3
        self.grass_4_tile = tile('assets/tiles/grass_04.png')  # 4
        self.water_0_tile = tile('assets/tiles/water_00.png', True)  # 5
        self.water_1_tile = tile('assets/tiles/water_01.png', True, tile_size / 2, tile_size / 2 - px*2, tile_size / 2,
                                 tile_size / 2 + px*2)  # 6
        self.water_2_tile = tile('assets/tiles/water_02.png', True, solid_y=int((tile_size / 2) - px*2),
                                 solid_size_y=int(tile_size / 2 + px*2))  # 7
        self.water_3_tile = tile('assets/tiles/water_03.png', True, solid_y=tile_size / 2 - px*2,
                                 solid_size_y=tile_size / 2 + px*2, solid_size_x=tile_size / 2)  # 8
        self.water_4_tile = tile('assets/tiles/water_04.png', True, solid_size_x=tile_size / 2)  # 9
        self.water_5_tile = tile('assets/tiles/water_05.png', True, solid_size_x=tile_size / 2,
                                 solid_size_y=tile_size / 2)  # 10
        self.water_6_tile = tile('assets/tiles/water_06.png', True, solid_size_y=tile_size / 2 + px)  # 11
        self.water_7_tile = tile('assets/tiles/water_07.png', True, solid_x=tile_size / 2,
                                 solid_size_y=tile_size / 2 + px, solid_size_x=tile_size / 2)  # 12
        self.water_8_tile = tile('assets/tiles/water_08.png', True, solid_x=tile_size / 2,
                                 solid_size_x=tile_size / 2)  # 13
        self.water_9_tile = tile('assets/tiles/water_09.png', True, solid_size_y=tile_size / 2)  # 14
        self.water_10_tile = tile('assets/tiles/water_10.png', True, solid_x=tile_size / 2,
                                  solid_size_x=tile_size / 2)  # 15
        self.water_11_tile = tile('assets/tiles/water_11.png', True, solid_y=tile_size / 2 - px*2,
                                  solid_size_y=tile_size / 2 + px*2)  # 16
        self.water_12_tile = tile('assets/tiles/water_12.png', True, solid_size_x=tile_size / 2)  # 17
        self.road_0_tile = tile('assets/tiles/road_00.png')  # 18
        self.road_1_tile = tile('assets/tiles/road_01.png')  # 19
        self.road_2_tile = tile('assets/tiles/road_02.png')  # 20
        self.road_3_tile = tile('assets/tiles/road_03.png')  # 21
        self.road_4_tile = tile('assets/tiles/road_04.png')  # 22
        self.road_5_tile = tile('assets/tiles/road_05.png')  # 23
        self.road_6_tile = tile('assets/tiles/road_06.png')  # 24
        self.road_7_tile = tile('assets/tiles/road_07.png')  # 25
        self.road_8_tile = tile('assets/tiles/road_08.png')  # 26
        self.road_9_tile = tile('assets/tiles/road_09.png')  # 27
        self.road_10_tile = tile('assets/tiles/road_10.png') # 28
        self.road_11_tile = tile('assets/tiles/road_11.png') # 29
        self.road_12_tile = tile('assets/tiles/road_12.png') # 30

        self.all_tiles = [self.grass_0_tile, self.grass_1_tile, self.grass_2_tile, self.grass_3_tile,
                          self.grass_4_tile, self.water_0_tile, self.water_1_tile, self.water_2_tile, self.water_3_tile,
                          self.water_4_tile,
                          self.water_5_tile, self.water_6_tile, self.water_7_tile, self.water_8_tile, self.water_9_tile,
                          self.water_10_tile, self.water_11_tile, self.water_12_tile, self.road_0_tile,
                          self.road_1_tile, self.road_2_tile,
                          self.road_3_tile, self.road_4_tile, self.road_5_tile, self.road_6_tile, self.road_7_tile,
                          self.road_8_tile, self.road_9_tile, self.road_10_tile, self.road_11_tile, self.road_12_tile]

    def draw_map(self, num_map):
        num_map.seek(0)
        y = self.start_y
        x = self.start_x
        tile_num = ""
        map = num_map.read()
        for i in range(len(map)):
            if map[i] != " " and map[i] != "\n":
                tile_num = tile_num + map[i]
            elif map[i] == " ":
                self.all_tiles[int(tile_num)].draw(x, y)
                x += tile_size
                tile_num = ""
            elif map[i] == "\n":
                self.all_tiles[int(tile_num)].draw(x, y)
                y += tile_size
                x = self.start_x
                tile_num = ""
        if dev_tools:
            for i in self.solid_rects:
                if i.colliderect(screen_rect):
                    pygame.draw.rect(screen, (255, 255, 0), i)

    def set_solid_tiles(self, num_map):
        self.solid_rects = []
        num_map.seek(0)
        y = self.start_y
        x = self.start_x
        tile_num = ""
        map = num_map.read()
        for i in range(len(map)):
            if map[i] != " " and map[i] != "\n":
                tile_num = tile_num + map[i]
            elif map[i] == " ":
                if self.all_tiles[int(tile_num)].solid:
                    self.solid_rects.append(self.all_tiles[int(tile_num)].set_solid_rect(x, y))
                x += tile_size
                tile_num = ""
            elif map[i] == "\n":
                if self.all_tiles[int(tile_num)].solid:
                    self.solid_rects.append(self.all_tiles[int(tile_num)].set_solid_rect(x, y))
                y += tile_size
                x = self.start_x
                tile_num = ""

class decor:
    def __init__(self):
        self.red_tulip = set_image("decors/red_tulip")
        self.yellow_tulip = set_image("decors/yellow_tulip")
        self.red_flower = set_image("decors/red_flower")
        self.yellow_flower = set_image("decors/yellow_flower")
        self.red_flower_2 = set_image("decors/red_flower_2")
        self.yellow_flower_2 = set_image("decors/yellow_flower_2")
        self.mushroom = set_image("decors/mushroom")
        self.small_stone = set_image("decors/small_stone")
        self.big_stone = set_image("decors/big_stone")

        self.all_decors = [self.mushroom, self.red_tulip, self.red_flower, self.red_flower_2, self.yellow_flower,
                           self.yellow_flower_2, self.yellow_tulip, self.small_stone]
        self.decors = []

    def setup_decors(self):
        hitboxes = []

        for i in range(40):
            rnd = (random.randint(-13 * tile_size, 30 * tile_size), random.randint(-10 * tile_size, 18 * tile_size))

            x = rnd[0]
            y = rnd[1]
            hitbox = pygame.Rect(x, y, px*10, px*10)
            rnd_decor = random.choice(self.all_decors)
            can_place = True
            for a in tiles.solid_rects:
                if hitbox.colliderect(a):
                    can_place = False
            for b in blocks.all_blocks:
                if b["hitbox"].colliderect(hitbox):
                    can_place = False
            for c in hitboxes:
                if c.colliderect(hitbox):
                    can_place = False

            if can_place:
                self.decors.append((rnd_decor, rnd))
                hitboxes.append(hitbox)


    def draw_decors(self):
        for i in self.decors:
            screen.blit(i[0], (i[1][0] + cam.transform_x,  i[1][1] + cam.transform_y))


        # CAMERA
class camera:
    def __init__(self):
        self.transform_x = 0
        self.transform_y = 0
        self.bottom_y = SCREEN_HEIGHT
        self.top_y = 0
        self.right_x = SCREEN_WIDTH
        self.left_x = 0


# COLLISION CHECKER

class collision_checker:
    def __init__(self):
        self.count_down = 0

    def check_tile_collision(self, rect, entity):
        for i in tiles.solid_rects:
            if i.colliderect(rect):
                if entity is not player:
                    entity.wait = 130
                if rect == entity.top_hitbox:
                    entity.can_move_up = False
                elif rect == entity.bottom_hitbox:
                    entity.can_move_down = False
                elif rect == entity.left_hitbox:
                    entity.can_move_left = False
                elif rect == entity.right_hitbox:
                    entity.can_move_right = False
                break
            else:
                entity.can_move_up = True
                entity.can_move_down = True
                entity.can_move_left = True
                entity.can_move_right = True

    def check_entity_collision(self):
        for entity in entities:
            if player.top_hitbox.colliderect(entity.main_hitbox):
                entity.drop_item()
                self.check_tile_collision(entity.top_hitbox, entity)
                if entity.can_move_up:
                    self.check_entities_collision(entity.top_hitbox, entity)
                if entity.can_move_up:
                    self.check_block_collision(entity.top_hitbox, entity)
                if entity.can_move_up:
                    col_checker.check_trader_col(entity.top_hitbox, entity)
                if entity.can_move_up:
                    if tiles.top_border != entity.pos_y:
                        entity.pos_y -= px
                    else:
                        player.can_move_up = False
                else:
                    player.can_move_up = False
            elif player.bottom_hitbox.colliderect(entity.main_hitbox):
                entity.drop_item()
                self.check_tile_collision(entity.bottom_hitbox, entity)
                if entity.can_move_down:
                    self.check_entities_collision(entity.bottom_hitbox, entity)
                if entity.can_move_down:
                    self.check_block_collision(entity.bottom_hitbox, entity)
                if entity.can_move_down:
                    col_checker.check_trader_col(entity.bottom_hitbox, entity)
                if entity.can_move_down:
                    if tiles.bottom_border != entity.pos_y:
                        entity.pos_y += px
                    else:
                        player.can_move_down = False
                else:
                    player.can_move_down = False
            elif player.left_hitbox.colliderect(entity.main_hitbox):
                entity.drop_item()
                self.check_tile_collision(entity.left_hitbox, entity)
                if entity.can_move_left:
                    self.check_entities_collision(entity.left_hitbox, entity)
                if entity.can_move_left:
                    self.check_block_collision(entity.left_hitbox, entity)
                if entity.can_move_left:
                    col_checker.check_trader_col(entity.left_hitbox, entity)
                if entity.can_move_left:
                    if tiles.left_border != entity.pos_x:
                        entity.pos_x -= px
                    else:
                        player.can_move_left = False
                else:
                    player.can_move_left = False
            elif player.right_hitbox.colliderect(entity.main_hitbox):
                entity.drop_item()
                self.check_tile_collision(entity.right_hitbox, entity)
                if entity.can_move_right:
                    self.check_entities_collision(entity.right_hitbox, entity)
                if entity.can_move_right:
                    self.check_block_collision(entity.right_hitbox, entity)
                if entity.can_move_right:
                    col_checker.check_trader_col(entity.right_hitbox, entity)
                if entity.can_move_right:
                    if tiles.right_border != entity.pos_x:
                        entity.pos_x += px
                    else:
                        player.can_move_right = False
                else:
                    player.can_move_right = False

    def check_entities_collision(self, rect, current_entity):
        for entity in entities:
            if entity != current_entity:
                if entity.main_hitbox.colliderect(rect):
                    if current_entity is not player:
                        entity.wait = 130
                    if rect == current_entity.top_hitbox:
                        current_entity.can_move_up = False
                    elif rect == current_entity.bottom_hitbox:
                            current_entity.can_move_down = False
                    elif rect == current_entity.left_hitbox:
                            current_entity.can_move_left = False
                    elif rect == current_entity.right_hitbox:
                            current_entity.can_move_right = False

    def check_player_collision(self, rect, entity):
        if rect == entity.top_hitbox:
            if player.main_hitbox.colliderect(rect):
                entity.can_move_up = False
        elif rect == entity.bottom_hitbox:
            if player.main_hitbox.colliderect(rect):
                entity.can_move_down = False
        elif rect == entity.left_hitbox:
            if player.main_hitbox.colliderect(rect):
                entity.can_move_left = False
        elif rect == entity.right_hitbox:
            if player.main_hitbox.colliderect(rect):
                entity.can_move_right = False

    def check_block_collision(self, rect, entity):
        for i in blocks.all_blocks:
            if entity == player:
                if i["name"] == "tree_2":
                    big_rect = pygame.Rect(i["x"] + cam.transform_x, i["y"] + cam.transform_y, i["image"].get_size()[0], i["image"].get_size()[1])
                    if big_rect.colliderect(entity.top_hitbox) and big_rect.colliderect(entity.bottom_hitbox) and big_rect.colliderect(entity.left_hitbox) and big_rect.colliderect(entity.right_hitbox):
                        copy_img = i["image"].__copy__()
                        copy_img.set_alpha(120)
                        i["image"] = copy_img
                    else:
                        copy_img = i["image"].__copy__()
                        copy_img.set_alpha(255)
                        i["image"] = copy_img

            if i["hitbox"].colliderect(rect):
                if entity is not player:
                    entity.wait = 130
                    if i["name"] == "drinker" or i ["name"] == "feeder" or i["name"] == "hay_bale":
                        if entity.max_cool_down > 10:
                            entity.max_cool_down -= 3
                if "interactable" not in i or i["interactable"] != 1:
                    if rect == entity.top_hitbox:
                        entity.can_move_up = False
                    elif rect == entity.bottom_hitbox:
                        entity.can_move_down = False
                    elif rect == entity.left_hitbox:
                        entity.can_move_left = False
                    elif rect == entity.right_hitbox:
                        entity.can_move_right = False
                    break
            else:
                entity.can_move_up = True
                entity.can_move_down = True
                entity.can_move_left = True
                entity.can_move_right = True

    def check_item_collision(self):
        for item in items.all_items:
            removed = False
            if item["hitbox"].colliderect(player.main_hitbox):
                for slot in inventory.inventory_slots:
                    if slot.get("item") is not None:
                        if item["name"] == slot.get("item")["name"] and slot.get("value") != item["max_stack"]:
                            slot["value"] += 1
                            sounds.play_sound(sounds.pick_sfx)
                            removed = True
                            break
                if not removed:
                    for slot in inventory.inventory_slots:
                        if slot.get("item") is None:
                            slot["value"] += 1
                            slot["item"] = item.copy()
                            sounds.play_sound(sounds.pick_sfx)
                            removed = True
                            break
                if removed:
                    items.all_items.remove(item)

    def check_place_block_col(self, temporary_rect):
        for block in blocks.all_blocks:
            if block['hitbox'].colliderect(temporary_rect):
                player.can_place_block = False
                return
        for tile in tiles.solid_rects:
            if tile.colliderect(temporary_rect):
                player.can_place_block = False
                return
        if player.main_hitbox.colliderect(temporary_rect):
            player.can_place_block = False
            return
        for entity in entities:
            if entity.main_hitbox.colliderect(temporary_rect):
                player.can_place_block = False
                return
        for trader in traders:
            if trader.main_hitbox.colliderect(temporary_rect):
                player.can_place_block = False
                return
        player.can_place_block = True

    def check_block_hit(self, attack_rect):
        for block in blocks.all_blocks:
            if attack_rect.colliderect(block["hitbox"]):
                if block["life"] < 1000:
                    block["life"] -= inventory.hand_item["strength"]
                    blocks.draw_life_bar(block, block["max_life"], block["life"])
                    inventory.hand_item["durability"] -= 1
                    if inventory.inventory_slots[inventory.selected_slot]["item"]["durability"] <= 0:
                        inventory.inventory_slots[inventory.selected_slot]["value"] = 0

                break
    def check_block_break(self, attack_rect):
        for block in blocks.all_blocks:
            if attack_rect.colliderect(block["hitbox"]):
                if block["life"] < 1000:
                    if block["life"] <= 0:
                        sounds.play_sound(sounds.break_sfx)
                        blocks.drop_item(block["drop"], (block["x"], block["y"]))
                        if "fence" in block:
                            blocks.all_fences.remove(block)
                            blocks.organize_fences()

                        if "second_block" in block:
                            set_block = block["second_block"]
                            blocks.set_block(set_block[0], (block["x"] + set_block[1], block["y"] + set_block[2]))
                            if block["name"] == "tree_2":
                                rnd = random.randint(1,4)
                                if rnd == 1:
                                    if player.direction == "right":
                                        blocks.set_block(blocks.log, (block["x"] + tile_size * 2, block["y"] + tile_size * 2 + px*13))
                                    elif player.direction == "left":
                                        blocks.set_block(blocks.log,
                                                         (block["x"] - tile_size, block["y"] + tile_size * 2 + px*13))
                                    elif player.direction == "up":
                                        blocks.set_block(blocks.log,
                                                         (block["x"] + tile_size, block["y"] + tile_size*2))
                                    elif player.direction == "down":
                                        blocks.set_block(blocks.log,
                                                         (block["x"] + tile_size, block["y"] + tile_size*3.5))
                        blocks.all_blocks.remove(block)


                break
    def check_trader_col(self, rect, entity):
        for trader in traders:
            if trader.main_hitbox.colliderect(rect):
                if rect == entity.top_hitbox:
                    entity.can_move_up = False
                elif rect == entity.bottom_hitbox:
                    entity.can_move_down = False
                elif rect == entity.left_hitbox:
                    entity.can_move_left = False
                elif rect == entity.right_hitbox:
                    entity.can_move_right = False
                traders.remove(trader)
                traders.append(trader)
                if entity == player:
                    trade.trades = trader.trades
                    global game_state
                    game_state = trade_state

            else:
                entity.can_move_up = True
                entity.can_move_down = True
                entity.can_move_left = True
                entity.can_move_right = True

    def check_block_interact(self):
        pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(pos[0], pos[1], px, px)


        for i in blocks.all_blocks:
            if "interactable" in i:
                if i["num"] == 10:
                    i["num"] = 0
                elif i["num"] > 0:
                    i["num"] += 1

                if i["hitbox"].colliderect(mouse_rect):
                    if player.right_clicked and i["num"] == 0:
                        i["num"] += 1
                        if i["interactable"] == 0 or i["interactable"] == 1:
                            i["image"], i["image_2"] = i["image_2"], i["image"]
                            if i["interactable"] == 0:
                                i["interactable"] = 1
                            else:
                                i["interactable"] = 0
                        elif i["interactable"] == 2:
                            if player.main_hitbox.colliderect(i["hitbox"]):
                                global game_state
                                game_state = market_state
                                market.reset()


class market:
    def __init__(self):
        self.offer_window = set_image("GUI/bases/offer_window")
        self.market_base = set_image("GUI/bases/market_base")
        self.minus_icon = set_image("GUI/icons/minus_icon")
        self.mini_coin = set_image("GUI/icons/mini_coin")
        self.arrow_icon = set_image("GUI/icons/arrow_icon")
        self.default_exit_button = set_image("GUI/buttons/exit_button")
        self.selected_exit_button = set_image("GUI/buttons/selected_exit_button")

        self.exit_button = self.default_exit_button
        self.def_button_img = paused_menu.button_img
        self.selected_button_img = paused_menu.selected_img
        self.button_img = self.def_button_img

        self.def_small_button_img = start_menu.small_button_img
        self.selected_small_button_img = start_menu.selected_button_img
        self.small_button_img = self.def_small_button_img

        self.minus_button = set_image("GUI/buttons/minus_button")
        self.selected_minus_button = set_image("GUI/buttons/selected_minus_button")
        self.pressed_minus_button = set_image("GUI/buttons/pressed_minus_button")
        self.value_minus_button = self.minus_button
        self.price_minus_button = self.minus_button

        self.plus_button = set_image("GUI/buttons/plus_button")
        self.selected_plus_button = set_image("GUI/buttons/selected_plus_button")
        self.pressed_plus_button = set_image("GUI/buttons/pressed_plus_button")
        self.value_plus_button = self.plus_button
        self.price_plus_button = self.plus_button

        self.small_trash_button = set_image("GUI/buttons/small_trash_button")
        self.small_selected_trash_button = set_image("GUI/buttons/selected_small_trash")

        self.left = SCREEN_WIDTH / 2 - px * 111 / 2
        self.top = SCREEN_HEIGHT / 3
        self.state = 0
        self.to_sell_item = {"item": None, "value": None, "price":None}
        self.offers = []
        self.delete_boxes = []
        self.item_boxes = []
        y = self.top
        for i in range(len(self.offers)):
            self.delete_boxes.append(pygame.Rect(self.left + tile_size*5.5, y+px*7, 13*px, 13*px))
            y += tile_size+px
        y = self.top + 6*px
        for i in range(len(self.offers)):
            self.item_boxes.append(pygame.Rect(self.left + px *6,y, tile_size, tile_size))
            y += tile_size+px
        y = self.top + 6 * px
        if len(self.offers) < 4:
            self.new_offer_button = pygame.Rect(self.left + tile_size*1.5, y + len(self.offers)*(tile_size+px), tile_size *4,px*14)
        else:
            self.new_offer_button = None
        self.x_button = pygame.Rect(self.left + 97*px, self.top- 9*px, 13*px, 13*px)
        self.sell_button = pygame.Rect(self.left + (111*px - 31*px)/2, self.top + tile_size*2, 31*px, 13*px)
        self.value_minus = pygame.Rect(self.left + px*6, self.top + tile_size - px*4, 9*px, 10*px)
        self.value_plus = pygame.Rect(self.left + tile_size + 17* px, self.top + tile_size - 4*px, 9*px, 10*px)
        self.price_minus = pygame.Rect(self.left + tile_size*3 + px*4, self.top + tile_size -4*px, 9*px, 10*px)
        self.price_plus = pygame.Rect(self.left + tile_size*5 + px *10, self.top + tile_size - 4 * px, 9*px, 10*px)
        self.pressed_time = 0


    def draw(self):
        if self.state == 0:
            screen.blit(self.market_base, (self.left, self.top))
            y = self.top + 6*px
            for j in range(len(self.offers)):
                i = self.offers[j]
                screen.blit(i[0]["image"], (self.left + px *6, y))
                screen.blit(self.arrow_icon, (self.left + px*10 + tile_size, y + px*6))
                draw_text(str(i[1]), inventory_text_font, white, self.left + tile_size + px, y + px*12)
                draw_text(str(i[2]*i[1]), text_font, white, self.left + tile_size*2 + px*2, y + px*5)
                img = text_font.render(str(i[2]*i[1]), True, white)
                screen.blit(self.mini_coin, (self.left + tile_size*2 + px*3 + img.get_size()[0], y + px*5))

                if self.delete_boxes[j][1]:
                    screen.blit(self.small_selected_trash_button, (self.left + tile_size*5.5, y + px))
                else:
                    screen.blit(self.small_trash_button, (self.left + tile_size * 5.5, y + px))
                y += tile_size+px
            if len(self.offers) < 4:
                screen.blit(self.button_img, (self.left + tile_size*1.5, self.top + 6 * px + len(self.offers)*(tile_size+px)))
                draw_text("New offer", text_font, white, 0, y + px * 3, True)
        elif self.state == 1:
            screen.blit(self.exit_button, (self.left + 97*px, self.top- 9*px))
        elif self.state == 2:
            if self.pressed_time > 0:
                self.pressed_time -= 1
            screen.blit(self.offer_window, (self.left, self.top))
            screen.blit(self.exit_button, (self.left + 97*px, self.top- 9*px))
            screen.blit(self.to_sell_item["item"]["image"], (self.left + tile_size, self.top + 8*px))

            screen.blit(self.value_minus_button, (self.left + px*6, self.top + tile_size - px*4))
            screen.blit(self.value_plus_button, (self.left + tile_size + 17* px, self.top + tile_size - 4*px))
            draw_text(str(self.to_sell_item["value"]), inventory_text_font, white,
                      self.left + tile_size + 11 * px,
                      self.top + tile_size + 4 * px)
            screen.blit(self.arrow_icon, (self.left + tile_size*3 - px *4, self.top + tile_size - 2*px))
            screen.blit(self.price_minus_button, (self.left + tile_size*3 + px*4, self.top + tile_size -4*px))
            draw_text(str(self.to_sell_item["price"]*self.to_sell_item["value"]), text_font, white, self.left + tile_size * 4 - px*3,
                      self.top + 13*px)
            img = text_font.render(str(self.to_sell_item["price"]*self.to_sell_item["value"]), True, white)
            screen.blit(self.mini_coin, (self.left + tile_size * 4 - px*2 + img.get_size()[0], self.top + tile_size - 3 * px))
            screen.blit(self.price_plus_button, (self.left + tile_size*5 + px *10, self.top + tile_size - 4 * px))
            screen.blit(self.small_button_img, (self.left + (111*px - 31*px)/2, self.top + tile_size*2))
            draw_text("sell", text_font, white, self.left + (111*px - 31*px)/2 + px*3, self.top + tile_size*2 + 3*px)

    def draw_item_info(self, item):
        s = pygame.Surface((tile_size * 3, tile_size))
        s.set_alpha(300)
        s.fill((50*px, 25*px, 0))
        y = self.top + 6*px
        for i in range(item):
            y += tile_size + px
        pos = (self.left - tile_size * 3, y)
        screen.blit(s, pos)
        draw_text(self.offers[item][0]["name"], inventory_text_font, white, pos[0] + px*2, pos[1] + px*2)


    def handle(self):
        pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(pos[0], pos[1], 3, 3)
        if self.state == 0:
            if self.new_offer_button is not None:
                if mouse_rect.colliderect(self.new_offer_button):
                    self.button_img = self.selected_button_img
                    if player.left_clicked:
                        self.state = 1
                        player.left_clicked = False
                else:
                    self.button_img = self.def_button_img
            for delete in range(len(self.delete_boxes)):
                if mouse_rect.colliderect(self.delete_boxes[delete][0]):
                    self.delete_boxes[delete][1] = True
                    if player.left_clicked:
                        items.set_item(self.offers[delete][0],
                                       player.pos_x, player.pos_y, self.offers[delete][1])
                        self.offers.pop(delete)
                        self.reset()
                        player.left_clicked = False
                        break
                else:
                    self.delete_boxes[delete][1] = False
            for item in range(len(self.item_boxes)):
                if mouse_rect.colliderect(self.item_boxes[item]):
                    self.draw_item_info(item)
        elif self.state == 1:
            if mouse_rect.colliderect(self.x_button):
                self.exit_button = self.selected_exit_button
                if player.left_clicked:
                    self.state = 0
                    inventory.selected_slot = 0
                    player.left_clicked = False
            else:
                self.exit_button = self.default_exit_button
        elif self.state == 2:
            if mouse_rect.colliderect(self.x_button):
                self.exit_button = self.selected_exit_button
                if player.left_clicked:
                    inventory.to_change_slot_1 = None
                    self.state = 1
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.value_minus):
                if self.pressed_time == 0:
                    self.value_minus_button = self.selected_minus_button
                if player.left_clicked and self.to_sell_item["value"] > 1:
                    self.value_minus_button = self.pressed_minus_button
                    self.pressed_time = 20
                    self.to_sell_item["value"] -= 1
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.value_plus):
                if self.pressed_time == 0:
                    self.value_plus_button = self.selected_plus_button
                if player.left_clicked and inventory.inventory_slots[inventory.selected_slot]["value"] > self.to_sell_item["value"]:
                    self.value_plus_button = self.pressed_plus_button
                    self.pressed_time = 20
                    self.to_sell_item["value"] += 1
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.price_minus):
                if self.pressed_time == 0:
                    self.price_minus_button = self.selected_minus_button
                if player.left_clicked and self.to_sell_item["price"] > 1:
                    self.price_minus_button = self.pressed_minus_button
                    self.pressed_time = 20
                    self.to_sell_item["price"] -= 1
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.price_plus):
                if self.pressed_time == 0:
                    self.price_plus_button = self.selected_plus_button
                if player.left_clicked and inventory.inventory_slots[inventory.selected_slot]["item"]["price"]*2 > self.to_sell_item["price"]:
                    self.price_plus_button = self.pressed_plus_button
                    self.pressed_time = 20
                    self.to_sell_item["price"] += 1
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.sell_button):
                self.small_button_img = self.selected_small_button_img
                if player.left_clicked:
                    inventory.inventory_slots[inventory.selected_slot]["value"] -= self.to_sell_item["value"]
                    self.offers.append((self.to_sell_item["item"].copy(), self.to_sell_item["value"], self.to_sell_item["price"]))
                    self.state = 0
                    player.left_clicked = False
                    self.reset()
            else:
                self.value_minus_button = self.minus_button
                self.price_minus_button = self.minus_button
                self.value_plus_button = self.plus_button
                self.price_plus_button = self.plus_button
                self.exit_button = self.default_exit_button
                self.small_button_img = self.def_small_button_img

    def reset(self):
        self.delete_boxes = []
        self.item_boxes = []
        y = self.top
        for i in range(len(self.offers)):
            self.delete_boxes.append([pygame.Rect(self.left + tile_size * 5.5, y + px * 7, 13 * px, 13 * px), False])
            y += tile_size + px
        y = self.top + 6 * px
        for i in range(len(self.offers)):
            self.item_boxes.append(pygame.Rect(self.left + px *6,y, tile_size, tile_size))
            y += tile_size + px
        y = self.top + 6 * px
        if len(self.offers) < 4:
            self.new_offer_button = pygame.Rect(self.left + tile_size * 1.5, y + len(self.offers) * (tile_size + px),
                                                tile_size * 4, px * 14)
        else:
            self.new_offer_button = None
        self.x_button = pygame.Rect(self.left + 97 * px, self.top - 9 * px, 13 * px, 13 * px)
        self.sell_button = pygame.Rect(self.left + (111 * px - 31 * px) / 2, self.top + tile_size * 2, 31 * px, 13 * px)
    def sell(self):
        for i in range(len(self.offers)):
            offer = self.offers[i]
            rnd_max = int(6000 + (offer[2]/offer[0]["price"] - 1)*4000)
            rnd = random.randint(1, rnd_max)
            if rnd == 1:
                player.currency += offer[1]*offer[2]
                self.offers.pop(i)
                self.reset()
                break



class trade:
    def __init__(self):
        self.selected_trade = None
        self.trades = []
        self.trade_base = set_image("GUI/bases/trade_base")
        self.down_scroll = set_image("GUI/icons/down_scroll")
        self.up_scroll = set_image("GUI/icons/up_scroll")
        self.plus_icon = set_image("GUI/icons/plus_icon")
        self.slash_icon = set_image("GUI/icons/slash_icon")
        self.offer_window = set_image("GUI/bases/offer_window")

        self.small_button_img = set_image("GUI/buttons/small_button")
        self.pressed_button_img = set_image("GUI/buttons/button_pressed")
        self.selected_button_img = set_image("GUI/buttons/button_selected")
        self.small_button = self.small_button_img

        self.default_exit_button = set_image("GUI/buttons/exit_button")
        self.selected_exit_button = set_image("GUI/buttons/selected_exit_button")

        self.plus_button = market.plus_button
        self.selected_plus_button = market.selected_plus_button
        self.pressed_plus_button = market.pressed_plus_button
        self.plus_button_img = self.plus_button
        self.minus_button = market.minus_button
        self.selected_minus_button = market.selected_minus_button
        self.pressed_minus_button = market.pressed_minus_button
        self.minus_button_img = self.minus_button

        self.exit_button = self.default_exit_button
        self.button_time = 0
        self.trade_item_rects = []
        self.trade_item_rects_2 = []
        self.trade_rects = []

        self.can_buy = 0
        self.left = SCREEN_WIDTH / 2 - px * 111 / 2
        self.top = SCREEN_HEIGHT / 3
        self.exit_rect = pygame.Rect(self.left + 97 * px, self.top - 9 * px, 13*px, 13*px)
        self.plus_rect = pygame.Rect(0,0,0,0)
        self.minus_rect = pygame.Rect(0,0,0,0)
        self.buy_rect = pygame.Rect(self.left + 80 * px / 2, self.top + tile_size * 1.5 + 9 * px, 31*px, 13*px)
        self.down_rect = pygame.Rect(
            (self.left + tile_size * 3 - px*2, SCREEN_HEIGHT / 3 + tile_size * 4 + px*7, px*9, px*8))
        self.up_rect = pygame.Rect(
            (self.left + tile_size * 3 + px*7, SCREEN_HEIGHT / 3 + tile_size * 4 + px*7, px*9, px*8))
        self.first_trade = 0
        self.s = pygame.Surface((px*9, px*8))
        self.s.set_alpha(100)
        self.state = 0
        self.value = 1
    def draw_trades(self):
        screen.blit(self.trade_base, (self.left, self.top))
        y = self.top + px*6

        # drow arrows
        if self.first_trade + 5 != len(self.trades) and len(self.trades) > 4:
            color_1 = green
        else:
            color_1 = red
        if self.first_trade != 0:
            color_2 = green
        else:
            color_2 = red

        self.s.fill(color_1)
        screen.blit(self.s, (self.left + tile_size * 3 - px*2, SCREEN_HEIGHT / 3 + tile_size * 4 + px*7))
        screen.blit(self.down_scroll,
                    (self.left + tile_size * 3, SCREEN_HEIGHT / 3 + tile_size * 4 + px*8))

        self.s.fill(color_2)
        screen.blit(self.s, (self.left + tile_size * 3 + px*7, SCREEN_HEIGHT / 3 + tile_size * 4 + px*7))
        screen.blit(self.up_scroll,
                    (self.left + tile_size * 3 + px*9, SCREEN_HEIGHT / 3 + tile_size * 4 + px*8))

        # draw trades
        j = self.first_trade
        if len(self.trades) < 4:
            b = len(self.trades) - 1
        else:
            b = 4
        for a in self.trades:
            i = self.trades[j]
            if j < self.first_trade + b:
                if len(i) < 3:

                    img = text_font.render(str(i[1]), True, white)
                    start_x = self.left + ((111*px - (img.get_size()[0] + tile_size*2 + 8*px))/2)

                    draw_text(str(i[1]), text_font, white, start_x,
                              y + px * 5)

                    screen.blit(market.mini_coin, (start_x + px*2 + img.get_size()[0], y + px * 5))
                    screen.blit(market.arrow_icon, (start_x + img.get_size()[0] + 14*px, y + px * 6))
                    screen.blit(i[0]["image"], (start_x + 24*px + img.get_size()[0], y))
                    y += tile_size + px

                else:

                    img = text_font.render(str(i[1]), True, white)
                    img_2 = text_font.render(str(i[2][1]), True, white)

                    start_x = self.left + ((111*px - (tile_size*3  + px *10+ img.get_size()[0] + img_2.get_size()[0]))/2)


                    draw_text(str(i[1]), text_font, white, start_x,
                              y + px * 5)

                    screen.blit(market.mini_coin, (start_x + px * 2 + img.get_size()[0], y + px * 5))
                    screen.blit(self.plus_icon, (start_x + px * 11 + img.get_size()[0], y + px*6))
                    draw_text(str(i[2][1]), text_font, white,
                              start_x + px * 18 + img.get_size()[0], y + px*5)

                    screen.blit(i[2][0]["image"], (start_x + tile_size + px*2 + img.get_size()[0] + img_2.get_size()[0], y))
                    screen.blit(market.arrow_icon, (start_x + tile_size*2+ px*2+ img.get_size()[0] + img_2.get_size()[0], y + px * 6))
                    screen.blit(i[0]["image"], (start_x + tile_size*2  + px *10+ img.get_size()[0] + img_2.get_size()[0], y))
                    y += tile_size + px
            else:
                break
            j += 1

        if self.state == 1:
            screen.blit(self.offer_window, (self.left, self.top))
            screen.blit(self.exit_button, (self.left + 97 * px, self.top - 9 * px))
            if len(self.selected_trade) < 3:
                y  = self.top + tile_size/2 - px
                img = text_font.render(str(self.selected_trade[1]*self.value), True, white)
                start_x = self.left + ((111 * px - (img.get_size()[0] + tile_size * 2 + 8 * px)) / 2)

                draw_text(str(self.selected_trade[1]*self.value), text_font, white, start_x,
                          y + px * 5)

                screen.blit(market.mini_coin, (start_x + px * 2 + img.get_size()[0], y + px * 5))
                screen.blit(market.arrow_icon, (start_x + img.get_size()[0] + 14 * px, y + px * 6))

                screen.blit(self.selected_trade[0]["image"], (start_x + 24 * px + img.get_size()[0], y))

                self.minus_rect = pygame.Rect(start_x + 22 * px + img.get_size()[0], y + tile_size + px, 9 * px,
                                              10 * px)
                self.plus_rect = pygame.Rect(start_x + tile_size * 2 + px + img.get_size()[0], y + tile_size + px,
                                             9 * px, 10 * px)

                screen.blit(self.minus_button_img, (start_x + 22 * px + img.get_size()[0], y + tile_size + px))
                screen.blit(self.plus_button_img, (start_x + tile_size*2 + px + img.get_size()[0], y + tile_size + px))

                draw_text(str(self.value), inventory_text_font, white,
                          start_x + 19 * px + img.get_size()[0] + tile_size ,
                          y + tile_size - px *4)

            else:
                y = self.top + tile_size/2 - px
                img = text_font.render(str(self.selected_trade[1]*self.value), True, white)
                img_2 = text_font.render(str(self.selected_trade[2][1]*self.value), True, white)

                start_x = self.left + (
                            (111 * px - (tile_size * 3 + px * 10 + img.get_size()[0] + img_2.get_size()[0])) / 2)

                draw_text(str(self.selected_trade[1]*self.value), text_font, white, start_x,
                          y + px * 5)

                screen.blit(market.mini_coin, (start_x + px * 2 + img.get_size()[0], y + px * 5))
                screen.blit(self.plus_icon, (start_x + px * 11 + img.get_size()[0], y + px * 6))
                draw_text(str(self.selected_trade[2][1]*self.value), text_font, white,
                          start_x + px * 18 + img.get_size()[0], y + px * 5)

                screen.blit(self.selected_trade[2][0]["image"],
                            (start_x + tile_size + px * 2 + img.get_size()[0] + img_2.get_size()[0], y))
                screen.blit(market.arrow_icon,
                            (start_x + tile_size * 2 + px * 2 + img.get_size()[0] + img_2.get_size()[0], y + px * 6))
                screen.blit(self.selected_trade[0]["image"],
                            (start_x + tile_size * 2 + px * 10 + img.get_size()[0] + img_2.get_size()[0], y))

                self.minus_rect = pygame.Rect(start_x + tile_size * 2 + px * 8 + img.get_size()[0] +
                                              img_2.get_size()[0], y + tile_size + px, 9 * px, 10 * px)
                self.plus_rect = pygame.Rect(start_x + tile_size * 3 + px * 3 + img.get_size()[0] +
                                             img_2.get_size()[0], y + tile_size + px, 9 * px, 10 * px)
                screen.blit(self.minus_button_img, (start_x + tile_size * 2 + px * 8 + img.get_size()[0] +
                                                img_2.get_size()[0], y + tile_size + px))
                screen.blit(self.plus_button_img, (start_x + tile_size * 3 + px * 3 + img.get_size()[0] +
                                               img_2.get_size()[0], y + tile_size + px))

                draw_text(str(self.value), inventory_text_font, white,
                          start_x + tile_size * 3 + px * 5 + img.get_size()[0] + img_2.get_size()[0],
                          y + tile_size - px * 4)
            screen.blit(self.small_button, (self.left + 40*px, y + tile_size + 12*px))
            draw_text("buy", text_font, white, self.left + 40*px, y + tile_size + 15*px, True)

    def draw_item_info(self, item, pos, value=None):
        s = pygame.Surface((tile_size * 3, tile_size))
        s.set_alpha(300)
        s.fill((50*px, 25*px, 0))
        screen.blit(s, pos)
        draw_text(item["name"], inventory_text_font, white, pos[0] + px*2, pos[1] + px*2)

    def handle_trades(self):
        pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(pos[0], pos[1], 3, 3)
        y = SCREEN_HEIGHT / 3 + px*6
        if self.state == 0:

            # Scrolling
            if mouse_rect.colliderect(self.down_rect):
                if player.left_clicked and self.can_buy == 0 and self.first_trade + 5 != len(self.trades) and len(
                        self.trades) > 4:
                    self.first_trade += 1
                    self.can_buy += 1
                    self.trade_rects = []
                    self.trade_item_rects = []
                    self.trade_item_rects_2 = []
            elif mouse_rect.colliderect(self.up_rect):
                if player.left_clicked and self.can_buy == 0 and self.first_trade != 0:
                    self.first_trade -= 1
                    self.can_buy += 1
                    self.trade_rects = []
                    self.trade_item_rects = []
                    self.trade_item_rects_2 = []


            if len(self.trades) < 4:
                b = len(self.trades) - 1
            else:
                b = 4


            # create trade_item_rects
            j = self.first_trade
            if not self.trade_item_rects:
                for i in range(b):
                    start_x = None
                    if len(self.trades[j]) >= 3:
                        i = self.trades[j]
                        img = text_font.render(str(i[1]), True, white)
                        img_2 = text_font.render(str(i[2][1]), True, white)

                        start_x = self.left + (
                                    (111 * px - (tile_size * 3 + px * 10 + img.get_size()[0] + img_2.get_size()[0])) / 2)
                        rect_2 = pygame.Rect((start_x + tile_size + px*2 + img.get_size()[0] + img_2.get_size()[0], y, tile_size, tile_size))

                        self.trade_item_rects_2.append(rect_2)
                    else:
                        self.trade_item_rects_2.append(None)
                    if start_x is not None:
                        rect = pygame.Rect((start_x + tile_size*2  + px *10+ img.get_size()[0] + img_2.get_size()[0], y, tile_size, tile_size))
                    else:
                        i = self.trades[j]
                        img = text_font.render(str(i[1]), True, white)
                        start_x = self.left + ((111 * px - (img.get_size()[0] + tile_size * 2 + 8 * px)) / 2)
                        rect = pygame.Rect((start_x + 24*px + img.get_size()[0], y,
                                            tile_size, tile_size))
                    self.trade_item_rects.append(rect)
                    y += tile_size + px
                    j += 1

            # show item info
            j = self.first_trade
            y = SCREEN_HEIGHT / 3 + px*6
            for i in self.trade_item_rects:
                if mouse_rect.colliderect(i):
                    self.draw_item_info(self.trades[j][0], (self.left - tile_size * 3, y))
                j += 1
                y += tile_size + px

            # show item info2
            j = self.first_trade
            y = SCREEN_HEIGHT / 3 + px*6
            for i in self.trade_item_rects_2:
                if i is not None:
                    if mouse_rect.colliderect(i):
                        self.draw_item_info(self.trades[j][2][0],
                                            (self.left - tile_size * 3, y),
                                            (self.has_item(self.trades[j][2][0]), (self.trades[j][2][1])))
                j += 1
                y += tile_size + px


            # create trade rects
            y = SCREEN_HEIGHT / 3 + px*6
            c = self.first_trade
            if not self.trade_rects:
                for i in range(b):
                    i = self.trades[c]
                    if len(self.trades[c]) >= 3:
                        img = text_font.render(str(i[1]), True, white)
                        img_2 = text_font.render(str(i[2][1]), True, white)

                        start_x = self.left + (
                                (111 * px - (tile_size * 3 + px * 10 + img.get_size()[0] + img_2.get_size()[0])) / 2)

                        rect = pygame.Rect((start_x, y + px*4, tile_size * 3 + px * 10 + img.get_size()[0] + img_2.get_size()[0], px*9))
                    else:
                        img = text_font.render(str(i[1]), True, white)
                        start_x = self.left + ((111 * px - (img.get_size()[0] + tile_size * 2 + 8 * px)) / 2)
                        rect = pygame.Rect((start_x, y + px*3, img.get_size()[0] + tile_size * 2 + 8 * px, px*10))
                    self.trade_rects.append(rect)
                    y += tile_size + px
                    c += 1

            # check trade rects
            j = self.first_trade
            for y in self.trade_rects:
                if mouse_rect.colliderect(y):
                    if player.left_clicked:
                        self.selected_trade = self.trades[j]
                        player.left_clicked = False

                        self.state = 1
                j += 1
        else:
            # Buy
            if self.button_time > 0:
                self.button_time -=1
            if mouse_rect.colliderect(self.buy_rect):
                if self.button_time == 0:
                    self.small_button = self.selected_button_img
                    self.plus_button_img = self.plus_button
                    self.minus_button_img = self.minus_button
                if player.left_clicked:
                    if len(self.selected_trade) < 3:
                            if player.left_clicked and player.currency >= self.selected_trade[1]*self.value and self.can_buy == 0:
                                self.small_button = self.pressed_button_img
                                self.button_time = 20
                                items.set_item(self.selected_trade[0], player.pos_x, player.pos_y, self.value)
                                player.currency -= self.selected_trade[1]*self.value
                                self.can_buy += 1
                    else:
                            if player.left_clicked and player.currency >= self.selected_trade[1]*self.value and self.can_buy == 0 and \
                                    self.has_item(self.selected_trade[2][0]) >= self.selected_trade[2][1]*self.value:
                                self.small_button = self.pressed_button_img
                                self.button_time = 20
                                self.remove_items(self.selected_trade[2][0], self.selected_trade[2][1]*self.value)
                                items.set_item(self.selected_trade[0], player.pos_x, player.pos_y, self.value)
                                player.currency -= self.selected_trade[1]*self.value
                                self.can_buy += 1



            elif mouse_rect.colliderect(self.exit_rect):
                self.exit_button = self.selected_exit_button
                if player.left_clicked:
                    self.selected_trade = None
                    self.value = 1
                    self.state = 0
            elif mouse_rect.colliderect(self.minus_rect):
                if self.button_time == 0:
                    self.minus_button_img = self.selected_minus_button
                    self.plus_button_img = self.plus_button
                    self.small_button = self.small_button_img
                if player.left_clicked:
                    if self.value > 1 and self.can_buy == 0:
                        self.button_time = 20
                        self.minus_button_img = self.pressed_minus_button
                        self.can_buy = 1
                        self.value -= 1
            elif mouse_rect.colliderect(self.plus_rect):
                if self.button_time == 0:
                    self.plus_button_img = self.selected_plus_button
                    self.small_button = self.small_button_img
                    self.minus_button_img = self.minus_button
                if player.left_clicked:
                    if self.selected_trade[1]*(self.value + 1) < 1000 and self.can_buy == 0 and\
                        self.value < self.selected_trade[0]["max_stack"]:
                        self.button_time = 20
                        self.plus_button_img = self.pressed_plus_button
                        self.can_buy = 1
                        self.value += 1
            else:
                self.small_button = self.small_button_img
                self.exit_button = self.default_exit_button
                self.plus_button_img = self.plus_button
                self.minus_button_img = self.minus_button

        if self.can_buy > 0 and self.can_buy != 12:
            self.can_buy += 1
        elif self.can_buy == 12:
            self.can_buy = 0



    def has_item(self, item):
        number = 0
        for i in inventory.inventory_slots:
            if i["item"] is not None:
                if i["item"]["name"] == item["name"]:
                    number += i["value"]
        return number

    def remove_items(self, item, value):
        for i in inventory.inventory_slots:
            if i["item"] is not None:
                if i["item"]["name"] == item["name"]:
                    while value != 0 and i["value"] != 0:
                        i["value"] -= 1
                        value -= 1

    def leave_trade(self):
        self.trade_rects = []
        self.trade_item_rects = []
        self.trade_item_rects_2 = []
        self.trade_rects = []
        self.first_trade = 0
        self.state = 0
        self.value = 1
        self.selected_trade = None


class blocks:
    def __init__(self):
        self.all_fences = []
        self.pos_x = 0
        self.pos_y = 0
        self.random_tick_speed = 10
        self.trunk = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/trunk.png'), (tile_size, 14 * px)),
            "hitbox": pygame.Rect(px, 0, tile_size - px*2, tile_size - px*2), "max_life": 3,
            "life": 3,
            "x": 0, "y": 0, "def_hit_box": [px, 0, tile_size - px*2, tile_size - px*2],
            "name": "trunk"}
        self.small_trunk = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/small_trunk.png'), (px*7, px*8)),
            "hitbox": pygame.Rect(px, 0, px*4, px*8), "max_life": 3,
            "life": 2,
            "x": 0, "y": 0, "def_hit_box": [px, 0, px*4, px*8],
            "name": "small_trunk"}
        self.tree_2 = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/tree_2.png'), (41 * px, 63 * px)),
            "hitbox": pygame.Rect(tile_size - px*2, tile_size * 2 + px*10, tile_size - px*2, tile_size - px), "max_life": 3,
            "life": 3,
            "x": 0, "y": 0, "def_hit_box": [tile_size - px*2, tile_size * 2 + px*10, tile_size - px*2, tile_size - px],
            "name": "tree_2", "second_block": [self.trunk, 13*px, tile_size*2 + px*11]}
        self.small_tree = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/small_tree.png'), (23 * px, 34 * px)),
            "hitbox": pygame.Rect(tile_size - px*2, tile_size * 2 + px*10, tile_size - px*2, tile_size - px), "max_life": 3,
            "life": 3,
            "x": 0, "y": 0, "def_hit_box": [px*9, tile_size + px*5, px*4, tile_size - px*6],
            "name": "small_tree", "second_block": [self.small_trunk, px*8, tile_size + px*7],
            "grow_to": (self.tree_2, - px*10, -25*px)}
        self.sapling = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/sapling.png'), (tile_size, tile_size)),
            "hitbox": pygame.Rect(tile_size - px*2, tile_size, tile_size - px*2, tile_size - px), "max_life": 3,
            "life": 1,
            "x": 0, "y": 0, "def_hit_box": [px*6, px*10, px*4, px*6],
            "name": "sapling", "grow_to": (self.small_tree, - px*4, -tile_size + px*2)}


        self.log = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/log.png'), (25*px, 11 * px)),
            "hitbox": pygame.Rect(3, 0, tile_size + px*6, tile_size - px*5), "max_life": 3,
            "life": 2,
            "x": 0, "y": 0, "def_hit_box": [px, 0, tile_size + px*6, tile_size - px*5],
            "name": "log"}
        self.bush = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/block_bush.png'), (tile_size, tile_size)),
            "hitbox": pygame.Rect(0, tile_size - px*6, tile_size, 21), "max_life": 1, "life": 1, "x": 0, "y": 0,
            "def_hit_box": [px*2, tile_size - px*8, tile_size-px*4, px*8], "name": "bush"}
        fence_hitbox = [5*px, tile_size - px*9, 6*px, 10*px]
        self.fence_0 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_0.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, tile_size - px*8, 33, 30), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_0"}
        self.fence_1 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_1.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(0, tile_size - px*8, tile_size, 30), "max_life": 2, "life": 2, "x": 0,
                        "y": 0, "def_hit_box": fence_hitbox, "fence": True, "name": "fence_1"}
        self.fence_2 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_2.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(0, tile_size - px*8, tile_size - px*5, 30), "max_life": 2, "life": 2, "x": 0,
                        "y": 0, "def_hit_box": fence_hitbox, "fence": True, "name": "fence_2"}
        self.fence_3 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_3.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_3"}
        self.fence_4 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_4.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(0, tile_size - px*8, 33, 30), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_4"}
        self.fence_6 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_5.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, tile_size - px*8, tile_size - px*5, 30), "max_life": 2, "life": 2, "x": 0,
                        "y": 0, "def_hit_box": fence_hitbox, "fence": True, "name": "fence_6"}
        self.fence_8 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_10.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_8"}
        self.fence_9 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_7.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_9"}
        self.fence_10 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_8.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_10"}
        self.fence_11 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_11.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_11"}
        self.fence_12 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_13.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_12"}
        self.fence_13 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_9.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_13"}
        self.fence_14 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_6.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_14"}
        self.fence_15 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_12.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_15"}
        self.fence_16 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_15.png'),
                                                        (tile_size, tile_size)),
                        "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                        "def_hit_box": fence_hitbox, "fence": True, "name": "fence_16"}
        self.fence_17 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/block_fence_14.png'),
                                                         (tile_size, tile_size)),
                         "hitbox": pygame.Rect(15, 6, 18, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
                         "def_hit_box": fence_hitbox, "fence": True, "name": "fence_17"}

        self.gate = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/gate_closed.png'),
                                                     (tile_size, tile_size)),
                     "image_2": pygame.transform.scale(pygame.image.load('assets/blocks/gate_opened.png'),
                                                       (tile_size, tile_size)),
                     "hitbox": pygame.Rect(0, tile_size - px*8, tile_size, 10*px), "max_life": 2, "life": 2, "x": 0,
                     "y": 0, "def_hit_box": [0, tile_size - px*8, tile_size, 10*px], "interactable": 0, "fence": True,
                     "num": 0,"name": "gate"}
        self.gate_1 = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/gate_closed_1.png'),
                                                     (tile_size, tile_size)),
                     "image_2": pygame.transform.scale(pygame.image.load('assets/blocks/gate_opened_1.png'),
                                                       (tile_size, tile_size)),
                     "hitbox": pygame.Rect(0, tile_size - px*8, tile_size, 10*px), "max_life": 2, "life": 2, "x": 0,
                     "y": 0, "def_hit_box": [5*px, tile_size - px*14, 6*px, 15*px], "interactable": 0, "fence": True, "num": 0,
                     "name": "gate_1"}

        self.market = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/market_desk.png'),
                                                       (tile_size * 3, tile_size * 2)),
                       "hitbox": pygame.Rect(0, 9, tile_size * 3, tile_size * 2 - px), "max_life": 5, "life": 5,
                       "x": 0,
                       "y": 0, "def_hit_box": [0, 9, tile_size * 3, tile_size * 2 - px], "interactable": 2,
                       "num": 0, "name": "market"}
        self.hay_bale = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/hay_bale.png'), (tile_size, tile_size)),
            "hitbox": pygame.Rect(0, tile_size - px*10, tile_size, 36), "max_life": 2, "life": 2, "x": 0, "y": 0,
            "def_hit_box": [0, tile_size - px*10, tile_size, 12*px], "name": "hay_bale"}
        self.water_bucket = {"image": pygame.transform.scale(pygame.image.load('assets/blocks/water_bucket.png'),
                                                             (tile_size, tile_size)),
                             "hitbox": pygame.Rect(px, tile_size - px*10, tile_size - px*3, px*12), "max_life": 2, "life": 2,
                             "x": 0,
                             "y": 0, "def_hit_box": [px, tile_size - px*10, tile_size - px*3, px*12], "name": "water_bucket"}
        self.milk_bucket = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/milk_bucket.png'), (tile_size, tile_size)),
            "hitbox": pygame.Rect(px, tile_size - px*10, tile_size - px*3, px*12), "max_life": 2, "life": 2, "x": 0, "y": 0,
            "def_hit_box": [px, tile_size - px*10, tile_size - px*3, px*12], "name": "milk_bucket"}
        self.bucket = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/bucket.png'), (tile_size, tile_size)),
            "hitbox": pygame.Rect(px, tile_size - px*10, tile_size - px*3, px*12), "max_life": 2, "life": 2, "x": 0, "y": 0,
            "def_hit_box": [px, tile_size - px*10, tile_size - px*3, px*12], "name": "bucket"}
        self.feeder = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/feeder.png'), (tile_size * 2, tile_size)),
            "hitbox": pygame.Rect(0, px*4, tile_size * 2, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
            "def_hit_box": [px, px*4, tile_size * 2 - px*2, tile_size - px*4], "name": "feeder"}
        self.drinker = {
            "image": pygame.transform.scale(pygame.image.load('assets/blocks/drinker.png'), (tile_size * 2, tile_size)),
            "hitbox": pygame.Rect(0, px*4, tile_size * 2, tile_size - px*2), "max_life": 2, "life": 2, "x": 0, "y": 0,
            "def_hit_box": [px, px*4, tile_size * 2 - px*2, tile_size - px*4], "name": "drinker"}

        self.blocks = [self.tree_2, self.bush, self.fence_6, self.fence_4, self.fence_3, self.fence_2,
                       self.fence_1, self.fence_0, self.bucket, self.milk_bucket, self.water_bucket, self.hay_bale,
                       self.drinker, self.feeder, self.gate, self.gate_1, self.market, self.trunk, self.log, self.small_trunk, self.small_tree,
                       self.sapling, self.fence_8, self.fence_9, self.fence_10, self.fence_11, self.fence_12, self.fence_13,
                       self.fence_14, self.fence_15, self.fence_16, self.fence_17]
        self.fences = [self.fence_8, self.fence_14, self.fence_9, self.fence_6, self.fence_13, self.fence_3, self.fence_0,
                       self.fence_17, self.fence_10, self.fence_4, self.fence_1, self.fence_12, self.fence_2, self.fence_15,
                       self.fence_11, self.fence_16]

        self.default_hitbox = (0, 0, tile_size, tile_size + px*2)
        self.all_blocks = []

    def draw_blocks(self):
        for block in self.all_blocks:
            if block["hitbox"].colliderect(screen_rect):
                screen.blit(block["image"], (block["x"] + cam.transform_x, block["y"] + cam.transform_y))
        if dev_tools == True:
            for box in self.all_blocks:
                if box["hitbox"].colliderect(screen_rect):
                    pygame.draw.rect(screen, (0, 0, 0), box["hitbox"])

    def set_block(self, block, pos):
        block_copy = block.copy()
        block_copy["x"], block_copy["y"] = pos[0], pos[1]
        hit_box = block_copy["def_hit_box"].copy()
        hit_box[0] += pos[0] + cam.transform_x
        hit_box[1] += pos[1] + cam.transform_y
        block_copy["hitbox"] = pygame.Rect(hit_box[0], hit_box[1], hit_box[2], hit_box[3])

        for block in self.all_blocks:
            if block_copy["y"] + block_copy["image"].get_size()[1] <= block["y"] + block["image"].get_size()[1]:
                block_copy_rect = pygame.Rect(block_copy["x"], block_copy["y"], block_copy["image"].get_size()[0],
                                              block_copy["image"].get_size()[1])
                block_rect = pygame.Rect(block["x"], block["y"], block["image"].get_size()[0],
                                              block["image"].get_size()[1])
                if block_copy_rect.colliderect(block_rect):
                    self.all_blocks.insert(self.all_blocks.index(block) - 1, block_copy)
                    if "fence" in block_copy:
                        self.all_fences.append(block_copy)
                        self.organize_fences()
                    return
        self.all_blocks.append(block_copy)
        if "fence" in block_copy:
            self.all_fences.append(block_copy)
            self.organize_fences()

    def update_blocks(self):
        for block in self.all_blocks:

            if "grow_to" in block:
                if random.randint(1, self.random_tick_speed * 1000) == 1:
                    blocks.set_block(block["grow_to"][0], (block["x"] + block["grow_to"][1], block["y"] +
                                                           block["grow_to"][2]))
                    blocks.all_blocks.remove(block)

            block["hitbox"].x = block["x"] + cam.transform_x + block["def_hit_box"][0]
            block["hitbox"].y = block["y"] + cam.transform_y + block["def_hit_box"][1]

    def set_blocks(self, start_x, start_y):
        self.pos_x = start_x + tile_size * 8
        self.pos_y = start_y - tile_size * 2
        # TREES
        for tree in range(12):
            self.set_block(self.tree_2, (self.pos_x, self.pos_y))
            self.pos_x += tile_size * 3
        self.pos_x = start_x + tile_size * 6.5
        self.pos_y -= tile_size * -2
        for tree in range(13):
            self.set_block(self.tree_2, (self.pos_x, self.pos_y))
            self.pos_x += tile_size * 3
        self.pos_x = start_x + tile_size * 5
        self.pos_y -= tile_size * -2
        for tree in range(13):
            self.set_block(self.tree_2, (self.pos_x, self.pos_y))
            self.pos_x += tile_size * 3

        self.pos_x = tile_size * 12
        self.pos_y = 0
        self.set_block(self.small_tree, (self.pos_x, self.pos_y))
        self.pos_x = tile_size * -1
        self.pos_y = tile_size * 12
        self.set_block(self.small_tree, (self.pos_x, self.pos_y))
        self.pos_x = tile_size * -5
        self.pos_y = tile_size * 4
        self.set_block(self.bush, (self.pos_x, self.pos_y))
        self.set_block(self.market, (tile_size*-2, tile_size*3))

    def set_drops(self):
        self.tree_2["drop"] = (items.wood, 6, items.sapling, 2)
        self.trunk["drop"] = (items.wood, 4)
        self.small_tree["drop"] = (items.wood, 4)
        self.sapling["drop"] = (items.sapling, 1)
        self.small_trunk["drop"] = (items.wood, 2)
        self.log["drop"] = (items.wood, 3)
        self.bush["drop"] = (items.wood, 5)
        self.fence_0["drop"] = (items.fence_1, 1)
        self.fence_1["drop"] = (items.fence_1, 1)
        self.fence_2["drop"] = (items.fence_1, 1)
        self.fence_3["drop"] = (items.fence_1, 1)
        self.fence_4["drop"] = (items.fence_1, 1)
        self.fence_6["drop"] = (items.fence_1, 1)
        self.fence_8["drop"] = (items.fence_1, 1)
        self.fence_9["drop"] = (items.fence_1, 1)
        self.fence_10["drop"] = (items.fence_1, 1)
        self.fence_11["drop"] = (items.fence_1, 1)
        self.fence_12["drop"] = (items.fence_1, 1)
        self.fence_13["drop"] = (items.fence_1, 1)
        self.fence_14["drop"] = (items.fence_1, 1)
        self.fence_15["drop"] = (items.fence_1, 1)
        self.fence_16["drop"] = (items.fence_1, 1)
        self.fence_17["drop"] = (items.fence_1, 1)

        self.hay_bale["drop"] = (items.hay_bale, 1)
        self.gate["drop"] = (items.gate, 1)
        self.gate_1["drop"] = (items.gate, 1)
        self.drinker["drop"] = (items.drinker, 1)
        self.feeder["drop"] = (items.feeder, 1)
        self.bucket["drop"] = (items.bucket, 1)
        self.milk_bucket["drop"] = (items.milk_bucket, 1)
        self.water_bucket["drop"] = (items.water_bucket, 1)
        self.market["drop"] = (items.market, 1)

    def drop_item(self, item, pos):

        items.set_item(item[0], pos[0] + random.randint(-tile_size, tile_size),
                       pos[1] + random.randint(-tile_size, tile_size), random.randint(1, item[1]))
        if len(item) > 2:

            items.set_item(item[2], pos[0] + random.randint(-tile_size, tile_size),
                           pos[1] + random.randint(-tile_size, tile_size), random.randint(1, item[3]))

    def draw_life_bar(self, block, max_life, life):
        dialogues.block = block
        dialogues.max_life = max_life
        dialogues.life = life

    def organize_fences(self):

        for fence in self.all_fences:

            hitbox_top = pygame.Rect(fence["x"] + cam.transform_x, fence["y"] - tile_size/2 + cam.transform_y,
                                     tile_size, tile_size/2)
            hitbox_right = pygame.Rect(fence["x"] + tile_size + cam.transform_x, fence["y"] + cam.transform_y + px*8,
                                       tile_size, tile_size - px*8)
            hitbox_bottom = pygame.Rect(fence["x"] + cam.transform_x, fence["y"] + tile_size + cam.transform_y,
                                        tile_size, tile_size)
            hitbox_left = pygame.Rect(fence["x"] - tile_size + cam.transform_x, fence["y"] + cam.transform_y + px*8,
                                      tile_size, tile_size - px*8)

            code = [0, 0, 0, 0]

            for i in self.all_fences:
                if i != fence:
                    if hitbox_top.colliderect(i["hitbox"]):
                        code[0] = 1
                    elif hitbox_right.colliderect(i["hitbox"]):
                        code[1] = 1
                    elif hitbox_bottom.colliderect(i["hitbox"]):
                        code[2] = 1
                    elif hitbox_left.colliderect(i["hitbox"]):
                        code[3] = 1
            index = code[0] + code[1]*2 + code[2]*4 + code[3]*8
            if fence["name"] != "gate" and fence["name"] != "gate_1":
                block_copy = self.fences[index].copy()
                block_copy["x"], block_copy["y"] = fence["x"], fence["y"]
                hit_box = block_copy["def_hit_box"].copy()
                hit_box[0] += block_copy["x"] + cam.transform_x
                hit_box[1] += block_copy["y"] + cam.transform_y
                block_copy["hitbox"] = pygame.Rect(hit_box[0], hit_box[1], hit_box[2], hit_box[3])

                if block_copy != fence:
                    self.all_fences.insert(self.all_fences.index(fence) - 1, block_copy)
                    self.all_fences.remove(fence)
                    for block in self.all_blocks:
                        if block_copy["y"] + block_copy["image"].get_size()[1] <= block["y"] + block["image"].get_size()[1]:
                            block_copy_rect = pygame.Rect(block_copy["x"], block_copy["y"],
                                                          block_copy["image"].get_size()[0],
                                                          block_copy["image"].get_size()[1])
                            block_rect = pygame.Rect(block["x"], block["y"], block["image"].get_size()[0],
                                                     block["image"].get_size()[1])
                            if block_copy_rect.colliderect(block_rect):
                                self.all_blocks.insert(self.all_blocks.index(block) - 1, block_copy)
                                break
                    self.all_blocks.remove(fence)
            else:
                if code == [0, 1, 0, 1] or code == [0, 1, 0, 0] or code == [0, 0 ,0, 1]:
                    block_copy = self.gate.copy()
                elif code == [1, 0, 1, 0] or code == [1, 0, 0, 0] or code == [0, 0 ,1, 0]:
                    block_copy = self.gate_1.copy()
                else:
                    block_copy = fence

                block_copy["x"], block_copy["y"] = fence["x"], fence["y"]
                hit_box = block_copy["def_hit_box"].copy()
                hit_box[0] += block_copy["x"] + cam.transform_x
                hit_box[1] += block_copy["y"] + cam.transform_y
                block_copy["hitbox"] = pygame.Rect(hit_box[0], hit_box[1], hit_box[2], hit_box[3])

                if block_copy != fence:
                    self.all_fences.insert(self.all_fences.index(fence) - 1, block_copy)
                    self.all_fences.remove(fence)
                    for block in self.all_blocks:
                        if block_copy["y"] + block_copy["image"].get_size()[1] <= block["y"] + \
                                block["image"].get_size()[1]:
                            block_copy_rect = pygame.Rect(block_copy["x"], block_copy["y"],
                                                          block_copy["image"].get_size()[0],
                                                          block_copy["image"].get_size()[1])
                            block_rect = pygame.Rect(block["x"], block["y"], block["image"].get_size()[0],
                                                     block["image"].get_size()[1])
                            if block_copy_rect.colliderect(block_rect):
                                self.all_blocks.insert(self.all_blocks.index(block) - 1, block_copy)
                                break
                    self.all_blocks.remove(fence)





class dialogues:
    def __init__(self):
        self.block = None
        self.max_life = None
        self.life = None

    def draw_block_life_bar(self):
        if self.block is not None:
            if player.attack_time < 24:
                pygame.draw.rect(screen, (0, 0, 0), (
                    self.block["x"] + cam.transform_x + self.block["def_hit_box"][0],
                    self.block["y"] + cam.transform_y + self.block["def_hit_box"][1], tile_size, 15))
                pygame.draw.rect(screen, (255, 0, 0), (
                    self.block["x"] + cam.transform_x + px + self.block["def_hit_box"][0],
                    self.block["y"] + cam.transform_y + self.block["def_hit_box"][1] + px, tile_size - px*2,
                    9))
                pygame.draw.rect(screen, (0, 255, 0), (
                    self.block["x"] + cam.transform_x + px + self.block["def_hit_box"][0],
                    self.block["y"] + cam.transform_y + self.block["def_hit_box"][1] + px,
                    (tile_size - px) / self.max_life * self.life, 9))
            else:
                self.block = None
                self.max_life = None
                self.life = None


class items:
    def __init__(self):
        self.time = 0
        self.pos_x = 0
        self.pos_y = 0
        self.all_items = []
        self.cow = {"image": pygame.transform.scale(pygame.image.load("assets/entity/cow/cow_down_1.png"),
                                                    (tile_size, tile_size)),
                    "x": 0, "y": 0, "max_stack": 1, "price": 100, "placeable": False, "name": "cow", "entity": cow}
        self.axe = {"image": pygame.transform.scale(pygame.image.load("assets/items/axe.png"), (tile_size, tile_size)),
                    "x": 0, "y": 0, "max_stack": 1, "price": 25, "placeable": False, "name": "axe", "durability": 50,
                    "max_durability": 50,
                    "strength": 1}
        self.milk = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/milk.png"), (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 15, "placeable": False, "name": "milk"}
        self.wood = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/wood.png"), (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 2, "placeable": False, "name": "wood"}
        self.sapling = {
            "image": pygame.transform.scale(pygame.image.load("assets/blocks/sapling.png"), (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 2, "placeable": True, "name": "sapling", "block_state": blocks.sapling}
        self.cheese = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/cheese.png"), (tile_size, tile_size)),
            "x": 0,
            "y": 0, "max_stack": 64, "price": 50, "placeable": False, "name": "Smoked\ncheese"}
        self.cheese_2 = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/cheese_2.png"), (tile_size, tile_size)),
            "x": 0,
            "y": 0, "max_stack": 64, "price": 50, "placeable": False, "name": "Trappist\ncheese"}
        self.fence_1 = {
            "image": pygame.transform.scale(blocks.fence_1["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 2, "placeable": True, "name": "fence", "block_state": blocks.fence_1}
        self.gate = {
            "image": pygame.transform.scale(blocks.gate["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 2, "placeable": True, "name": "gate", "block_state": blocks.gate}
        self.bucket = {
            "image": pygame.transform.scale(blocks.bucket["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 8, "placeable": True, "name": "bucket",
            "block_state": blocks.bucket}
        self.milk_bucket = {
            "image": pygame.transform.scale(blocks.milk_bucket["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 8, "placeable": True, "name": "milk_bucket",
            "block_state": blocks.milk_bucket}
        self.water_bucket = {
            "image": pygame.transform.scale(blocks.water_bucket["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 8, "placeable": True, "name": "water_bucket",
            "block_state": blocks.water_bucket}
        self.drinker = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/drinker_item.png"),
                                            (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 10, "placeable": True, "name": "drinker",
            "block_state": blocks.drinker}

        self.feeder = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/feeder_item.png"),
                                            (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 10, "placeable": True, "name": "feeder",
            "block_state": blocks.feeder}

        self.hay_bale = {
            "image": pygame.transform.scale(blocks.hay_bale["image"], (tile_size, tile_size)), "x": 0,
            "y": 0, "max_stack": 64, "price": 10, "placeable": True, "name": "hay_bale",
            "block_state": blocks.hay_bale}
        self.market = {
            "image": pygame.transform.scale(pygame.image.load("assets/items/market_item.png"),(tile_size, tile_size)),
                                            "x": 0, "y": 0, "max_stack": 64, "price": 50, "placeable": True,
            "name": "market", "block_state": blocks.market}
        self.items = [self.cow, self.axe, self.milk, self.cheese, self.cheese_2, self.wood, self.fence_1, self.gate,
                      self.feeder, self.drinker, self.hay_bale, self.bucket, self.milk_bucket, self.water_bucket,
                      self.market, self.sapling]

    def set_item(self, item, x, y, value=1):
        item_copy = item.copy()
        item_copy["x"] = x
        item_copy["y"] = y
        item_copy["hitbox"] = pygame.Rect(x + cam.transform_x, y + cam.transform_y, tile_size, tile_size)
        for i in range(value):
            self.all_items.append(item_copy.copy())
        self.time = 0
        #self.reset_items()

    def draw_items(self):
        for i in self.all_items:
            if i["hitbox"].colliderect(screen_rect):
                screen.blit(i["image"], (i["x"] + cam.transform_x, i["y"] + cam.transform_y))

    def update_hitboxes(self):
        for item in self.all_items:
            i = item
            i["hitbox"] = pygame.Rect(i["x"] + cam.transform_x, i["y"] + cam.transform_y, tile_size, tile_size)
            if dev_tools:
                for i in self.all_items:
                    pygame.draw.rect(screen, (0, 255, 0), i["hitbox"])

    def move_to_player(self):
        if self.time == 45:
            for i in self.all_items:
                if i["x"] < player.pos_x:
                    i["x"] += 6
                elif i["x"] > player.pos_x:
                    i["x"] -= 6
            for i in self.all_items:
                if i["y"] < player.pos_y:
                    i["y"] += 6
                elif i["y"] > player.pos_y:
                    i["y"] -= 6
        elif self.time < 45:
            self.time += 1
        else:
            self.time = 0

class inventory:
    def __init__(self):
        self.left = SCREEN_WIDTH / 2 - px * 111 / 2
        self.selected_slot = 0
        self.to_change_slot_1 = None
        self.to_change_slot_2 = None
        self.main_inv_img = pygame.transform.scale(pygame.image.load('assets/GUI/bases/inventory.png'), (111 * px, 77 * px))
        self.hot_bar_img = pygame.transform.scale(pygame.image.load('assets/GUI/bases/hot_bar.png'), (111 * px, 26 * px))
        self.selected_slot_img = pygame.transform.scale(pygame.image.load('assets/GUI/icons/selected_slot.png'), (18 * px, 18 * px))
        self.inventory_slots = [{"item": items.axe.copy(), "value": 1}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0},
                                {"item": None, "value": 0}, {"item": None, "value": 0}, {"item": None, "value": 0}]
        self.slot_hitboxes = []
        x = self.left + px*5
        y = SCREEN_HEIGHT - 26 * px
        for i in range(30):
            hitbox = pygame.Rect(x, y, tile_size, tile_size)
            self.slot_hitboxes.append(hitbox)
            x += px*17
            if i == 5:
                x = self.left + px*5
                y = SCREEN_HEIGHT - tile_size * 7 - px*11
            if i == 11:
                x = self.left + px*5
                y = SCREEN_HEIGHT - tile_size * 7 - px*11 + px*17
            if i == 17:
                x = self.left + px*5
                y = SCREEN_HEIGHT - tile_size * 7 - px*11 + px*34
            if i == 23:
                x = self.left + px*5
                y = SCREEN_HEIGHT - tile_size * 7 - px*11 + px*51
            if i == 29:
                x = self.left + px*5
                y = SCREEN_HEIGHT - tile_size * 7 - px*11 + px*68
        self.hand_item = self.inventory_slots[self.selected_slot]["item"]
        self.shift_clicked = False

    def draw_inventory(self):
        if game_state == inventory_state or market.state == 1 or market.state == 2:
            screen.blit(self.main_inv_img, (self.left, SCREEN_HEIGHT / 3))
        screen.blit(self.hot_bar_img, (self.left, SCREEN_HEIGHT - 26 * px - px*5))
        if self.selected_slot <= 5:
            y = SCREEN_HEIGHT - 26 * px - px
        elif self.selected_slot <= 11:
            y = SCREEN_HEIGHT - tile_size * 7 - px*12
        elif self.selected_slot <= 17:
            y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*17
        elif self.selected_slot <= 23:
            y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*34
        elif self.selected_slot <= 29:
            y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*51
        else:
            y = 0
        x_slot = self.selected_slot
        while x_slot > 5:
            x_slot -= 6
        screen.blit(self.selected_slot_img, (self.left + px*4 + x_slot * px*17, y))

        if self.to_change_slot_1 is not None:
            x_slot = self.to_change_slot_1
            while x_slot > 5:
                x_slot -= 6
            if self.to_change_slot_1 <= 5:
                y = SCREEN_HEIGHT - 26 * px - px
            elif self.to_change_slot_1 <= 11:
                y = SCREEN_HEIGHT - tile_size * 7 - px*12
            elif self.to_change_slot_1 <= 17:
                y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*17
            elif self.to_change_slot_1 <= 23:
                y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*34
            elif self.to_change_slot_1 <= 29:
                y = SCREEN_HEIGHT - tile_size * 7 - px*12 + px*51
            screen.blit(self.selected_slot_img, (self.left + px*4 + x_slot * px*17, y))

        x = self.left + px*5
        y = SCREEN_HEIGHT - tile_size
        for i in range(len(self.inventory_slots)):
            slot = self.inventory_slots[i]
            if i >= 6:
                if i >= 6:
                    y = SCREEN_HEIGHT / 3 + px*5
                if i >= 12:
                    y = SCREEN_HEIGHT / 3 + px*22
                if i >= 18:
                    y = SCREEN_HEIGHT / 3 + px*39
                if i >= 24:
                    y = SCREEN_HEIGHT / 3 + px*39 + px*17
                if i == 6 or i == 12 or i == 18 or i == 24:
                    x = self.left + px*5
                if game_state == inventory_state or market.state == 1 or market.state == 2:
                    if slot["item"] is not None:
                        screen.blit(slot["item"]["image"], (x, y))
                        if "durability" in slot["item"]:
                            if slot["item"]["durability"] != 0:
                                if slot["item"]["durability"] / slot["item"]["max_durability"] > 0.75:
                                    color = (0, 255, 0)
                                elif slot["item"]["durability"] / slot["item"]["max_durability"] > 0.5:
                                    color = (204, 218, 70)
                                elif slot["item"]["durability"] / slot["item"]["max_durability"] > 0.25:
                                    color = (255, 165, 0)
                                else:
                                    color = (255, 0, 0)
                                pygame.draw.rect(screen, color, (x + px, y + px*14,
                                                                 (tile_size - px*2) / slot["item"]["max_durability"] *
                                                                 slot["item"]["durability"], px))
            else:
                if slot["item"] is not None:
                    screen.blit(slot["item"]["image"], (x, SCREEN_HEIGHT - 26 * px))
                    if "durability" in slot["item"]:
                        if slot["item"]["durability"] != 0:
                            if slot["item"]["durability"] / slot["item"]["max_durability"] > 0.75:
                                color = (0, 255, 0)
                            elif slot["item"]["durability"] / slot["item"]["max_durability"] > 0.5:
                                color = (204, 218, 70)
                            elif slot["item"]["durability"] / slot["item"]["max_durability"] > 0.25:
                                color = (255, 165, 0)
                            else:
                                color = (255, 0, 0)
                            pygame.draw.rect(screen, color, (x + px, y + px*4,(tile_size - px*2) /
                                            slot["item"]["max_durability"] * slot["item"]["durability"], px))
            x += tile_size + px
        x = self.left + tile_size
        for j in range(len(self.inventory_slots)):
            slot = self.inventory_slots[j]
            if j >= 6:
                if j >= 6:
                    y = SCREEN_HEIGHT / 3 + px*5 + px*12
                if j >= 12:
                    y = SCREEN_HEIGHT / 3 + px*22 + px*12
                if j >= 18:
                    y = SCREEN_HEIGHT / 3 + px*39 + px*12
                if j >= 24:
                    y = SCREEN_HEIGHT / 3 + px*39 + px*17 + px*12
                if j == 6 or j == 12 or j == 18 or j == 24:
                    x = self.left + tile_size
            if slot != {"item": None, "value": 0}:
                if slot["value"] == 0:
                    slot["item"] = None
                elif slot["value"] != 1:
                    if j >= 6:
                        if game_state == inventory_state or market.state == 1 or market.state == 2:
                            draw_text(str(slot["value"]), inventory_text_font, white, x, y)
                    else:
                        y = SCREEN_HEIGHT - px*26 + px*12
                        draw_text(str(slot["value"]), inventory_text_font, white, x, y)
            x += tile_size + px
        if game_state == inventory_state or market.state == 1:
            self.show_information(self.inventory_slots[self.selected_slot]["item"], (
                self.slot_hitboxes[self.selected_slot].x, self.slot_hitboxes[self.selected_slot].y - px*19))

    def handle_inventory(self):
        if game_state == play_state:
            self.hand_item = self.inventory_slots[self.selected_slot]["item"]
            self.to_change_slot_1 = None
        elif game_state == inventory_state or market.state == 1:
            pos = pygame.mouse.get_pos()
            mouse_rect = pygame.Rect(pos[0], pos[1], 9, 9)
            for slot in self.slot_hitboxes:
                if slot.colliderect(mouse_rect):
                    self.selected_slot = self.slot_hitboxes.index(slot)
                    if player.left_clicked and not self.shift_clicked:
                        player.left_clicked = False
                        if market.state == 1:
                            if self.inventory_slots[self.selected_slot] != {"item": None, "value": 0}:
                                market.to_sell_item = self.inventory_slots[self.selected_slot].copy()
                                market.to_sell_item["price"] = (self.inventory_slots[self.selected_slot]["item"]["price"])
                                market.state = 2
                            else:
                                self.to_change_slot_1 = None
                        elif self.to_change_slot_1 is None:
                            self.to_change_slot_1 = self.selected_slot
                        else:
                            self.to_change_slot_2 = self.selected_slot
                            if   self.inventory_slots[self.to_change_slot_2] != {"item": None, "value": 0} and \
                                    self.inventory_slots[self.to_change_slot_1] != {"item": None, "value": 0}:
                                if self.inventory_slots[self.to_change_slot_2]["item"]["name"] == \
                                        self.inventory_slots[self.to_change_slot_1]["item"][
                                            "name"] and self.to_change_slot_1 != self.to_change_slot_2:
                                    if self.inventory_slots[self.to_change_slot_2]["value"] + \
                                            self.inventory_slots[self.to_change_slot_1]["value"] <= \
                                            self.inventory_slots[self.to_change_slot_1]["item"]["max_stack"]:
                                        self.inventory_slots[self.to_change_slot_2]["value"] += \
                                            self.inventory_slots[self.to_change_slot_1]["value"]
                                        self.inventory_slots[self.to_change_slot_1] = {"item": None, "value": 0}
                                        self.to_change_slot_1 = None
                                        self.to_change_slot_2 = None
                                    else:
                                        self.inventory_slots[self.to_change_slot_1]["value"] -= \
                                            self.inventory_slots[self.to_change_slot_1]["item"]["max_stack"] - \
                                            self.inventory_slots[self.to_change_slot_2]["value"]
                                        self.inventory_slots[self.to_change_slot_2]["value"] = \
                                            self.inventory_slots[self.to_change_slot_2]["item"]["max_stack"]

                                        self.to_change_slot_1 = None
                                        self.to_change_slot_2 = None
                                else:
                                    self.inventory_slots[self.to_change_slot_2], self.inventory_slots[
                                        self.to_change_slot_1] = self.inventory_slots[self.to_change_slot_1], \
                                        self.inventory_slots[self.to_change_slot_2]
                                    self.to_change_slot_1 = None
                                    self.to_change_slot_2 = None
                            else:
                                self.inventory_slots[self.to_change_slot_2], self.inventory_slots[
                                    self.to_change_slot_1] = self.inventory_slots[self.to_change_slot_1], \
                                    self.inventory_slots[self.to_change_slot_2]
                                self.to_change_slot_1 = None
                                self.to_change_slot_2 = None

                    elif self.shift_clicked and player.left_clicked:
                        if self.selected_slot > 5:
                            for i in range(6):
                                if self.inventory_slots[i] == {"item": None, "value": 0}:
                                    self.inventory_slots[self.selected_slot], self.inventory_slots[i] = self.inventory_slots[i], self.inventory_slots[self.selected_slot]
                                    break
                        else:
                            for i in range(len(self.inventory_slots)):
                                if len(self.inventory_slots)-1-i > self.selected_slot and len(self.inventory_slots)-1-i > 5:
                                    if self.inventory_slots[len(self.inventory_slots)-1-i] == {"item": None, "value": 0}:
                                        self.inventory_slots[self.selected_slot], self.inventory_slots[len(self.inventory_slots)-1-i] = \
                                        self.inventory_slots[len(self.inventory_slots)-1-i], self.inventory_slots[self.selected_slot]
                                        break


                    break




    def show_information(self, item, pos):
        if item is not None:
            name = item["name"].replace("_", " ")
            img = inventory_text_font.render(name, inventory_text_font, white).get_size()
            if "\n" in name:
                img = inventory_text_font.render(name, inventory_text_font, white).get_size()
                s = pygame.Surface((img[0]/2 + px*3, img[1]*2+ px*3))
            else:
                s = pygame.Surface((img[0]+ px*3, img[1]+ px*3))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            screen.blit(s, pos)
            draw_text(name, inventory_text_font, white, pos[0] + px*2, pos[1] + px*2)


class entity:

    def __init__(self):
        self.right_hitbox = None
        self.left_hitbox = None
        self.bottom_hitbox = None
        self.top_hitbox = None
        self.pos_x = 0
        self.pos_y = 0
        self.sprite = pygame.transform.scale(pygame.image.load('assets/entity/player/player_down_1.png'),
                                             (tile_size, tile_size))
        self.image = self.sprite
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True
        self.show_icon = False
        self.warning_icon = pygame.transform.scale(pygame.image.load("assets/GUI/icons/warning_icon.png"),
                                                   (px, px*5))
        self.icons = []

    def draw_entity(self):
        self.image = self.sprite
        screen.blit(self.image, (self.pos_x + cam.transform_x, self.pos_y + cam.transform_y))
        if dev_tools:
            pygame.draw.rect(screen, (255, 0, 0), self.top_hitbox)
            pygame.draw.rect(screen, (255, 0, 0), self.bottom_hitbox)
            pygame.draw.rect(screen, (255, 0, 0), self.left_hitbox)
            pygame.draw.rect(screen, (255, 0, 0), self.right_hitbox)
    def draw_icon(self):
        for i in self.icons:
            screen.blit(self.warning_icon, (i.pos_x + cam.transform_x + tile_size/2, i.pos_y + cam.transform_y - px*8))

class player(entity):
    def __init__(self):
        super().__init__()
        self.speed = 3
        self.sprinting = False
        self.time = 0
        self.down_1 = set_image('entity/player/player_down_1')
        self.down_2 = set_image('entity/player/player_down_2')
        self.down_3 = set_image('entity/player/player_down_3')
        self.down_4a = set_image('entity/player/player_down_4a')
        self.down_4b = set_image('entity/player/player_down_4b')
        self.up_4a = set_image('entity/player/player_up_4a')
        self.up_4b = set_image('entity/player/player_up_4b')
        self.up_1 = set_image('entity/player/player_up_1')
        self.up_2 = set_image('entity/player/player_up_2')
        self.up_3 = set_image('entity/player/player_up_3')
        self.left_1 = set_image('entity/player/player_left_1')
        self.left_2 = set_image('entity/player/player_left_2')
        self.left_3 = set_image('entity/player/player_left_3')
        self.left_4a = set_image('entity/player/player_left_4a')
        self.left_4b = set_image('entity/player/player_left_4b')
        self.right_1 = set_image('entity/player/player_right_1')
        self.right_2 = set_image('entity/player/player_right_2')
        self.right_3 = set_image('entity/player/player_right_3')
        self.right_4a = set_image('entity/player/player_right_4a')
        self.right_4b = set_image('entity/player/player_right_4b')
        self.sprite = self.down_1
        self.second_sprite = None
        self.direction = 'down'
        self.image = self.sprite
        self.pos_x = SCREEN_WIDTH / 2 - tile_size / 2
        self.pos_y = SCREEN_HEIGHT / 2 - tile_size / 2
        self.break_time = 0
        self.clicked = False
        self.time = 0
        self.top_hitbox = pygame.Rect(self.pos_x, self.pos_y, tile_size, px)
        self.bottom_hitbox = pygame.Rect(self.pos_x, self.pos_y + tile_size, tile_size, px)
        self.left_hitbox = pygame.Rect(self.pos_x, self.pos_y, px, tile_size)
        self.right_hitbox = pygame.Rect(self.pos_x + tile_size, self.pos_y, px, tile_size)
        self.main_hitbox = pygame.Rect(self.pos_x, self.pos_y, tile_size, tile_size)
        self.show_icon = False
        self.right_clicked = False
        self.left_clicked = False
        self.can_place_block = False
        self.currency = 500
        self.coin_img = pygame.transform.scale(pygame.image.load('assets/GUI/icons/coin.png'),
                                               (tile_size, tile_size))
        self.attack_time = 0
        self.attack_rect = pygame.Rect(0,0,0,0)

    def update_hitbox(self):
        self.top_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px*2, self.pos_y + cam.transform_y + px,
                                      tile_size - px*4, px)
        self.bottom_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px*2, self.pos_y + cam.transform_y + tile_size - px*2,
                                         tile_size - px*4, px)
        self.left_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px, self.pos_y + cam.transform_y + px*2, px,
                                       tile_size - px*4)
        self.right_hitbox = pygame.Rect(self.pos_x + cam.transform_x + tile_size - px*2, self.pos_y + cam.transform_y + px*2,
                                        px, tile_size - px*4)
        self.main_hitbox = pygame.Rect(self.pos_x + cam.transform_x, self.pos_y + cam.transform_y, tile_size, tile_size)

    def move_player(self):
        # Move
        self.update_hitbox()
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True
        moving = False
        if self.sprinting:
            self.speed = px*2
        else:
            self.speed = px

        if down_pressed and self.attack_time == 0:
            self.direction = 'down'
            for i in range(int(player.speed / 3)):
                self.update_hitbox()

                col_checker.check_entity_collision()
                if self.can_move_down:
                    col_checker.check_block_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_tile_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_trader_col(self.bottom_hitbox, self)
                if self.can_move_down:
                    if tiles.bottom_border != cam.bottom_y and player.pos_y + cam.transform_y == SCREEN_HEIGHT / 2 - tile_size / 2:
                        cam.transform_y -= px
                        cam.bottom_y += px
                        cam.top_y += px
                        blocks.update_blocks()
                    if tiles.bottom_border - tile_size != self.pos_y:
                        self.pos_y += px
                else:
                    break
            moving = True
        elif up_pressed and self.attack_time == 0:
            self.direction = 'up'
            for i in range(int(player.speed / px)):
                self.update_hitbox()
                col_checker.check_tile_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_entity_collision()
                if self.can_move_up:
                    col_checker.check_block_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_trader_col(self.top_hitbox, self)
                if self.can_move_up:
                    if tiles.top_border != cam.top_y and player.pos_y + cam.transform_y == SCREEN_HEIGHT / 2 - tile_size / 2:
                        cam.transform_y += px
                        cam.top_y -= px
                        cam.bottom_y -= px
                        blocks.update_blocks()
                    if tiles.top_border != self.pos_y:
                        self.pos_y -= px
                else:
                    break
            moving = True
        elif left_pressed and self.attack_time == 0:
            self.direction = 'left'
            for i in range(int(player.speed / px)):
                self.update_hitbox()
                col_checker.check_tile_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_entity_collision()
                if self.can_move_left:
                    col_checker.check_block_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_trader_col(self.left_hitbox, self)
                if self.can_move_left:
                    if tiles.left_border != cam.left_x and player.pos_x + cam.transform_x == SCREEN_WIDTH / 2 - tile_size / 2:
                        cam.transform_x += px
                        cam.left_x -= px
                        cam.right_x -= px
                        blocks.update_blocks()
                    if tiles.left_border != self.pos_x:
                        self.pos_x -= px
                else:
                    break
            moving = True
        elif right_pressed and self.attack_time == 0:
            self.direction = 'right'
            for i in range(int(player.speed / px)):
                self.update_hitbox()
                col_checker.check_tile_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_entity_collision()
                if self.can_move_right:
                    col_checker.check_block_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_trader_col(self.right_hitbox, self)
                if self.can_move_right:
                    if tiles.right_border != cam.right_x and player.pos_x + cam.transform_x == SCREEN_WIDTH / 2 - tile_size / 2:
                        cam.transform_x -= px
                        cam.right_x += px
                        cam.left_x += px
                        blocks.update_blocks()
                        tiles.set_solid_tiles(num_map)
                    if tiles.right_border - tile_size != self.pos_x:
                        self.pos_x += px
                else:
                    break
            moving = True
        # Animation
        if self.sprite == self.down_4a:
            if self.attack_time == 24:
                self.sprite = self.down_3
                self.second_sprite = None
                self.attack_time = 0
            else:
                self.attack_time += 1
        elif self.sprite == self.up_4a:
            if self.attack_time == 24:
                self.sprite = self.up_3
                self.second_sprite = None
                self.attack_time = 0
            else:
                self.attack_time += 1
        elif self.sprite == self.right_4a:
            if self.attack_time == 24:
                self.sprite = self.right_3
                self.second_sprite = None
                self.attack_time = 0
            else:
                self.attack_time += 1
        elif self.sprite == self.left_4a:
            if self.attack_time == 24:
                self.sprite = self.left_3
                self.second_sprite = None
                self.attack_time = 0
            else:
                self.attack_time += 1
        elif moving:
            if self.direction == "down":
                if self.time == 0:
                    self.sprite = self.down_3
                    self.time += int(self.speed / px)
                elif self.time == 16:
                    self.sprite = self.down_1
                    self.time += int(self.speed / px)
                elif self.time == 32:
                    self.sprite = self.down_3
                    self.time += int(self.speed / px)
                elif self.time == 48:
                    self.sprite = self.down_2
                    self.time += int(self.speed / px)
                elif self.time >= 64:
                    self.time = 0
                else:
                    self.time += int(self.speed / px)
            elif self.direction == "up":
                if self.time == 0:
                    self.sprite = self.up_3
                    self.time += int(self.speed / px)
                elif self.time == 16:
                    self.sprite = self.up_1
                    self.time += int(self.speed / px)
                elif self.time == 32:
                    self.sprite = self.up_3
                    self.time += int(self.speed / px)
                elif self.time == 48:
                    self.sprite = self.up_2
                    self.time += int(self.speed / px)
                elif self.time >= 64:
                    self.time = 0
                else:
                    self.time += int(self.speed / px)
            elif self.direction == "left":
                if self.time == 0:
                    self.sprite = self.left_3
                    self.time += int(self.speed / px)
                elif self.time == 16:
                    self.sprite = self.left_1
                    self.time += int(self.speed / px)
                elif self.time == 32:
                    self.sprite = self.left_3
                    self.time += int(self.speed / px)
                elif self.time == 48:
                    self.sprite = self.left_2
                    self.time += int(self.speed / px)
                elif self.time >= 64:
                    self.time = 0
                else:
                    self.time += int(self.speed / px)
            elif self.direction == "right":
                if self.time == 0:
                    self.sprite = self.right_3
                    self.time += int(self.speed / px)
                elif self.time == 16:
                    self.sprite = self.right_1
                    self.time += int(self.speed / px)
                elif self.time == 32:
                    self.sprite = self.right_3
                    self.time += int(self.speed / px)
                elif self.time == 48:
                    self.sprite = self.right_2
                    self.time += int(self.speed / px)
                elif self.time >= 64:
                    self.time = 0
                else:
                    self.time += int(self.speed / px)
        else:
            if self.direction == "down":
                self.sprite = self.down_3
                self.time = 8
            elif self.direction == "up":
                self.sprite = self.up_3
                self.time = 8
            elif self.direction == "left":
                self.sprite = self.left_3
                self.time = 8
            elif self.direction == "right":
                self.sprite = self.right_3
                self.time = 8

    def place_block(self):
        if inventory.hand_item is not None:
            if inventory.hand_item["placeable"]:

                pos = pygame.mouse.get_pos()
                x = pos[0] - cam.transform_x
                while x % tile_size != 0:
                    x -= 1
                y = pos[1] - cam.transform_y
                while y % tile_size != 0:
                    y -= 1

                x_size = inventory.hand_item["block_state"]["def_hit_box"][2]
                y_size = inventory.hand_item["block_state"]["def_hit_box"][3]
                temporary_rect = pygame.Rect(x + cam.transform_x + inventory.hand_item["block_state"]["def_hit_box"][0],
                                             y + cam.transform_y + inventory.hand_item["block_state"]["def_hit_box"][1],
                                             x_size, y_size)

                col_checker.check_place_block_col(temporary_rect)

                if (x > self.pos_x + tile_size * 3 or y > self.pos_y + tile_size * 3 or x < self.pos_x - tile_size * 3 or
                        y < self.pos_y - tile_size * 3):
                    self.can_place_block = False
                if self.can_place_block:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                if "fence" in inventory.hand_item["block_state"]:
                    self.show_preview(color, temporary_rect, inventory.hand_item["block_state"]["image"],
                                      (x + cam.transform_x, y + cam.transform_y), inventory.hand_item["block_state"])
                else:
                    self.show_preview(color, temporary_rect, inventory.hand_item["block_state"]["image"],
                                    (x + cam.transform_x, y + cam.transform_y))
                if self.right_clicked and self.can_place_block:
                    blocks.pos_x = x
                    blocks.pos_y = y
                    blocks.set_block(inventory.hand_item["block_state"], (x, y))
                    sounds.play_sound(sounds.place_sfx)
                    inventory.inventory_slots[inventory.selected_slot]["value"] -= 1
                    self.right_clicked = False
            elif "entity" in inventory.hand_item:
                pos = pygame.mouse.get_pos()
                x = pos[0] - cam.transform_x
                while x % tile_size != 0:
                    x -= 1
                y = pos[1] - cam.transform_y
                while y % tile_size != 0:
                    y -= 1
                temporary_rect = pygame.Rect(x + cam.transform_x + px*2, y + cam.transform_y + px*2, tile_size - px*2,
                                             tile_size - px*2)
                col_checker.check_place_block_col(temporary_rect)

                if x > self.pos_x + tile_size * 3 or y > self.pos_y + tile_size * 3 or x < self.pos_x - tile_size * 3 or y < self.pos_y - tile_size * 3:
                    self.can_place_block = False
                if self.can_place_block:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)
                self.show_preview(color, temporary_rect, inventory.hand_item["image"],
                                  (x + cam.transform_x, y + cam.transform_y))
                if self.right_clicked and self.can_place_block:
                    entities.append(inventory.hand_item["entity"](x - tiles.start_x, y - tiles.start_y))
                    inventory.inventory_slots[inventory.selected_slot]["value"] -= 1
                    self.right_clicked = False

    def show_preview(self, color, rect, img, pos, fence=None):
        if rect[2] > tile_size:
            s = pygame.Surface((img.get_size()[0], img.get_size()[1]))
        else:
            s = pygame.Surface((tile_size, tile_size))
        s.set_alpha(120)
        s.fill(color)
        screen.blit(s, pos)

        if fence is not None:

            hitbox_top = pygame.Rect(pos[0], pos[1] - tile_size/2,
                                     tile_size, tile_size/2)
            hitbox_right = pygame.Rect(pos[0] + tile_size, pos[1] + px*8,
                                       tile_size, tile_size - px*8)
            hitbox_bottom = pygame.Rect(pos[0], pos[1] + tile_size,
                                        tile_size, tile_size)
            hitbox_left = pygame.Rect(pos[0] - tile_size, pos[1] + px*8,
                                      tile_size, tile_size - px*8)

            code = [0, 0, 0, 0]

            for i in blocks.all_fences:
                if i != fence:
                    if hitbox_top.colliderect(i["hitbox"]):
                        code[0] = 1
                    elif hitbox_right.colliderect(i["hitbox"]):
                        code[1] = 1
                    elif hitbox_bottom.colliderect(i["hitbox"]):
                        code[2] = 1
                    elif hitbox_left.colliderect(i["hitbox"]):
                        code[3] = 1

            if fence["name"] != "gate":
                index = code[0] + code[1]*2 + code[2]*4 + code[3]*8
                temporary_img = blocks.fences[index]["image"].__copy__()
            else:
                if code == [0, 1, 0, 1] or code == [0, 1, 0, 0] or code == [0, 0, 0, 1]:
                    temporary_img = blocks.gate["image"].__copy__()
                elif code == [1, 0, 1, 0] or code == [1, 0, 0, 0] or code == [0, 0, 1, 0]:
                    temporary_img = blocks.gate_1["image"].__copy__()
                else:
                    temporary_img = fence["image"].__copy__()
        else:
            temporary_img = img.__copy__()
        temporary_img.set_alpha(120)
        screen.blit(temporary_img, pos)

    def drop_item(self, item):
        rnd_x = random.randint(-px*10, px*10)
        rnd_y = random.randint(0, tile_size)
        if self.direction == "down":
            items.set_item(item, self.pos_x + rnd_x, self.pos_y + tile_size + rnd_y)
        elif self.direction == "up":
            items.set_item(item, self.pos_x + rnd_x, self.pos_y - tile_size - rnd_y)
        elif self.direction == "left":
            items.set_item(item, self.pos_x - rnd_y - tile_size, self.pos_y + rnd_x)
        else:
            items.set_item(item, self.pos_x + rnd_y + tile_size, self.pos_y + rnd_x)

    def break_block(self):

        if self.left_clicked:
            if self.break_time == 0:
                if inventory.hand_item is not None:
                    if "durability" in inventory.hand_item:
                        pos = pygame.mouse.get_pos()
                        mouse_rect = pygame.Rect(pos[0], pos[1], 6, 6)
                        bottom_rect = pygame.Rect(self.pos_x + cam.transform_x + px*4,
                                                  self.pos_y + tile_size + cam.transform_y - px*4, tile_size/2,
                                                  tile_size)
                        top_rect = pygame.Rect(self.pos_x + cam.transform_x + px*4,
                                               self.pos_y - tile_size  + px*4 + cam.transform_y,
                                               tile_size/2, tile_size)
                        left_rect = pygame.Rect(self.pos_x - tile_size + cam.transform_x + px*4,
                                                self.pos_y + cam.transform_y + px*4,
                                                tile_size, tile_size/2)
                        right_rect = pygame.Rect(self.pos_x + tile_size + cam.transform_x - px*4,
                                                 self.pos_y + cam.transform_y + px*4, tile_size, tile_size/2)

                        bottom_mouse_rect = pygame.Rect(self.pos_x + cam.transform_x,
                                                  self.pos_y + tile_size + cam.transform_y, tile_size,
                                                  tile_size * 2)
                        top_mouse_rect = pygame.Rect(self.pos_x + cam.transform_x,
                                               self.pos_y - tile_size*2 + cam.transform_y,
                                               tile_size, tile_size * 2)
                        left_mouse_rect = pygame.Rect(self.pos_x - tile_size*2 + cam.transform_x ,
                                                self.pos_y + cam.transform_y,
                                                tile_size * 2, tile_size)
                        right_mouse_rect = pygame.Rect(self.pos_x + tile_size + cam.transform_x,
                                                 self.pos_y + cam.transform_y, tile_size * 2, tile_size)
                        if mouse_rect.colliderect(bottom_mouse_rect):
                            self.direction = "down"
                            self.attack_rect = bottom_rect
                            self.sprite = self.down_4a
                            self.second_sprite = self.down_4b
                        elif mouse_rect.colliderect(top_mouse_rect):
                            self.direction = "up"
                            self.attack_rect = top_rect
                            self.sprite = self.up_4a
                            self.second_sprite = self.up_4b
                        elif mouse_rect.colliderect(left_mouse_rect):
                            self.direction = "left"
                            self.attack_rect = left_rect
                            self.sprite = self.left_4a
                            self.second_sprite = self.left_4b
                        elif mouse_rect.colliderect(right_mouse_rect):
                            self.direction = "right"
                            self.attack_rect = right_rect
                            self.sprite = self.right_4a
                            self.second_sprite = self.right_4b
                        else:
                            self.left_clicked = False
                            return
                        col_checker.check_block_hit(self.attack_rect)
                        self.left_clicked = False
                self.clicked = True
        if self.clicked:
            self.break_time += 1
        if self.break_time == 24:
            col_checker.check_block_break(self.attack_rect)
            self.break_time = 0
            self.clicked = False

    def draw_second_sprite(self):
        if self.second_sprite is not None:
            if self.sprite == self.down_4a:
                screen.blit(self.second_sprite,
                            (self.pos_x + cam.transform_x, self.pos_y + cam.transform_y + tile_size))
            elif self.sprite == self.up_4a:
                screen.blit(self.second_sprite,
                            (self.pos_x + cam.transform_x, self.pos_y + cam.transform_y - tile_size))
            elif self.sprite == self.left_4a:
                screen.blit(self.second_sprite,
                            (self.pos_x + cam.transform_x - tile_size, self.pos_y + cam.transform_y))
            elif self.sprite == self.right_4a:
                screen.blit(self.second_sprite,
                            (self.pos_x + cam.transform_x + tile_size, self.pos_y + cam.transform_y))

    def draw_coins(self):
        screen.blit(self.coin_img, (tile_size * 15, tile_size / 2 - px*2))
        img = text_font.render(str(self.currency), True, white)
        draw_text(str(self.currency), text_font, white, tile_size * 15 - img.get_size()[0] - px *2, tile_size / 2)


class cow(entity):
    def __init__(self, x, y):
        super().__init__()
        self.time = 0
        self.wait = 0
        self.pos_x = x + tiles.start_x
        self.pos_y = y + tiles.start_y
        self.down_1 = set_image('entity/cow/cow_down_1')
        self.down_2 = set_image('entity/cow/cow_down_2')
        self.down_3 = set_image('entity/cow/cow_down_3')
        self.up_1 = set_image('entity/cow/cow_up_1')
        self.up_2 = set_image('entity/cow/cow_up_2')
        self.up_3 = set_image('entity/cow/cow_up_3')
        self.left_1 = set_image('entity/cow/cow_left_1')
        self.left_2 = set_image('entity/cow/cow_left_2')
        self.left_3 = set_image('entity/cow/cow_left_3')
        self.right_1 = set_image('entity/cow/cow_right_1')
        self.right_2 = set_image('entity/cow/cow_right_2')
        self.right_3 = set_image('entity/cow/cow_right_3')
        self.warning_icon = set_image('GUI/icons/warning_icon')
        self.sprite = self.down_1
        self.direction = 'down'
        self.image = self.sprite
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True
        self.rand_num = random.randint(1, 100)
        self.top_hitbox = pygame.Rect(self.pos_x, self.pos_y, tile_size, 1)
        self.bottom_hitbox = pygame.Rect(self.pos_x, self.pos_y + tile_size, tile_size, 1)
        self.left_hitbox = pygame.Rect(self.pos_x, self.pos_y, 1, tile_size)
        self.right_hitbox = pygame.Rect(self.pos_x + tile_size, self.pos_y, 1, tile_size)
        self.main_hitbox = pygame.Rect(self.pos_x, self.pos_y, tile_size, tile_size)
        self.speed = px/3
        self.max_cool_down = 6000
        self.cool_down = random.randint(1, self.max_cool_down)
        self.show_icon = False
        self.walking_num = 0
        self.sound_num = random.randint(1, 15000)


    def update_hitbox(self):
        self.top_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px*2, self.pos_y + cam.transform_y + px,
                                      tile_size - px*4, px)
        self.bottom_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px*2, self.pos_y + cam.transform_y + tile_size - px*2,
                                         tile_size - px*4, px)
        self.left_hitbox = pygame.Rect(self.pos_x + cam.transform_x + px, self.pos_y + cam.transform_y + px*2, 3,
                                       tile_size - px*4)
        self.right_hitbox = pygame.Rect(self.pos_x + cam.transform_x + tile_size - px*2, self.pos_y + cam.transform_y + px*2,
                                        px, tile_size - px*4)
        self.main_hitbox = pygame.Rect(self.pos_x + cam.transform_x, self.pos_y + cam.transform_y, tile_size, tile_size)

    def move(self):
        # mooing
        if self.main_hitbox.colliderect(screen_rect):
            if self.sound_num >= 15000:
                sounds.play_sound(random.choice([sounds.moo_sfx, sounds.moo_sfx_2]))
                self.sound_num = 0
            else:
                self.sound_num += random.randint(1, 12)


        # Move
        self.update_hitbox()
        if self.cool_down == 1:
            self.show_icon = True
            self.max_cool_down = 6000
        else:
            self.cool_down = random.randint(1, self.max_cool_down)
        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True
        moving = False
        stop = False
        if self.wait >= 60:
            if self.wait == 140:
                self.rand_num = random.randint(1, 100)
                stop = False
                self.wait = 0
            else:
                moving = False
                stop = True
                self.wait = random.randint(60, 140)
        else:
            self.wait = random.randint(1, 60)
        if not stop:
            if self.rand_num <= 25:
                self.direction = 'down'
                col_checker.check_tile_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_player_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_entities_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_block_collision(self.bottom_hitbox, self)
                if self.can_move_down:
                    col_checker.check_trader_col(self.bottom_hitbox, self)
                if self.can_move_down:
                    if tiles.bottom_border - tile_size != self.pos_y:
                        self.pos_y += self.speed
                moving = True
            elif self.rand_num <= 50:
                self.direction = 'up'
                col_checker.check_tile_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_player_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_entities_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_block_collision(self.top_hitbox, self)
                if self.can_move_up:
                    col_checker.check_trader_col(self.top_hitbox, self)
                if self.can_move_up:
                    if tiles.top_border != self.pos_y:
                        self.pos_y -= self.speed
                moving = True
            elif self.rand_num <= 75:
                self.direction = 'left'
                col_checker.check_tile_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_player_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_entities_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_block_collision(self.left_hitbox, self)
                if self.can_move_left:
                    col_checker.check_trader_col(self.left_hitbox, self)
                if self.can_move_left:
                    if tiles.left_border != self.pos_x:
                        self.pos_x -= self.speed
                moving = True
            elif self.rand_num <= 100:
                self.direction = 'right'
                col_checker.check_tile_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_player_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_entities_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_block_collision(self.right_hitbox, self)
                if self.can_move_right:
                    col_checker.check_trader_col(self.right_hitbox, self)
                if self.can_move_right:
                    if tiles.right_border - tile_size != self.pos_x:
                        self.pos_x += self.speed
                moving = True
        elif self.direction == 'down':
            self.sprite = self.down_3
            self.time = 20
        elif self.direction == 'up':
            self.sprite = self.up_3
            self.time = 20
        elif self.direction == 'left':
            self.sprite = self.left_3
            self.time = 20
        elif self.direction == 'right':
            self.sprite = self.right_3
            self.time = 20
        # Animation
        if moving:
            if self.time == 20:
                self.time = 0
                if self.direction == 'down':
                    if self.sprite == self.down_1 or self.sprite == self.down_2:
                        self.sprite = self.down_3
                    elif self.walking_num == 0:
                        self.sprite = self.down_1
                        self.walking_num = 1
                    else:
                        self.sprite = self.down_2
                        self.walking_num = 0
                elif self.direction == 'up':
                    if self.sprite == self.up_1 or self.sprite == self.up_2:
                        self.sprite = self.up_3
                    elif self.walking_num == 0:
                        self.sprite = self.up_1
                        self.walking_num = 1
                    else:
                        self.sprite = self.up_2
                        self.walking_num = 0

                elif self.direction == 'left':
                    if self.sprite == self.left_1 or self.sprite == self.left_2:
                        self.sprite = self.left_3
                    elif self.walking_num == 0:
                        self.sprite = self.left_1
                        self.walking_num = 1
                    else:
                        self.sprite = self.left_2
                        self.walking_num = 0
                elif self.direction == 'right':
                    if self.sprite == self.right_1 or self.sprite == self.right_2:
                        self.sprite = self.right_3
                    elif self.walking_num == 0:
                        self.sprite = self.right_1
                        self.walking_num = 1
                    else:
                        self.sprite = self.right_2
                        self.walking_num = 0
            else:
                self.time += 1

    def drop_item(self):
        if self.show_icon:
            random_x = random.randint(-1 * tile_size, tile_size)
            random_y = random.randint(-1 * tile_size, tile_size)
            items.set_item(items.milk, self.pos_x + random_x, self.pos_y + random_y)

            self.cool_down = 0
            self.show_icon = False


class trader(entity):
    def __init__(self, x, y, trades):
        super().__init__()
        self.time = 0
        self.wait = 0
        self.pos_x = x + tiles.start_x
        self.pos_y = y + tiles.start_y
        self.down_1 = pygame.transform.scale(pygame.image.load('assets/entity/npcs/trader.png'),
                                             (tile_size, tile_size))
        self.trades = trades
        self.sprite = self.down_1
        self.direction = 'down'
        self.image = self.sprite
        self.rand_num = random.randint(1, 100)
        self.top_hitbox = pygame.Rect(self.pos_x, self.pos_y, tile_size, 1)
        self.bottom_hitbox = pygame.Rect(self.pos_x, self.pos_y + tile_size, tile_size, 1)
        self.left_hitbox = pygame.Rect(self.pos_x, self.pos_y, 1, tile_size)
        self.right_hitbox = pygame.Rect(self.pos_x + tile_size, self.pos_y, 1, tile_size)
        self.main_hitbox = pygame.Rect(self.pos_x, self.pos_y - px*2, tile_size, tile_size + px*2)
        self.show_icon = False

    def update_hitbox(self):
        self.main_hitbox = pygame.Rect(self.pos_x + cam.transform_x, self.pos_y + cam.transform_y - px*2, tile_size,
                                       tile_size + px*2)

class save_load:
    def __init__(self):
        self.load_slot = None
        self.load_offer = None
        self.current_world = None
        self.full_screen = False
        self.save_time = 0

    def save(self, file):
        # INVENTORY
        saved_inventory = []
        for slot in inventory.inventory_slots:
            if slot["item"] is not None:
                if "durability" in slot["item"]:
                    save_slot = {"item": slot["item"]["name"], "value": slot["value"],
                                 "durability": slot["item"]["durability"]}
                else:
                    save_slot = {"item": slot["item"]["name"], "value": slot["value"]}
            else:
                save_slot = slot
            saved_inventory.append(save_slot)

        # MARKET
        saved_market = []
        for i in market.offers:
            if "durability" in i[0]:
                offer = {"item":i[0]["name"], "amount": i[1], "price": i[2], "durability": i[0]["durability"]}
            else:
                offer = {"item":i[0]["name"], "amount": i[1], "price": i[2]}
            saved_market.append(offer)
        # ENTITIES
        global entities
        saved_entities = []
        for i in entities:
            saved_entity = {"x": i.pos_x - tiles.start_x, "y": i.pos_y - tiles.start_y}
            saved_entities.append(saved_entity)
        # BLOCKS
        saved_blocks = []
        for i in blocks.all_blocks:
            saved_block = {"name": i["name"], "x": i["x"] / px, "y": i["y"] / px}
            saved_blocks.append(saved_block)
        # DECORS
        saved_decors = []
        for i in decor.decors:
            if i[0] == decor.red_flower:
                saved_decors.append(("red_flower", i[1]))
            elif i[0] == decor.red_tulip:
                saved_decors.append(("red_tulip", i[1]))
            elif i[0] == decor.red_flower_2:
                saved_decors.append(("red_flower_2", i[1]))
            elif i[0] == decor.yellow_flower:
                saved_decors.append(("yellow_flower", i[1]))
            elif i[0] == decor.yellow_tulip:
                saved_decors.append(("yellow_tulip", i[1]))
            elif i[0] == decor.yellow_flower_2:
                saved_decors.append(("yellow_flower_2", i[1]))
            elif i[0] == decor.mushroom:
                saved_decors.append(("mushroom", i[1]))
            elif i[0] == decor.small_stone:
                saved_decors.append(("small_stone", i[1]))
            elif i[0] == decor.big_stone:
                saved_decors.append(("big_stone", i[1]))

 
        data = {"player_pos_x": player.pos_x/px, "player_pos_y": player.pos_y/px,
                 "player_currency": player.currency, "cam_transform_x": cam.transform_x/px,
                "cam_transform_y": cam.transform_y/px, "cam_top_y": cam.top_y/px, "cam_bottom_y": cam.bottom_y/px,
                "cam_left_x": cam.left_x/px,"cam_right_x": cam.right_x/px,"inventory": saved_inventory,
                "entities": saved_entities, "blocks": saved_blocks,
                "decors": saved_decors, "market": saved_market}

        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode("utf-8"))
        with open('assets/saves/' + file, 'wb') as f:

            f.write(encoded)

    def load(self, file):
        self.current_world = file

        with open('assets/saves/'+ file, 'rb') as file:
            encoded = file.read()
            json_str = base64.b64decode(encoded).decode("utf-8")
            data = json.loads(json_str)

        inventory.inventory_slots = []

        for slot in data["inventory"]:
            if slot["item"] is not None:
                for i in items.items:
                    if i["name"] == slot["item"]:
                        self.load_slot = {"item": i.copy(), "value": slot["value"]}
                        break
            else:
                self.load_slot = slot
            if "durability" in slot:
                self.load_slot["item"]["durability"] = slot["durability"]
            inventory.inventory_slots.append(self.load_slot)
        # MARKET

        market.offers = []
        for offer in data["market"]:  #
            for i in items.items:
                if i["name"] == offer["item"]:
                    loaded_offer = (i.copy(), offer["amount"], offer["price"])
                    break
            if len(offer) > 3:
                loaded_offer[0]["durability"] = offer["durability"]
            market.offers.append(loaded_offer)

        player.pos_x = data["player_pos_x"]*px
        player.pos_y = data["player_pos_y"]*px
        player.currency = data["player_currency"]
        cam.transform_x = data["cam_transform_x"]*px
        cam.transform_y = data["cam_transform_y"]*px
        cam.top_y = data["cam_top_y"]*px
        cam.bottom_y = data["cam_bottom_y"]*px
        cam.left_x = data["cam_left_x"]*px
        cam.right_x = data["cam_right_x"]*px

        # ENTITIES
        global  entities
        entities = []
        for i in data["entities"]:
            entities.append(cow(i["x"], i["y"]))

        # BLOCKS
        blocks.all_fences = []
        blocks.all_blocks = []
        for i in data["blocks"]:
            for j in blocks.blocks:
                if i["name"] == j["name"]:
                    blocks.set_block(j,(i["x"]*px, i["y"]*px))
                    break
        # DECORS
        decor.decors = []
        for i in data["decors"]:
            if i[0] == "red_flower":
                decor.decors.append((decor.red_flower, i[1]))
            elif i[0] == "red_flower_2":
                decor.decors.append((decor.red_flower_2, i[1]))
            elif i[0] == "red_tulip":
                decor.decors.append((decor.red_tulip, i[1]))
            elif i[0] == "yellow_flower":
                decor.decors.append((decor.yellow_flower, i[1]))
            elif i[0] == "yellow_flower_2":
                decor.decors.append((decor.yellow_flower_2, i[1]))
            elif i[0] == "yellow_tulip":
                decor.decors.append((decor.yellow_tulip, i[1]))
            elif i[0] == "mushroom":
                decor.decors.append((decor.mushroom, i[1]))
            elif i[0] == "small_stone":
                decor.decors.append((decor.small_stone, i[1]))
            elif i[0] == "big_stone":
                decor.decors.append((decor.big_stone, i[1]))

    def save_settings(self):
        data = {"full_screen": self.full_screen, "dev_tools": allow_dev_tools, "sound_volume": sounds.sound_effect_volume,
                "music_volume": sounds.music_volume}
        with open('assets/settings.json', 'w') as file:
            json.dump(data, file)
    def load_settings(self):
        with open('assets/settings.json', 'r') as file:
            data = json.load(file)

        self.full_screen = data["full_screen"]
        if self.full_screen:
            global screen
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        global allow_dev_tools
        allow_dev_tools = data["dev_tools"]
        sounds.sound_effect_volume = data["sound_volume"]
        sounds.music_volume = data["music_volume"]


class start_menu:
    def __init__(self):


        self.left = SCREEN_WIDTH / 2 - px * 111 / 2
        self.pressed = [False, None]
        self.file_names = []
        self.ask_base = set_image("GUI/bases/ask_base")
        self.trash = set_image("GUI/buttons/trash")
        self.selected_trash = set_image("GUI/buttons/selected_trash")
        self.pressed_trash = set_image("GUI/buttons/pressed_trash")
        self.lever_on = set_image("GUI/buttons/on")
        self.lever_off = set_image("GUI/buttons/off")
        self.back_screen = set_image("GUI/bases/back_screen")
        self.top_button_img = set_image("GUI/buttons/big_button")
        self.middle_button_img = set_image("GUI/buttons/big_button")
        self.bottom_button_img = set_image("GUI/buttons/big_button")
        self.quit_button_img = set_image("GUI/buttons/big_button")
        self.big_button_img = set_image("GUI/buttons/big_button")
        self.frame_img = set_image("GUI/buttons/button")
        self.selected_big_button_img = set_image("GUI/buttons/selected_big_button")
        self.pressed_big_button_img = set_image("GUI/buttons/pressed_big_button")
        self.small_button_img = set_image("GUI/buttons/small_button")
        self.pressed_button_img = set_image("GUI/buttons/button_pressed")
        self.selected_button_img = set_image("GUI/buttons/button_selected")

        self.no_button = self.small_button_img
        self.yes_button = self.small_button_img
        self.top_button = pygame.Rect(tile_size*3.5, tile_size*4 -px, tile_size*9, tile_size*0.75 + px)
        self.middle_button = pygame.Rect(tile_size * 3.5, tile_size * 5.2 -px, tile_size * 9, tile_size * 0.75+ px)
        self.middle_buttons = []
        self.trash_buttons = []
        self.bottom_button = pygame.Rect(tile_size * 5.2, tile_size * 6.4 -px, tile_size * 9, tile_size * 0.75+ px)
        self.quit_button = pygame.Rect(tile_size * 5.2, tile_size * 7.6 - px, tile_size * 9, tile_size * 0.75 + px)
        self.state = 0
        self.world_name = ""
        self.time = 0
        self.press_time = 0
        self.delete_world = ""
        self.current_middle_button = None
        self.current_trash_button = None
        self.pressed_trash_button = None
    def draw(self):
        if self.state != 4:
            screen.blit(self.back_screen, (0, 0))
        if self.state == 0:

            screen.blit(self.top_button_img, (tile_size*3.5 - px*2, tile_size*4- px*2))
            screen.blit(self.middle_button_img, (tile_size * 3.5 - px*2, tile_size * 5.2 - px*2))
            screen.blit(self.bottom_button_img, (tile_size * 3.5 - px*2, tile_size * 6.4 - px*2))
            screen.blit(self.quit_button_img, (tile_size * 3.5 - px * 2, tile_size * 7.6 - px * 2))
            draw_text("Cheese Factory", title_font, (0, 0, 0), px*3, tile_size/2 + px*2, True)
            draw_text("Cheese Factory", title_font, white, px*3, tile_size / 2, True)
            draw_text("Single player", mid_title_font, white, tile_size*2, tile_size*4 + px, True)
            draw_text("Multi player", mid_title_font, white, tile_size * 2, tile_size * 5.2 + px, True)
            draw_text("Settings", mid_title_font, white, tile_size * 2, tile_size * 6.4 + px, True)
            draw_text("Quit", mid_title_font, white, tile_size * 2, tile_size * 7.6 + px, True)
        elif self.state == 1:
            screen.blit(self.top_button_img, (tile_size * 3.5 - px*2, tile_size * 4 - px*2))
            draw_text("Single player", title_font, (0, 0, 0), px*3, tile_size / 2 + px*2, True)
            draw_text("Single player", title_font, white, px*3, tile_size / 2, True)
            draw_text("New world", mid_title_font, white, tile_size * 2, tile_size * 4 + px, True)

            self.file_names = os.listdir("assets/saves")
            y = tile_size * 5.2
            for i in self.file_names:
                if self.current_middle_button == self.file_names.index(i):
                    screen.blit(self.selected_big_button_img, (tile_size * 3.5 - px*2, y - px*2))
                    self.current_middle_button = None
                else:
                    screen.blit(self.middle_button_img, (tile_size * 3.5 - px*2, y - px*2))
                if self.current_trash_button == self.file_names.index(i):
                    screen.blit(self.selected_trash, (tile_size * 12 + px*12, y - px*2))
                    self.current_trash_button = None
                    if self.pressed_trash_button == self.file_names.index(i):
                        screen.blit(self.pressed_trash, (tile_size * 12 + px*12, y - px*2))
                        self.pressed_trash_button = None
                else:
                    screen.blit(self.trash, (tile_size * 12 + px*12, y - px*2))
                draw_text(os.path.splitext(i)[0], mid_title_font, white, tile_size * 2, y + px, True)

                if pygame.Rect(tile_size * 3.5, y-3, tile_size * 9, tile_size * 0.75+ px) not in self.middle_buttons:
                    self.middle_buttons.append(pygame.Rect(tile_size * 3.5, y-3, tile_size * 9, tile_size * 0.75+ px))
                if pygame.Rect(tile_size * 12 + px*12, y - px*2, tile_size, tile_size) not in self.trash_buttons:
                    self.trash_buttons.append(pygame.Rect(tile_size * 12 + px*12, y - px*2, tile_size, tile_size))
                y += 1.2 * tile_size
            screen.blit(self.bottom_button_img, (tile_size * 3.5 - px*2, y - px*2))
            draw_text("Back", mid_title_font, white, tile_size * 2, y + px, True)
            self.bottom_button = pygame.Rect(tile_size * 3.5, y-px, tile_size * 9, tile_size * 0.75+ px)

        elif self.state == 2:
            screen.blit(self.frame_img, (tile_size * 3.5 - px*2, tile_size * 4 - px*2))
            screen.blit(self.middle_button_img, (tile_size * 3.5 - px*2, tile_size * 5.2 - px*2))
            screen.blit(self.bottom_button_img, (tile_size * 3.5 - px*2, tile_size * 6.4 - px*2))
            draw_text("New world", title_font, (0, 0, 0), px*3, tile_size / 2 + px*2, True)
            draw_text("New world", title_font, white, px*3, tile_size / 2, True)
            if self.time <= 35:
                draw_text(self.world_name + "i", mid_title_font, white, tile_size * 2, tile_size * 4 + px, True)
                self.time += 1
            elif self.time <= 70:
                draw_text(self.world_name + " ", mid_title_font, white, tile_size * 2, tile_size * 4 + px, True)
                self.time += 1
            else: self.time = 0
            draw_text("Done", mid_title_font, white, tile_size * 2, tile_size * 5.2 + px, True)
            draw_text("Cancel", mid_title_font, white, tile_size * 2, 6.4 * tile_size + px, True)

            self.bottom_button = pygame.Rect(tile_size * 3.5, tile_size * 6.4 -px, tile_size * 9, tile_size * 0.75+ px)
        elif self.state == 3:
            if self.pressed[0] and self.press_time > 0:
                if self.pressed[1] == "top":
                    self.top_button_img = self.pressed_big_button_img
                elif self.pressed[1] == "mid":
                    self.middle_button_img = self.pressed_big_button_img
                self.press_time -= 1
            else:
                self.pressed[0] = False
                if self.pressed[1] == "top":
                    self.top_button_img = self.big_button_img
                elif self.pressed[1] == "mid":
                    self.middle_button_img = self.big_button_img
                self.pressed[1] = None


            screen.blit(self.top_button_img, (tile_size * 3.5 - px*2, tile_size * 4 - px*2))
            screen.blit(self.middle_button_img, (tile_size * 3.5 - px*2, tile_size * 5.2 - px*2))
            screen.blit(self.bottom_button_img, (tile_size * 3.5 - px*2, tile_size * 6.4 - px*2))
            draw_text("Settings", title_font, (0, 0, 0), px*3, tile_size / 2 + px*2, True)
            draw_text("Settings", title_font, white, px*3, tile_size / 2, True)
            draw_text("Dev tools", mid_title_font, white, tile_size * 2, tile_size * 5.2 + px, True)
            draw_text("Fullscreen", mid_title_font, white, tile_size * 2, tile_size * 4 + px, True)
            if save_load.full_screen:
                screen.blit(self.lever_on, (tile_size * 11 + px*4, tile_size * 4+ px*2))
            else:
                screen.blit(self.lever_off, (tile_size * 11 + px*4, tile_size * 4 + px*2))
            if allow_dev_tools:
                screen.blit(self.lever_on, (tile_size * 11 + px*4, tile_size * 5.2 + px*2))
            else:
                screen.blit(self.lever_off, (tile_size * 11 + px*4, tile_size * 5.2 + px*2))
            draw_text("Back", mid_title_font, white, tile_size * 2, 6.4 * tile_size + px , True)
        elif self.state == 4:
            screen.blit(self.ask_base, (self.left, SCREEN_HEIGHT / 3))
            draw_text("Do you want to", text_font, white,
                      self.left, SCREEN_HEIGHT / 3 + px*10, True)
            draw_text("delete", text_font, white,
                      self.left, SCREEN_HEIGHT / 3 + tile_size + px*2, True)
            draw_text(os.path.splitext(self.delete_world)[0] + "?", text_font, white,
                      self.left, SCREEN_HEIGHT / 3 + tile_size + px*10, True)
            screen.blit(self.yes_button, (self.left + tile_size + px*4, SCREEN_HEIGHT / 3 + tile_size*3 - px*2))
            screen.blit(self.no_button,
                        (self.left + tile_size*4, SCREEN_HEIGHT / 3 + tile_size * 3 - px*2))
            draw_text("yes    No", text_font, white,
                      self.left + 26*px, SCREEN_HEIGHT / 3 + tile_size*3, True)




    def handle(self):
        pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(pos[0], pos[1], 3, 3)
        global game_state
        if self.state == 0:
            self.bottom_button = pygame.Rect(tile_size * 3.5, tile_size * 6.4 -3, tile_size * 9, tile_size * 0.75+ px)
            if mouse_rect.colliderect(self.top_button):
                self.top_button_img = self.selected_big_button_img
                if player.left_clicked:
                    self.top_button_img = self.big_button_img
                    self.state = 1
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_big_button_img
                self.top_button_img = self.big_button_img
                self.quit_button_img = self.big_button_img
                if player.left_clicked:
                    self.bottom_button_img = self.big_button_img
                    self.state = 3
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.quit_button):
                self.quit_button_img = self.selected_big_button_img
                self.top_button_img = self.big_button_img
                self.bottom_button_img = self.big_button_img
                if player.left_clicked:
                    save_load.save_settings()
                    global run
                    run = False
            else:
                self.bottom_button_img = self.big_button_img
                self.top_button_img = self.big_button_img
                self.quit_button_img = self.big_button_img

        elif self.state == 1:
            if mouse_rect.colliderect(self.top_button):
                self.top_button_img = self.selected_big_button_img
                if player.left_clicked:
                    self.state = 2
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            elif mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_big_button_img
                self.top_button_img = self.big_button_img
                if player.left_clicked:
                    self.state = 0
                    self.bottom_button = pygame.Rect(tile_size * 3.5, tile_size * 6.4 -3, tile_size * 9, tile_size * 0.75 + px)
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            else:
                self.bottom_button_img = self.big_button_img
                self.middle_button_img = self.big_button_img
                self.top_button_img = self.big_button_img
            j = 0
            for i in self.middle_buttons:
                if mouse_rect.colliderect(i):
                    self.current_middle_button = j
                    if player.left_clicked:
                        blocks.set_blocks(tiles.start_x, tiles.start_y)
                        save_load.load(self.file_names[j])
                        self.middle_button_img = self.big_button_img
                        game_state = play_state
                        sounds.play_sound(sounds.cursor_sfx)
                        player.left_clicked = False

                j += 1
            j = 0
            for i in self.trash_buttons:
                if mouse_rect.colliderect(i):
                    self.current_trash_button = j
                    if player.left_clicked:
                        self.pressed_trash_button = j
                        self.draw()
                        sounds.play_sound(sounds.cursor_sfx)
                        player.left_clicked = False
                        self.delete_world = self.file_names[j]
                        self.state = 4
                j += 1

        elif self.state == 2:
            if mouse_rect.colliderect(self.middle_button):
                self.middle_button_img = self.selected_big_button_img
                if player.left_clicked:

                    if self.world_name == "":
                        
                        save_load.current_world = "untitled.cheese"
                        game_state = play_state
                        self.world_name = ""
                        sounds.play_sound(sounds.cursor_sfx)
                        player.left_clicked = False
                    else:
                        already_name = False
                        for i in self.file_names:
                            if self.world_name+ ".cheese" == i:
                                already_name = True
                                break
                        if not already_name:
                            self.reset()
                            save_load.current_world = self.world_name + ".cheese"

                            game_state = play_state
                            self.world_name = ""
                            sounds.play_sound(sounds.cursor_sfx)
                            player.left_clicked = False
                            self.middle_button_img = self.big_button_img
            elif mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_big_button_img
                self.middle_button_img = self.big_button_img
                if player.left_clicked:
                    self.world_name = ""
                    self.state = 1
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            else:
                self.middle_button_img = self.big_button_img
                self.bottom_button_img = self.big_button_img

        elif self.state == 3:
            if mouse_rect.colliderect(self.top_button):
                self.top_button_img = self.selected_big_button_img
                if player.left_clicked:
                    self.pressed = [True, "top"]
                    self.press_time = 18

                    if save_load.full_screen:
                        global screen
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        save_load.full_screen = False
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                        save_load.full_screen = True
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    save_load.save_settings()
            elif mouse_rect.colliderect(self.middle_button):
                self.middle_button_img = self.selected_big_button_img
                if player.left_clicked:
                    self.pressed = [True, "mid"]
                    self.press_time = 18
                    global allow_dev_tools
                    if allow_dev_tools:
                        allow_dev_tools = False
                    else: allow_dev_tools = True
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    save_load.save_settings()
            elif mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_big_button_img
                if player.left_clicked:
                    self.state = 0
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
            else:
                self.top_button_img = self.big_button_img
                self.middle_button_img = self.big_button_img
                self.bottom_button_img = self.big_button_img

        elif self.state == 4:
            yes_button = pygame.Rect(self.left + tile_size + px*4, SCREEN_HEIGHT / 3 + tile_size*3 - px*2, tile_size*2 - px,
                                     px*13)
            no_button = pygame.Rect(self.left + tile_size*4, SCREEN_HEIGHT / 3 + tile_size*3 - px*2, tile_size*2 - px,
                                     px*13)

            if mouse_rect.colliderect(yes_button):
                self.yes_button = self.selected_button_img
                if player.left_clicked:
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    self.trash_buttons = []
                    os.remove("assets/saves/" + self.delete_world)
                    self.state = 1
            elif mouse_rect.colliderect(no_button):
                self.no_button = self.selected_button_img
                self.yes_button = self.small_button_img
                if player.left_clicked:
                    self.no_button = self.pressed_button_img
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    self.state = 1
            else:
                self.yes_button = self.small_button_img
                self.no_button = self.small_button_img
    def reset(self):
        player.currency = 500
        blocks.all_blocks = []
        blocks.all_fences = []
        decor.decors = []
        decor.setup_decors()
        global entities
        entities = []
        blocks.set_blocks(tiles.start_x, tiles.start_y)
        inventory.__init__()
        market.__init__()
        market.markets = 0
        player.pos_x = SCREEN_WIDTH / 2 - tile_size / 2
        player.pos_y = SCREEN_HEIGHT / 2 - tile_size / 2
        cam.__init__()

class paused_menu:
    def __init__(self):
        self.left = SCREEN_WIDTH / 2 - px * 111 / 2
        self.button_img = set_image("GUI/buttons/mid_button")
        self.selected_img = set_image("GUI/buttons/selected_mid_button")
        self.pressed_img = set_image("GUI/buttons/pressed_mid_button")
        self.save_icon = set_image("GUI/buttons/save_icon")

        self.sound_button_img = set_image("GUI/buttons/sound_button")
        self.selected_sound_button = set_image("GUI/buttons/selected_sound_button")
        self.muted_sound_button = set_image("GUI/buttons/mute_button")
        self.selected_muted_sound_button = set_image("GUI/buttons/selected_mute_button")
        self.sound_icon = self.sound_button_img

        self.music_icon = set_image("GUI/buttons/music_button")
        self.slider = set_image("GUI/icons/slider")
        self.slider_button_img = set_image("GUI/buttons/slider_button")

        self.sound_x = self.left + tile_size * 2 + tile_size * 3 * sounds.sound_effect_volume - px * 2
        self.slider_button = pygame.Rect(self.left + tile_size*1.5 + px*4, SCREEN_HEIGHT / 3 + tile_size + px*11,tile_size * 5 + px *4, px*3)
        self.sound_button = pygame.Rect(self.left + px*8, SCREEN_HEIGHT / 3 + tile_size + px*6, 13*px, 13*px)
        self.top_button_img = self.button_img
        self.mid_button_img = self.button_img
        self.bottom_button_img = self.button_img

        self.top_button = pygame.Rect(self.left + tile_size *1.5, SCREEN_HEIGHT / 3 + tile_size + px*6,
                                      63*px, 13*px)
        self.mid_button = pygame.Rect(self.left + tile_size * 1.5, SCREEN_HEIGHT / 3 + tile_size*2 + px*6,
                                      63 * px, 13 * px)
        self.bottom_button = pygame.Rect(self.left + tile_size * 1.5, SCREEN_HEIGHT / 3 + tile_size*3 + px*6,
                                      63 * px, 13 * px)

        self.state = 0
    def draw(self):
        screen.blit(start_menu.ask_base, (self.left, SCREEN_HEIGHT / 3))
        if self.state == 0:
            draw_text("Paused", mid_title_font, white, 0, SCREEN_HEIGHT / 3 + px*7, True)
            screen.blit(self.top_button_img,
                        (self.left + tile_size *1.5, SCREEN_HEIGHT / 3 + tile_size + px*6))
            screen.blit(self.mid_button_img,
                        (self.left + tile_size * 1.5, SCREEN_HEIGHT / 3 + tile_size*2 + px*6))
            screen.blit(self.bottom_button_img,
                        (self.left + tile_size * 1.5, SCREEN_HEIGHT / 3 + tile_size * 3 + px*6))
            draw_text("Resume", text_font, white, 0, SCREEN_HEIGHT / 3 + tile_size + px*9, True)
            draw_text("Settings", text_font, white, 0, SCREEN_HEIGHT / 3 + tile_size*2 + px*9, True)
            draw_text("Exit", text_font, white, 0, SCREEN_HEIGHT / 3 + tile_size*3 + px*9, True)
        elif self.state == 1:
            draw_text("Settings", mid_title_font, white, 0, SCREEN_HEIGHT / 3 + px*7, True)
            screen.blit(self.music_icon,(self.left + px*8, SCREEN_HEIGHT / 3 + tile_size * 2 + px*6))
            screen.blit(self.sound_icon,(self.left + px*8, SCREEN_HEIGHT / 3 + tile_size + px*6))
            screen.blit(self.slider, (self.left + tile_size*1.5 + px*8, SCREEN_HEIGHT / 3 + tile_size + px*13))
            screen.blit(self.slider_button_img, (self.sound_x,
                                                 SCREEN_HEIGHT / 3 + tile_size + px * 11))
            screen.blit(self.slider,
                        (self.left + tile_size * 1.5 + px*8, SCREEN_HEIGHT / 3 + tile_size*2 + px*13))
            screen.blit(self.slider_button_img,
                        (self.left + tile_size*2 + tile_size*3*sounds.music_volume - px*2, SCREEN_HEIGHT / 3 + tile_size*2 + px*11))
            screen.blit(self.bottom_button_img,
                        (self.left + tile_size * 1.5, SCREEN_HEIGHT / 3 + tile_size * 3 + px*6))
            draw_text("Back", text_font, white, 0, SCREEN_HEIGHT / 3 + tile_size * 3 + px*9, True)

    def handle(self):
        global game_state
        pos = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(pos[0], pos[1], 12, 12)
        self.sound_x = self.left + tile_size * 2 + tile_size * 3 * sounds.sound_effect_volume - px * 2
        if self.state == 0:
            if mouse_rect.colliderect(self.top_button):
                self.top_button_img = self.selected_img

                self.mid_button_img = self.button_img
                self.bottom_button_img = self.button_img
                if player.left_clicked:
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    game_state = play_state

            elif mouse_rect.colliderect(self.mid_button):
                self.mid_button_img = self.selected_img

                self.top_button_img = self.button_img
                self.bottom_button_img = self.button_img
                if player.left_clicked:
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    self.state = 1
            elif mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_img

                self.top_button_img = self.button_img
                self.mid_button_img = self.button_img
                if player.left_clicked:
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    save_load.save(save_load.current_world)
                    screen.fill((0,0,0))
                    start_menu.state = 0
                    game_state = start_state
            else:
                self.top_button_img = self.button_img
                self.mid_button_img = self.button_img
                self.bottom_button_img = self.button_img
        elif self.state == 1:
            if mouse_rect.colliderect(self.bottom_button):
                self.bottom_button_img = self.selected_img
                if player.left_clicked:
                    sounds.play_sound(sounds.cursor_sfx)
                    player.left_clicked = False
                    self.state = 0
                    self.bottom_button_img = self.button_img
            elif mouse_rect.colliderect(self.sound_button):
                if self.sound_icon == self.sound_button_img:
                    self.sound_icon = self.selected_sound_button
                elif self.sound_icon == self.muted_sound_button:
                    self.sound_icon = self.selected_muted_sound_button
                if player.left_clicked:
                    if sounds.sound_effect_volume == 0:
                        sounds.sound_effect_volume = 0.5
                        self.sound_icon = self.selected_sound_button
                        player.left_clicked = False
                    else:
                        self.sound_icon = self.muted_sound_button
                        sounds.sound_effect_volume = 0
                        player.left_clicked = False 



            elif mouse_rect.colliderect(self.slider_button):
                self.bottom_button_img = self.button_img
                if player.left_clicked:
                    pos = pygame.mouse.get_pos()
                    mouse_rect = pygame.Rect(pos[0], pos[1], 15, 15)
                    if self.left + tile_size * 2 + tile_size * 3 - px * 2 >= \
                            mouse_rect[0] >= self.left + tile_size*2 - px*2:
                        self.sound_x = mouse_rect[0]
                        self.draw()
                        sounds.sound_effect_volume = (self.sound_x - (self.left + tile_size*2 - px*2))/(tile_size*3)
                        if sounds.sound_effect_volume < 0.011:
                            sounds.sound_effect_volume = 0
                        if sounds.sound_effect_volume == 0:
                            self.sound_icon = self.muted_sound_button
                        else:
                            self.sound_icon = self.sound_button_img

            else:
                self.bottom_button_img = self.button_img
                if self.sound_icon == self.selected_sound_button:
                    self.sound_icon = self.sound_button_img
                elif self.sound_icon == self.selected_muted_sound_button:
                    self.sound_icon = self.muted_sound_button



class sounds:
    def __init__(self):
        self.sound_effect_volume = 0.5
        self.music_volume = 0.5
        self.moo_sfx = pygame.mixer.Sound('assets/sounds/entity/cow_sound.ogg')
        self.moo_sfx_2 = pygame.mixer.Sound('assets/sounds/entity/cow_sound_2.ogg')
        self.cursor_sfx = pygame.mixer.Sound('assets/sounds/cursor.ogg')
        self.break_sfx = pygame.mixer.Sound('assets/sounds/break.ogg')
        self.pick_sfx = pygame.mixer.Sound('assets/sounds/pick.ogg')
        self.place_sfx = pygame.mixer.Sound('assets/sounds/place.ogg')
    def play_sound(self, sound):
        sound.set_volume(self.sound_effect_volume)
        sound.play()

class develop:
    def __init__(self):
        self.texts = []
        self.add_rect_state = False
        self.state = 0
        self.pos_0 = (0,0)
        self.clicked = False
    def add_rect(self):
        pos = (round(pygame.mouse.get_pos()[0] / px) *px, round(pygame.mouse.get_pos()[1]/px) *px)

        if self.state == 0:
            if self.clicked:
                self.pos_0 = (pos[0], pos[1])
                self.state = 1
                self.clicked = False
        elif self.state == 1:
            rect = pygame.Rect(self.pos_0[0], self.pos_0[1], pos[0] - self.pos_0[0], pos[1] - self.pos_0[1])
            pygame.draw.rect(screen, red, rect)
            if self.clicked:
                print("pygame.Rect(" + str(int(rect[0]/px)) + "*px, " + str(int(rect[1]/px)) + "*px, " +
                      str(int(rect[2]/px)) + "*px, " + str(int(rect[3]/px)) + "*px)")
                self.state = 0
                self.clicked = False
                self.add_rect_state = False
    def add_text(self):
        pos = (round(pygame.mouse.get_pos()[0] / px) * 3, round(pygame.mouse.get_pos()[1] / px) * 3)
        text = [input("add text: ")]
        while len(text)<2:
            font_input = input("select font: inventory_text_font[0]\ntext_font[1]\ntitle_font[2]\nmid_title_font[3] ")
            if font_input == "0":
                text.append(inventory_text_font)
            elif font_input == "1":
                text.append(text_font)
            elif font_input == "2":
                text.append(title_font)
            elif font_input == "3":
                text.append(mid_title_font)
            else:
                print("invalid syntax")
        text.append(white)

        text.append(pos[0])
        text.append(pos[1])
        print(text_font)
        self.texts.append(text)
        self.add_rect_state = False
    def draw(self):
        for i in self.texts:
            draw_text(i[0], i[1], white, i[3], i[4])
    def clicking(self):
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.dict['button'] == 1:
                self.clicked = True
        for event in pygame.event.get(pygame.MOUSEBUTTONUP):
            if event.dict['button'] == 1:
                self.clicked = False


# Initializing Classes
entity = entity()
develop = develop()
save_load = save_load()
start_menu = start_menu()
sounds = sounds()
paused_menu = paused_menu()
cam = camera()
col_checker = collision_checker()
player = player()
blocks = blocks()
items = items()
market = market()
trade = trade()
dialogues = dialogues()
tiles = tiles()
decor = decor()
inventory = inventory()


# TRADERS
trader_1 = trader(tile_size * 23, tile_size * 12,
                    [(items.axe, items.axe["price"]*2),
                            (items.gate, items.gate["price"]*2, (items.wood, 1)),
                            (items.fence_1, items.fence_1["price"]*2, (items.wood, 1)),
                            (items.cow, items.cow["price"]*2),
                            (items.market, items.market["price"]*2, (items.wood, 20)),
                            (None, None)])
trader_2 = trader(tile_size * 21, tile_size * 12,
                    [(items.hay_bale, items.hay_bale["price"]*2),
                            (items.drinker, items.drinker["price"]*2),
                            (items.feeder, items.feeder["price"]*2),
                            (items.bucket, items.bucket["price"]*2),
                            (items.milk_bucket, items.milk_bucket["price"]*2),
                            (items.water_bucket, items.water_bucket["price"]*2),
                            (None, None)])
traders = [trader_2, trader_1]

save_load.load_settings()
entities = []

blocks.set_drops()

tiles.set_solid_tiles(num_map)
decor.setup_decors()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if game_state == start_state:
                if start_menu.state == 2:
                    if event.key == pygame.K_BACKSPACE:
                        start_menu.world_name = start_menu.world_name[:-1]
                    else:
                        start_menu.world_name += event.unicode

            if event.key == pygame.K_w:
                up_pressed = True
            elif event.key == pygame.K_s:
                down_pressed = True
            elif event.key == pygame.K_a:
                left_pressed = True
            elif event.key == pygame.K_d:
                right_pressed = True

            elif event.key == pygame.K_ESCAPE:
                if game_state == inventory_state:
                    game_state = play_state
                    inventory.selected_slot = 0
                elif game_state == trade_state:
                    if trade.state == 0:
                        trade.leave_trade()
                        game_state = play_state
                    else:
                        trade.state = 0
                elif game_state == market_state:
                    if market.state == 0:
                        game_state = play_state
                        inventory.selected_slot = 0
                    elif market.state == 1:
                        market.state = 0
                        inventory.selected_slot = 0
                    elif market.state == 2:
                        market.state = 1
                elif game_state == play_state:
                    dev_tools = False
                    game_state = pause_state
                    player.direction = "down"
                elif game_state == pause_state:
                    if paused_menu.state == 0:
                        game_state = play_state
                        paused_menu.state = 0
                    elif paused_menu.state == 1:
                        paused_menu.state = 0

            elif event.key == pygame.K_c and game_state != start_state and allow_dev_tools:
                pygame.image.save(screen, "screenshot.png")
                if dev_tools:
                    dev_tools = False
                else:
                    dev_tools = True

            elif event.key == pygame.K_e:
                if game_state == play_state:
                    game_state = inventory_state
                elif game_state == inventory_state:
                    game_state = play_state
                    inventory.selected_slot = 0
                elif game_state == market_state:
                    if market.state == 0:
                        game_state = play_state
                        inventory.selected_slot = 0
                    elif market.state == 1:
                        market.state = 0
                        inventory.selected_slot = 0
                    elif market.state == 2:
                        market.state = 1
                elif game_state == trade_state:
                    if trade.state == 0:
                        trade.leave_trade()
                        game_state = play_state
                    else:
                        trade.state = 0
                        trade.value = 1

            elif event.key == pygame.K_LSHIFT:
                player.sprinting = True
                inventory.shift_clicked = True

            elif event.key == pygame.K_y:
                if dev_tools:
                    develop.add_rect_state = True
            elif event.key == pygame.K_x:
                if dev_tools:
                    develop.add_text()

            elif event.key == pygame.K_q:
                if game_state == play_state or game_state == inventory_state:
                    if inventory.inventory_slots[inventory.selected_slot]['item'] is not None:
                        player.drop_item(inventory.inventory_slots[inventory.selected_slot]['item'])
                        inventory.inventory_slots[inventory.selected_slot]["value"] -= 1
            elif event.key == pygame.K_F11:
                if save_load.full_screen:
                    save_load.full_screen = False
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                else:
                    save_load.full_screen = True
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

        if event.type == pygame.MOUSEWHEEL:
            if game_state == play_state:
                if inventory.selected_slot == 0 and event.dict.get('y') <= -1:
                    inventory.selected_slot = 5
                elif inventory.selected_slot == 5 and event.dict.get('y') >= 1:
                    inventory.selected_slot = 0
                else:
                    if event.dict.get('y') >= 1:
                        inventory.selected_slot += 1
                    elif event.dict.get('y') <= -1:
                        inventory.selected_slot -= 1
            elif game_state == trade_state:
                if event.dict.get('y') <= -1 and trade.can_buy == 0 and trade.first_trade + 5 != len(trade.trades) and len(
                        trade.trades) > 4:
                    trade.first_trade += 1
                    trade.trade_rects = []
                    trade.trade_item_rects = []
                    trade.trade_item_rects_2 = []
                elif event.dict.get('y') >= 1 and trade.can_buy == 0 and trade.first_trade != 0:
                    trade.first_trade -= 1
                    trade.trade_rects = []
                    trade.trade_item_rects = []
                    trade.trade_item_rects_2 = []


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.dict['button'] == 3:
                player.right_clicked = True
            if event.dict['button'] == 1:
                player.left_clicked = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.dict['button'] == 3:
                player.right_clicked = False
            if event.dict['button'] == 1:
                player.left_clicked = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                up_pressed = False
                player.time = 0
            elif event.key == pygame.K_s:
                down_pressed = False
                player.time = 0
            elif event.key == pygame.K_a:
                left_pressed = False
                player.time = 0
            elif event.key == pygame.K_d:
                right_pressed = False
                player.time = 0
            elif event.key == pygame.K_LSHIFT:
                player.sprinting = False
                inventory.shift_clicked = False

    clock.tick(FPS)
    entity.icons = []
    if game_state == start_state:
        start_menu.draw()
        start_menu.handle()
    elif game_state == play_state:
        market.sell()
        player.move_player()
        tiles.set_solid_tiles(num_map)
        blocks.update_blocks()
        tiles.draw_map(num_map)
        decor.draw_decors()
        for i in entities:
            i.move()
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
                if i.show_icon:
                    entity.icons.append(i)
        for i in traders:
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
            i.update_hitbox()
        player.place_block()
        player.break_block()
        col_checker.check_block_interact()
        player.draw_entity()
        blocks.draw_blocks()
        items.move_to_player()
        items.update_hitboxes()
        items.draw_items()
        dialogues.draw_block_life_bar()
        player.draw_second_sprite()
        col_checker.check_item_collision()
        entity.draw_icon()
        inventory.handle_inventory()
        inventory.draw_inventory()
        player.draw_coins()
    elif game_state == inventory_state:
        market.sell()
        tiles.set_solid_tiles(num_map)
        tiles.draw_map(num_map)
        decor.draw_decors()
        for i in entities:
            i.move()
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
                if i.show_icon:
                    entity.icons.append(i)
        for i in traders:
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
        player.draw_entity()
        blocks.draw_blocks()
        items.update_hitboxes()
        items.move_to_player()
        items.draw_items()
        col_checker.check_item_collision()
        entity.draw_icon()
        inventory.handle_inventory()
        inventory.draw_inventory()
        player.draw_coins()
    elif game_state == trade_state:
        market.sell()
        tiles.set_solid_tiles(num_map)
        tiles.draw_map(num_map)
        decor.draw_decors()
        for i in entities:
            i.move()
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
                if i.show_icon:
                    entity.icons.append(i)
        for i in traders:
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
        player.draw_entity()
        blocks.draw_blocks()
        items.update_hitboxes()
        items.move_to_player()
        items.draw_items()
        col_checker.check_item_collision()
        entity.draw_icon()
        inventory.handle_inventory()
        inventory.draw_inventory()
        trade.handle_trades()
        trade.draw_trades()
        player.draw_coins()
    elif game_state == market_state:
        market.sell()
        tiles.set_solid_tiles(num_map)
        tiles.draw_map(num_map)
        decor.draw_decors()
        for i in entities:
            i.move()
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
                if i.show_icon:
                    entity.icons.append(i)
        for i in traders:
            if i.main_hitbox.colliderect(screen_rect):
                i.draw_entity()
        player.draw_entity()
        blocks.draw_blocks()
        items.update_hitboxes()
        items.move_to_player()
        items.draw_items()
        col_checker.check_item_collision()
        entity.draw_icon()
        inventory.handle_inventory()
        inventory.draw_inventory()
        market.handle()
        market.draw()
        player.draw_coins()
    elif game_state == pause_state:
        paused_menu.handle()
        paused_menu.draw()
    if dev_tools:
        draw_text("x :" + str(round(player.pos_x / tile_size, 2)), text_font, white, 10, 10)
        draw_text("y :" + str(round(player.pos_y / tile_size, 2)), text_font, white, 10, 40)
        draw_text("FPS :" + str(round(clock.get_fps(), 1)), text_font, white, 10, 70)
        pos = pygame.mouse.get_pos()
        
        draw_text("MOUSE_POS: x:" + str(int((pos[0])/tile_size)) + "," + str(int(pos[0]%tile_size/px)) +" y:"
                  + str(int(pos[1]/tile_size)) + "," + str(int(pos[1]%tile_size/px)), text_font, white, 10, 100)
        develop.clicking()
        develop.draw()
        if develop.add_rect_state:
            develop.add_rect()
    pygame.display.update()
if game_state != start_state:
    save_load.save(save_load.current_world)
pygame.quit()