import debug

import pygame
import sys
from collections import defaultdict

from constants import GameState
from data import Equipment, Item
from colors import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class GameUI:
    def __init__(self, game):
        self.game = game
        self.show_item_popup = False

    def draw_text(self, text, font, color, x, y, align="left", max_width=None):
        """
        渲染文字，支持自动换行和对齐方式
        - align: "left", "center", "right"
        - max_width: 设定最大行宽，超过则换行
        """
        if max_width:
            words = text.split(' ')
            lines = []
            current_line = ""

            # 构建换行列表
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            total_height = 0
            for i, line_text in enumerate(lines):
                text_surface = font.render(line_text.strip(), True, color)
                text_rect = text_surface.get_rect()

                if align == "center":
                    text_rect.centerx = x
                elif align == "right":
                    text_rect.right = x
                else:
                    text_rect.left = x
                text_rect.top = y + i * font.get_linesize()

                screen.blit(text_surface, text_rect)
                total_height += font.get_linesize()

            return total_height

        else:
            # 单行模式
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()

            if align == "center":
                text_rect.center = (x, y)
            elif align == "right":
                text_rect.right = x
                text_rect.top = y
            else:
                text_rect.left = x
                text_rect.top = y

            screen.blit(text_surface, text_rect)
            return text_rect.height

    def draw_button(self, text, x, y, width, height,
                inactive_color, active_color,
                text_color=KURO, font_to_use=None,
                border_color=None, border_width=0):
        """渲染按钮，并在鼠标悬停时改变颜色"""

        font_to_use = font_to_use or FONT_MEDIUM
        mouse_pos = pygame.mouse.get_pos()

        is_hovered = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height
        color = active_color if is_hovered else inactive_color

        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=6)  # 轻圆角风格

        if border_color and border_width > 0:
            pygame.draw.rect(screen, border_color, (x, y, width, height), border_width, border_radius=6)

        text_surf = font_to_use.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + width / 2, y + height / 2))
        screen.blit(text_surf, text_rect)

        return is_hovered

    def draw_message_log(self, x, y, width, height):
        # 背景与边框
        pygame.draw.rect(screen, LIGHT_PANEL, (x, y, width, height))
        pygame.draw.rect(screen, TEXT_LIGHT, (x, y, width, height), 1)

        padding = 5
        line_height = FONT_SMALL.get_linesize()
        max_lines = (height - padding * 2) // line_height
        total_lines = len(self.game.message_log)

        # 限制滑动范围
        max_offset = max(0, total_lines - max_lines)
        self.game.scroll_offset_message_log = max(0, min(self.game.scroll_offset_message_log, max_offset))

        # 取出当前要显示的日志行
        start_idx = self.game.scroll_offset_message_log
        end_idx = min(total_lines, start_idx + max_lines)
        log_to_display = self.game.message_log[start_idx:end_idx]

        current_y = y + padding
        for message in log_to_display:
            self.draw_text(message, FONT_SMALL, TEXT_FAINT, x + padding, current_y, max_width=width - 2 * padding)
            current_y += line_height * (1 + message.count('\n'))
            if current_y > y + height - line_height:
                break

        # --- 清除按钮 ---
        clear_btn_w, clear_btn_h = 50, 24
        if self.draw_button("清除", x + width - clear_btn_w - 24, y + height - clear_btn_h - 12,
                            clear_btn_w, clear_btn_h, BTN_RED, BTN_RED_HOVER, font_to_use=FONT_SMALL):
            if self.game.clicked_this_frame:
                self.game.message_log.clear()
                self.game.scroll_offset_message_log = 0

        # --- 滑动条 ---
        if total_lines > max_lines:
            scrollbar_width = 10
            bar_x = x + width - scrollbar_width - 4
            bar_y = y + padding
            bar_height = height - 2 * padding
            scroll_ratio = max_lines / total_lines
            scroll_bar_h = max(int(bar_height * scroll_ratio), 20)
            scroll_bar_y = bar_y + int((self.game.scroll_offset_message_log / max_offset) * (bar_height - scroll_bar_h))

            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, scrollbar_width, bar_height))  # 背景槽
            pygame.draw.rect(screen, (180, 180, 180), (bar_x, scroll_bar_y, scrollbar_width, scroll_bar_h))  # 滑块

            # 鼠标滚轮事件
            if self.game.mouse_in_rect(x, y, width, height):
                if self.game.scroll_up:
                    self.game.scroll_offset_message_log = max(0, self.game.scroll_offset_message_log - 1)
                elif self.game.scroll_down:
                    self.game.scroll_offset_message_log = min(max_offset, self.game.scroll_offset_message_log + 1)

    def draw_player_status_bar(self, x, y, width, height):
        pygame.draw.rect(screen, LIGHT_PANEL, (x, y, width, height))
        pygame.draw.rect(screen, TEXT_LIGHT, (x, y, width, height), 1)

        self.draw_text(f"{self.game.player.name} | Lvl: {self.game.player.level}", FONT_MEDIUM, TEXT_LIGHT, x + 10, y + 10)
        self.draw_text(f"HP: {self.game.player.hp}/{self.game.player.max_hp}", FONT_SMALL, BTN_GREEN if self.game.player.hp > self.game.player.max_hp * 0.3 else BTN_RED_DARK, x + 10, y + 40)
        self.draw_text(f"MP: {self.game.player.mp}/{self.game.player.max_mp}", FONT_SMALL, BTN_BLUE, x + 170, y + 40)
        self.draw_text(f"ATK: {self.game.player.attack} DEF: {self.game.player.defense}", FONT_SMALL, TEXT_FAINT, x + 10, y + 65)
        self.draw_text(f"EXP: {self.game.player.exp}/{self.game.player.exp_to_next_level}", FONT_SMALL, BTN_PURPLE, x + 170, y + 65)
        self.draw_text(f"金币: {self.game.gold}", FONT_SMALL, BTN_ORANGE, x + 170, y + 90)

        for effect in self.game.player.status_effects[:2]:
            self.draw_text(f"{effect.name}({effect.turns_remaining})", FONT_SMALL, BTN_PURPLE, x + 10, y + 90)

    def draw_main_menu(self):
        screen.fill(BG_DARK)
        self.draw_text("RPG 文字冒险游戏", FONT_TITLE, SHIRONERI, SCREEN_WIDTH//2, 150, "center")

        if self.draw_button("开始新游戏", SCREEN_WIDTH//2 - 100, 300, 200, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.game.clicked_this_frame: self.game.start_new_game()
        # Add Load Game Button if implemented
        if self.draw_button("退出游戏", SCREEN_WIDTH//2 - 100, 380, 200, 50, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame: pygame.quit(); sys.exit()
        if self.draw_button("DEBUG", SCREEN_WIDTH - 70, SCREEN_HEIGHT -34, 60, 24, BTN_RED, BTN_RED_HOVER, font_to_use=FONT_SMALL):
            if self.game.clicked_this_frame: debug.DEBUG = True; print(f"DEBUG: {debug.DEBUG}")

    def draw_exploring(self):
        screen.fill(BG_DARK)
        current_loc = self.game.get_current_location()

        # 玩家状态栏
        self.draw_player_status_bar(10, 10, 320, 120)
        pygame.draw.rect(screen, BTN_GRAY_LIGHT, (292, 20, 28, 28), 1)
        if self.draw_button("i", 292, 20, 28, 28, LIGHT_PANEL, BTN_GRAY, BTN_ORANGE, FONT_SMALL):
            if self.game.clicked_this_frame:
                self.game.state = GameState.CHARACTER_INFO

        # 地点信息框
        pygame.draw.rect(screen, LIGHT_PANEL, (SCREEN_WIDTH - 330, 10, 320, 120))
        pygame.draw.rect(screen, TEXT_LIGHT, (SCREEN_WIDTH - 330, 10, 320, 120), 1)
        self.draw_text(f"当前位置: {current_loc['name']}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH - 320, 20)
        self.draw_text(current_loc['description'], FONT_SMALL, TEXT_FAINT, SCREEN_WIDTH - 320, 50, max_width=310)

        # 消息日志
        log_height = 200
        self.draw_message_log(10, SCREEN_HEIGHT - log_height - 10, SCREEN_WIDTH - 20, log_height)

        # 按钮统一属性
        button_width = 160
        button_height = 36
        button_spacing = 16
        button_x_start = 30
        button_y = 150

        if self.draw_button("探索周围", button_x_start, button_y, button_width, button_height, BTN_GREEN, BTN_GREEN_HOVER):
            if self.game.clicked_this_frame:
                if current_loc["enemies"]:
                    self.game.start_battle()
                else:
                    self.game.add_message("这里很安全，你四处看了看，没什么发现。")

        button_y += button_height + button_spacing
        if self.draw_button("物品栏", button_x_start, button_y, button_width, button_height, BTN_BLUE, BTN_BLUE_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.INVENTORY
                self.game.item_page_inv = 0
                self.game.scroll_offset_inventory = 0

        button_y += button_height + button_spacing
        if self.draw_button("装备", button_x_start, button_y, button_width, button_height, BTN_ORANGE, BTN_ORANGE_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.EQUIPMENT_SCREEN
                self.game.scroll_offset_equipment = 0

        if current_loc.get("shop_idx") is not None:
            button_y += button_height + button_spacing
            if self.draw_button("进入商店", button_x_start, button_y, button_width, button_height, BTN_ORANGE, BTN_ORANGE_HOVER):
                if self.game.clicked_this_frame:
                    self.game.current_shop_idx = current_loc["shop_idx"]
                    self.game.state = GameState.SHOP
                    self.game.item_page_shop = 0
                    self.game.scroll_offset_shop = 0

        if current_loc.get("can_rest", False):
            button_y += button_height + button_spacing
            if self.draw_button("休息-20G", button_x_start, button_y, button_width, button_height, 
                                BTN_PURPLE if self.game.gold >= 20 else SHEN_ZI_SE, 
                                BTN_PURPLE_HOVER if self.game.gold >= 20 else SHEN_ZI_SE,
                                KURO if self.game.gold >= 20 else TEXT_FAINT):
                if self.game.clicked_this_frame:
                    if self.game.gold >= 20:
                        self.game.gold -= 20
                        self.game.message_log.clear()
                        self.game.scroll_offset_message_log = 0
                        self.game.rest_at_location()

        # 排除当前地点
        other_locations = [
            (i, loc) for i, loc in enumerate(self.game.all_locations)
            if i != self.game.current_location_idx
        ]

        # 地点跳转按钮
        loc_btn_y_start = 180
        loc_btn_x = SCREEN_WIDTH - button_width - 30
        self.draw_text("前往:", FONT_MEDIUM, TEXT_LIGHT, loc_btn_x + button_width // 2, loc_btn_y_start - 25, "center")
        for i, loc_data in other_locations:
            if self.draw_button(loc_data["name"], loc_btn_x, loc_btn_y_start, button_width, 35, BTN_GRAY, BTN_GRAY_LIGHT, KURO, FONT_SMALL):
                if self.game.clicked_this_frame:
                    self.game.change_location(i)
            loc_btn_y_start += 35 + 10

    def merge_similar_items(self, items):
        grouped_items = defaultdict(list)
        for item in items:
            grouped_items[item.name].append(item)

        merged_items = []
        for name, group in grouped_items.items():
            rep_item = group[0]
            rep_item._quantity = len(group)
            merged_items.append(rep_item)

        return merged_items

    def _draw_multicolumn(self, items, fixed, count, start_x, start_y, x_offset, y_offset, callback):
        """通用多列布局函数"""
        for idx, item in enumerate(items):
            if fixed == 'columns':
                col = idx % count
                row = idx // count
            elif fixed == 'rows':
                col = idx // count
                row = idx % count
            x = start_x + col * x_offset
            y = start_y + row * y_offset
            callback(item, idx, x, y)

    def _draw_generic_list_menu(self, title, items_to_display, item_handler_func, back_state, current_page,
                                scroll_offset_attr_name, items_per_page=5, item_price_func=None, item_desc_func=None):
        screen.fill(BG_DARK)
        self.draw_text(title, FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

        merged_items = self.merge_similar_items(items_to_display)

        # --- 分页 ---
        start_idx = current_page * (items_per_page * 2)  # 每页两列
        end_idx = start_idx + (items_per_page * 2)
        visible_items = merged_items[start_idx:end_idx]

        if not merged_items:
            self.draw_text("空空如也。", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 120, "center")
        else:
            col_start_x = 60
            col_width = SCREEN_WIDTH // 2 - 100
            button_height = 44

            def draw_callback(item, idx, x, y):
                # 显示物品名及数量
                item_count = getattr(item, '_quantity', 1)
                item_text = f"{item.name} x{item_count}" if item_count > 1 else item.name
                if item_price_func:
                    item_text += f" ({item_price_func(item)}G)"
                if self.draw_button(item_text, x, y, col_width, button_height, BTN_GREEN, BTN_GREEN_HOVER, KURO, FONT_MEDIUM):
                    if self.game.clicked_this_frame:
                        item_handler_func(item)
                # 显示描述信息
                desc = item_desc_func(item) if item_desc_func else getattr(item, 'description', None)
                if desc:
                    self.draw_text(desc, FONT_SMALL, TEXT_FAINT, x + 6, y + button_height + 2, max_width=col_width - 12)

            self._draw_multicolumn(
                items=visible_items,
                fixed='columns',
                count=2,
                start_x=60,
                start_y=100,
                x_offset=(SCREEN_WIDTH // 2 + 20) - col_start_x,
                y_offset=76,
                callback=draw_callback
                )

        total_pages = (len(merged_items) - 1) // (items_per_page * 2) + 1
        if total_pages > 1:
            self.draw_text(f"页: {current_page + 1}/{total_pages}", FONT_MEDIUM, TEXT_FAINT, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130, "center")
            if current_page > 0:
                if self.draw_button("上一页", 50, SCREEN_HEIGHT - 130, 100, 38, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.game.clicked_this_frame:
                        setattr(self.game, scroll_offset_attr_name, current_page - 1)
            if current_page < total_pages - 1:
                if self.draw_button("下一页", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 130, 100, 38, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.game.clicked_this_frame:
                        setattr(self.game, scroll_offset_attr_name, current_page + 1)

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 34, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = back_state
                if scroll_offset_attr_name == "item_page_inv":
                    self.game.item_page_inv = 0
                elif scroll_offset_attr_name == "item_page_shop":
                    self.game.item_page_shop = 0

    def draw_battle_reward_screen(self): # 战斗胜利奖励界面
        screen.fill(BG_DARK)
        self.draw_text("战斗胜利！", FONT_LARGE, BTN_ORANGE, SCREEN_WIDTH // 2, 100, "center")

        y = 180
        self.draw_text(f"获得经验: {self.game.battle_rewards['exp']}", FONT_MEDIUM, SHIRONEZUMI, SCREEN_WIDTH // 2, y, "center")
        y += 40
        self.draw_text(f"获得金币: {self.game.battle_rewards['gold']}", FONT_MEDIUM, BTN_ORANGE, SCREEN_WIDTH // 2, y, "center")
        y += 40

        if self.game.battle_rewards['items']:
            self.draw_text("获得物品:", FONT_MEDIUM, SHIRONEZUMI, SCREEN_WIDTH // 2, y, "center")
            y += 30
            for item in self.game.battle_rewards['items']:
                self.draw_text(f"- {item.name}", FONT_SMALL, BTN_CYAN, SCREEN_WIDTH // 2, y, "center")
                y += 25

        if self.draw_button("继续", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.game.clicked_this_frame:
                self.game.process_battle_rewards()

    def draw_game_over(self): # 游戏结束界面
        screen.fill(SUMI)
        self.draw_text("游戏结束", FONT_LARGE, BTN_RED, SCREEN_WIDTH // 2, 200, "center")
        if self.game.player:
            self.draw_text(f"你 {self.game.player.name} 倒下了。", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 250, "center")
            self.draw_text(f"最终等级: {self.game.player.level}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 280, "center")

        if self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100, 400, 200, 50, BTN_GRAY, BTN_GRAY_LIGHT):
            if self.game.clicked_this_frame:
                self.game.state = GameState.MAIN_MENU

    def draw_equipment_screen(self):
        """绘制装备界面"""
        screen.fill(BG_DARK)
        self.draw_text("装备栏", FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

        y = 80
        self.draw_text("当前装备：", FONT_MEDIUM, TEXT_LIGHT, 150, y, "center")
        for slot, item in self.game.player.equipment.items():
            slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
            text = f"{slot_name_map.get(slot, slot)}: {item if item else '无'}"
            self.draw_text(text, FONT_SMALL, BTN_CYAN, 50, y + 40)
            if item:
                pygame.draw.rect(screen, BTN_GRAY_LIGHT, (10, y + 35, 28, 28), 1)
                if self.draw_button("↓", 10, y + 35, 28, 28, BG_DARK, BTN_GRAY, BTN_RED, FONT_SMALL):
                    if self.game.clicked_this_frame:
                        _, msg = self.game.player.unequip(slot)
                        self.game.add_message(msg)
            y += 37

        self.draw_player_status_bar(SCREEN_WIDTH - 330, 10, 320, 120)

        equippable = [it for it in self.game.player.inventory if isinstance(it, Equipment)]
        merged_items = self.merge_similar_items(equippable)

        # --- 多列显示 ---
        col_start_x = 60
        col_width = SCREEN_WIDTH // 2 - 100
        button_height = 44
        items_per_col = 3  # 每列 3 个按钮
        items_per_page = items_per_col * 2  # 每页两列
        page = self.game.scroll_offset_equipment
        start = page * items_per_page
        end = start + items_per_page
        visible_items = merged_items[start:end]

        def equip_callback(item, idx, x, y):
            count = getattr(item, '_quantity', 1)
            btn_text = f"{item.name} x{count}" if count > 1 else item.name

            pygame.draw.rect(screen, LIGHT_PANEL, (x, y, col_width, button_height))
            pygame.draw.rect(screen, TEXT_LIGHT, (x, y, col_width, button_height), 1)
            self.draw_text(btn_text, FONT_MEDIUM, TEXT_LIGHT, x + 20, y + 5, max_width=col_width)

            if self.draw_button("装备", x + col_width - 60, y + button_height // 2 - 14, 50, 28, BTN_PURPLE, BTN_PURPLE_HOVER, KURO, FONT_SMALL):
                if self.game.clicked_this_frame:
                    _, msg = self.game.player.equip(item)
                    self.game.add_message(msg)
                    if len(merged_items) <= self.game.scroll_offset_equipment * items_per_page and self.game.scroll_offset_equipment > 0:
                        self.game.scroll_offset_equipment -= 1

            if getattr(item, "description", None):
                self.draw_text(item.description, FONT_SMALL, TEXT_FAINT, x + 6, y + button_height + 2, max_width=col_width - 12)

        self._draw_multicolumn(
                items=visible_items,
                fixed='columns',
                count=2,
                start_x=60,
                start_y=y+60,
                x_offset=(SCREEN_WIDTH // 2 + 20) - col_start_x,
                y_offset=76,
                callback=equip_callback
                )

        # --- 分页 ---
        total_pages = (len(merged_items) - 1) // items_per_page + 1
        if total_pages > 1:
            self.draw_text(f"页: {page + 1}/{total_pages}", FONT_MEDIUM, TEXT_FAINT, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130, "center")
            if page > 0:
                if self.draw_button("上一页", 50, SCREEN_HEIGHT - 130, 100, 38, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.game.clicked_this_frame:
                        self.game.scroll_offset_equipment -= 1
            if page < total_pages - 1:
                if self.draw_button("下一页", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 130, 100, 38, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.game.clicked_this_frame:
                        self.game.scroll_offset_equipment += 1

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 34, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.EXPLORING

    def draw_shop_screen(self):
        """绘制商店界面"""
        shop = self.game.all_shops[self.game.current_shop_idx]

        # 页签按钮
        tab_x = SCREEN_WIDTH // 2 - 130

        # 获取物品列表和处理逻辑
        if self.game.shop_tab == "buy":
            goods = shop.get_all_sellable_goods()

            def handle_buy_item(item):
                if self.game.gold >= item.price:
                    self.game.gold -= item.price
                    self.game.player.add_item_to_inventory(item)
                    self.game.add_message(f"购买了 {item.name}。")
                else:
                    self.game.add_message("金币不足！")

            self._draw_generic_list_menu(
                f"{shop.name} (金币: {self.game.gold})",
                goods,
                handle_buy_item,
                GameState.EXPLORING,
                self.game.item_page_shop, "item_page_shop", self.game.items_per_page,
                item_price_func=lambda item: item.price
            )

            if self.draw_button("出售", tab_x + 160, 60, 100, 30,
                            BTN_ORANGE if self.game.shop_tab == "sell" else BTN_RED,
                            BTN_ORANGE_HOVER if self.game.shop_tab == "sell" else BTN_RED_HOVER):
                if self.game.clicked_this_frame:
                    self.game.shop_tab = "sell"

        elif self.game.shop_tab == "sell":
            sellable = [item for item in self.game.player.inventory]
            sell_price = lambda item: item.price // 2 if hasattr(item, "price") else 1

            def handle_sell_item(item):
                price = sell_price(item)
                self.game.gold += price
                self.game.player.remove_item_from_inventory(item)
                self.game.add_message(f"售出 {item.name}，获得 {price} 金币。")

            self._draw_generic_list_menu(
                f"出售物品 (金币: {self.game.gold})",
                sellable,
                handle_sell_item,
                GameState.EXPLORING,
                self.game.item_page_shop, "item_page_shop", self.game.items_per_page,
                item_price_func=sell_price
            )

            if self.draw_button("购买", tab_x - 20, 60, 100, 30,
                            BTN_GREEN if self.game.shop_tab == "buy" else BTN_ORANGE,
                            BTN_GREEN_HOVER if self.game.shop_tab == "buy" else BTN_ORANGE_HOVER):
                if self.game.clicked_this_frame:
                    self.game.shop_tab = "buy"

    def draw_inventory(self):
        """绘制物品栏界面"""
        def handle_item_use_from_inv(item_obj):
            self._handle_item_use(item_obj)

        back_state = GameState.BATTLE if self.game.current_enemy and self.game.state != GameState.EXPLORING else GameState.EXPLORING
        self._draw_generic_list_menu(
                "物品栏",
                self.game.player.inventory,
                handle_item_use_from_inv,
                back_state,
                self.game.item_page_inv,
                "item_page_inv",
                self.game.items_per_page
            )

    def _handle_item_use(self, item_obj):
        """统一处理物品使用逻辑"""
        if isinstance(item_obj, Equipment):
            _, msg = self.game.player.equip(item_obj)
            self.game.add_message(msg)
            return

        target = (
            self.game.current_enemy
            if self.game.state == GameState.BATTLE and item_obj.target == "enemy"
            else self.game.player
        )
        success, message = self.game.use_item(item_obj, target)
        if not success:
            return

        if self.game.state == GameState.INVENTORY:
            self.game.state = GameState.EXPLORING

        # 若当前页为空则自动回退一页
        inv = self.game.player.inventory
        if len(inv) <= self.game.item_page_inv * self.game.items_per_page and self.game.item_page_inv > 0:
            self.game.item_page_inv -= 1

    def draw_character_info_screen(self):
        """绘制角色信息界面"""
        screen.fill(BG_DARK)
        self.draw_text("角色信息", FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

        self._draw_character_stats()
        self._draw_equipment_info()
        self._draw_skill_list()

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 40, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.EXPLORING

    # ===================== 私有辅助方法_始 =====================

    def _draw_character_stats(self):
        """绘制玩家基本信息"""
        y = 80
        x = 50
        p = self.game.player
        info = [
            f"名字: {p.name}",
            f"等级: {p.level}",
            f"经验: {p.exp} / {p.exp_to_next_level}",
            f"金币: {self.game.gold}",
            f"生命值: {p.hp} / {p.max_hp}",
            f"法力值: {p.mp} / {p.max_mp}",
            f"攻击力: {p.attack} (基础: {p.base_attack})",
            f"防御力: {p.defense} (基础: {p.base_defense})"
        ]
        colors = [
            TEXT_LIGHT, SHIRONEZUMI, SHIRONEZUMI, BTN_ORANGE,
            BTN_GREEN, BTN_BLUE, SHIRONEZUMI, SHIRONEZUMI
        ]

        for line, color in zip(info, colors):
            self.draw_text(line, FONT_MEDIUM, color, x, y)
            y += 35 if "金币" not in line else 50

    def _draw_equipment_info(self):
        """绘制当前装备信息"""
        y = 80
        x = 400
        self.draw_text("当前装备:", FONT_MEDIUM, TEXT_LIGHT, x, y)
        y += 35

        slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
        for slot, item in self.game.player.equipment.items():
            name = item.name if item else "无"
            label = slot_name_map.get(slot, slot)
            self.draw_text(f"{label}: {name}", FONT_SMALL, TEXT_FAINT, x, y)
            y += 25

    def _draw_skill_list(self):
        """绘制技能列表"""
        y = 260
        x = 400
        self.draw_text("技能列表：", FONT_MEDIUM, TEXT_LIGHT, x, y)
        y += 35

        for skill in self.game.player.skills[1:7]:
            self.draw_text(f"- {skill.name} (MP: {skill.mp_cost})", FONT_SMALL, BTN_CYAN, x, y)
            self.draw_text(
                f"  {skill.description}",
                FONT_SMALL,
                TEXT_FAINT,
                x + 10,
                y + 20,
                max_width=SCREEN_WIDTH - x - 20
            )
            y += 45
            if y > SCREEN_HEIGHT - 100:
                break

    # ===================== 私有辅助方法_终 =====================

    def draw_battle(self):
        screen.fill(BG_DARK if self.game.current_enemy else KURO)
        if self.game.player:
            self.draw_player_status_bar(10, 10, SCREEN_WIDTH // 2 - 20, 120)
        if self.game.current_enemy:
            self.draw_enemy_status_panel()

        self.draw_message_log(10, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 20, 150)

        turn_text = "你的回合！" if self.game.battle_turn == "player" else f"{self.game.current_enemy.name} 的回合..."
        self.draw_text(turn_text, FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 160, "center")

        if self.game.battle_turn == "player" and self.game.player.is_alive():
            self.draw_player_actions_panel()

    def draw_enemy_status_panel(self):
        enemy = self.game.current_enemy
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120)
        pygame.draw.rect(screen, LIGHT_PANEL, panel_rect)
        pygame.draw.rect(screen, TEXT_LIGHT, panel_rect, 1)

        self.draw_text(f"{enemy.name} | Lv.{enemy.level}", FONT_MEDIUM, TEXT_LIGHT, panel_rect.x + 10, 20)
        self.draw_text(f"HP: {enemy.hp}/{enemy.max_hp}", FONT_SMALL,
                       BTN_GREEN if enemy.hp > enemy.max_hp * 0.3 else BTN_RED_DARK, panel_rect.x + 10, 50)
        self.draw_text(f"MP: {enemy.mp}/{enemy.max_mp}", FONT_SMALL, BTN_BLUE, panel_rect.x + 160, 50)
        self.draw_text(f"ATK: {enemy.attack} DEF: {enemy.defense}", FONT_SMALL, TEXT_FAINT, panel_rect.x + 10, 75)

        # 显示敌人状态效果（最多2个）
        y_offset = 100
        for effect in enemy.status_effects[:2]:
            self.draw_text(f"{effect.name}({effect.turns_remaining})", FONT_SMALL, BTN_PURPLE, panel_rect.x + 10, y_offset)
            y_offset += 15

    def draw_player_actions_panel(self):
        skill_x, skill_y = 20, SCREEN_HEIGHT - 300
        self.draw_text("技能:", FONT_MEDIUM, TEXT_LIGHT, skill_x + 75, skill_y - 25, "center")
        self.draw_skill_buttons(skill_x, skill_y)
        self.draw_action_buttons(SCREEN_WIDTH - 220, skill_y)

    def draw_skill_buttons(self, x, y):
        filtered_skills = self.game.player.skills[1:]
        skills_per_page = 3
        start = self.game.scroll_offset_skills * skills_per_page
        visible_skills = filtered_skills[start:start + skills_per_page]

        for i, skill in enumerate(visible_skills):
            true_idx = self.game.player.skills.index(skill)
            label = f"{skill.name}" + (f"-MP:{skill.mp_cost}" if skill.mp_cost else '')
            enough_mp = self.game.player.mp >= skill.mp_cost
            btn_color = BTN_CYAN if enough_mp else SHEN_LAN_SE
            hover_color = BTN_CYAN_HOVER if enough_mp else SHEN_LAN_SE
            font_color = KURO if enough_mp else TEXT_FAINT

            if self.draw_button(label, x, y + i * 45, 200, 40, btn_color, hover_color, font_color):
                if self.game.clicked_this_frame and enough_mp:
                    self.game.player_action(skill_idx=true_idx)
                    self.show_item_popup = False

        total_pages = (len(filtered_skills) - 1) // skills_per_page + 1
        if total_pages > 1:
            if self.game.scroll_offset_skills > 0 and self.draw_button("↑", x + 125, y - 35, 28, 28, BTN_BLUE, BTN_BLUE_HOVER):
                if self.game.clicked_this_frame:
                    self.game.scroll_offset_skills -= 1
            if self.game.scroll_offset_skills < total_pages - 1 and self.draw_button("↓", x + 160, y - 35, 28, 28, BTN_BLUE, BTN_BLUE_HOVER):
                if self.game.clicked_this_frame:
                    self.game.scroll_offset_skills += 1

    def draw_action_buttons(self, x, y):
        if self.draw_button("攻击", x, y, 200, 40, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame:
                self.game.player_action(skill_idx=0)
                self.show_item_popup = False

        if self.draw_button("物品", x, y + 45, 200, 40,
                            BTN_ORANGE if not self.show_item_popup else SHEN_ZONG_SE,
                            BTN_ORANGE_HOVER if not self.show_item_popup else SHEN_ZONG_SE,
                            KURO if not self.show_item_popup else TEXT_FAINT):
            if self.game.clicked_this_frame:
                self.show_item_popup = True

        if self.draw_button("逃跑", x, y + 90, 200, 40, BTN_GREEN, BTN_GREEN_HOVER):
            if self.game.clicked_this_frame:
                self.game.attempt_escape_battle()
                self.show_item_popup = False

        if self.show_item_popup:
            self.draw_item_popup()

    def draw_item_popup(self):
        popup_rect = pygame.Rect(250, 200, 400, 300)
        pygame.draw.rect(screen, ONE_DARK, popup_rect)
        pygame.draw.rect(screen, TEXT_FAINT, popup_rect, 1)

        items_to_display = [item for item in self.game.player.inventory if isinstance(item, Item)]
        merged_items = self.merge_similar_items(items_to_display)

        if not merged_items:
            self.draw_text("空空如也。", FONT_MEDIUM, TEXT_LIGHT, popup_rect.centerx, popup_rect.centery, "center")
        else:
            def popup_callback(item, idx, x, y):
                label = f"{item.name} x{getattr(item, '_quantity', 1)}"
                if self.draw_button(label, x, y, 160, 28, BTN_ORANGE, BTN_ORANGE_DARK, KURO, FONT_SMALL):
                    if self.game.clicked_this_frame:
                        real_idx = next((i for i, it in enumerate(self.game.player.inventory) if it.name == item.name), None)
                        if real_idx is not None:
                            self.game.player_action(item_idx=real_idx)
                            self.show_item_popup = False

            self._draw_multicolumn(
                items=merged_items,
                fixed='rows',
                count=7,
                start_x=popup_rect.left + 30,
                start_y=popup_rect.top + 20,
                x_offset=180,
                y_offset=34,
                callback=popup_callback
                )

        if self.draw_button("返回", popup_rect.centerx - 25, popup_rect.bottom - 34, 50, 24, BTN_RED, BTN_RED_HOVER, KURO, FONT_SMALL):
            if self.game.clicked_this_frame:
                self.show_item_popup = False
