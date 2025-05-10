import pygame
import sys
from collections import defaultdict

from constants import GameState
from data import Equipment
from colors import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class GameUI:
    def __init__(self, game):
        self.game = game

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
        if self.draw_button("清除", x + width - clear_btn_w - 18, y + height - clear_btn_h - 12,
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
        self.draw_text(f"HP: {self.game.player.hp}/{self.game.player.max_hp}", FONT_SMALL, BTN_GREEN if self.game.player.hp > self.game.player.max_hp * 0.3 else BTN_RED, x + 10, y + 40)
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

    def draw_exploring(self):
        screen.fill(BG_DARK)
        current_loc = self.game.get_current_location()

        # 玩家状态栏
        self.draw_player_status_bar(10, 10, 320, 120)

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
        if self.draw_button("装备", button_x_start, button_y, button_width, button_height, BTN_BLUE, BTN_BLUE_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.EQUIPMENT_SCREEN
                self.game.scroll_offset_equipment = 0

        button_y += button_height + button_spacing
        if self.draw_button("角色信息", button_x_start, button_y, button_width, button_height, BTN_ORANGE, BTN_ORANGE_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = GameState.CHARACTER_INFO

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
            if self.draw_button("休息-20G", button_x_start, button_y, button_width, button_height, BTN_PURPLE, BTN_PURPLE_HOVER):
                if self.game.clicked_this_frame:
                    if self.game.gold >= 20:
                        self.game.gold -= 20
                        self.game.rest_at_location()
                    else:
                        self.game.add_message("金币不足，无法休息。")

        # TODO 跳转按钮有小的显示问题
        # 地点跳转按钮
        loc_btn_y_start = 180
        loc_btn_x = SCREEN_WIDTH - button_width - 30
        self.draw_text("前往:", FONT_MEDIUM, TEXT_LIGHT, loc_btn_x + button_width // 2, loc_btn_y_start - 25, "center")
        for i, loc_data in enumerate(self.game.all_locations):
            if i != self.game.current_location_idx:
                if self.draw_button(loc_data["name"], loc_btn_x, loc_btn_y_start, button_width, 35, BTN_GRAY, BTN_GRAY_LIGHT, KURO, FONT_SMALL):
                    if self.game.clicked_this_frame:
                        self.game.change_location(i)
                loc_btn_y_start += 35 + 10

    def _draw_generic_list_menu(self, title, items_to_display, item_handler_func, back_state, current_page, scroll_offset_attr_name, items_per_page=5, item_price_func=None, item_desc_func=None):
        screen.fill(BG_DARK)
        self.draw_text(title, FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

        # --- 合并相似物品（根据 item.name 分组） ---
        grouped_items = defaultdict(list)
        for item in items_to_display:
            grouped_items[item.name].append(item)

        # 将合并后的条目转为列表
        merged_items = []
        for name, group in grouped_items.items():
            rep_item = group[0]  # 使用第一个作为代表
            rep_item._quantity = len(group)  # 附加数量属性
            merged_items.append(rep_item)

        # --- 分页 ---
        start_idx = current_page * (items_per_page * 2)  # 每页两列
        end_idx = start_idx + (items_per_page * 2)
        visible_items = merged_items[start_idx:end_idx]

        if not merged_items:
            self.draw_text("空空如也。", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 120, "center")
        else:
            # 多列布局
            col_x = [60, SCREEN_WIDTH // 2 + 20]
            col_width = SCREEN_WIDTH // 2 - 100
            button_height = 44
            v_spacing = 76
            base_y = 100

            for i, item in enumerate(visible_items):
                col = i % 2
                row = i // 2
                x = col_x[col]
                y = base_y + row * v_spacing

                # 显示物品名 + 数量 + 价格
                item_count = getattr(item, '_quantity', 1)
                item_text = f"{item.name} x{item_count}" if item_count > 1 else f"{item.name}"
                if item_price_func:
                    item_text += f" ({item_price_func(item)}G)"

                if self.draw_button(item_text, x, y, col_width, button_height, BTN_GREEN, BTN_GREEN_HOVER, KURO, FONT_MEDIUM):
                    if self.game.clicked_this_frame:
                        item_handler_func(item)

                # 描述文字显示在按钮下方
                desc = item_desc_func(item) if item_desc_func else getattr(item, 'description', None)
                if desc:
                    self.draw_text(desc, FONT_SMALL, TEXT_FAINT, x + 6, y + button_height + 2, max_width=col_width - 12)

        # 分页导航
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

        # 返回按钮
        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 34, BTN_RED, BTN_RED_HOVER):
            if self.game.clicked_this_frame:
                self.game.state = back_state
                if scroll_offset_attr_name == "item_page_inv":
                    self.game.item_page_inv = 0
                elif scroll_offset_attr_name == "item_page_shop":
                    self.game.item_page_shop = 0

    def draw_battle_reward_screen(self):
        # 战斗胜利奖励界面
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

    def draw_game_over(self):
        # 游戏结束界面
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

        # 显示角色当前装备
        for slot, item in self.game.player.equipment.items():
            slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
            text = f"{slot_name_map.get(slot, slot)}: {item.name if item else '无'}"
            self.draw_text(text, FONT_SMALL, BTN_CYAN, 50, y + 40)

            if item:
                if self.draw_button("卸下", 200, y + 35, 50, 28, BTN_RED, BTN_RED_HOVER, KURO, FONT_SMALL):
                    if self.game.clicked_this_frame:
                        _, msg = self.game.player.unequip(slot)
                        self.game.add_message(msg)
            y += 37

        self.draw_player_status_bar(SCREEN_WIDTH - 330, 10, 320, 120)

        # --- 合并可装备物品 ---
        equippable = [it for it in self.game.player.inventory if isinstance(it, Equipment)]
        grouped = defaultdict(list)
        for item in equippable:
            grouped[item.name].append(item)

        merged_items = []
        for name, group in grouped.items():
            rep = group[0]
            rep._quantity = len(group)
            merged_items.append(rep)

        # --- 多列显示 ---
        y_offset = y + 60
        items_per_col = 3  # 每列 3 个按钮
        items_per_page = items_per_col * 2  # 每页两列
        page = self.game.scroll_offset_equipment
        start = page * items_per_page
        end = start + items_per_page
        visible_items = merged_items[start:end]

        if not visible_items:
            self.draw_text("没有可装备的物品。", FONT_MEDIUM, TEXT_FAINT, SCREEN_WIDTH // 2, y_offset + 30, "center")
        else:
            col_x = [60, SCREEN_WIDTH // 2 + 20]
            col_width = SCREEN_WIDTH // 2 - 100
            button_height = 44
            v_spacing = 76

            for i, item in enumerate(visible_items):
                col = i % 2
                row = i // 2
                x = col_x[col]
                y_pos = y_offset + row * v_spacing

                count = getattr(item, '_quantity', 1)
                btn_text = f"{item.name} x{count}" if count > 1 else item.name

                # 装备面板框
                pygame.draw.rect(screen, LIGHT_PANEL, (x, y_pos, col_width, button_height))
                pygame.draw.rect(screen, TEXT_LIGHT, (x, y_pos, col_width, button_height), 1)
                self.draw_text(btn_text, FONT_MEDIUM, TEXT_LIGHT, x + 20, y_pos + 5, max_width=col_width)

                # 装备按钮
                if self.draw_button("装备", x + col_width - 60, y_pos + button_height // 2 - 14, 50, 28, BTN_PURPLE, BTN_PURPLE_HOVER, KURO, FONT_SMALL):
                    if self.game.clicked_this_frame:
                        _, msg = self.game.player.equip(item)
                        self.game.add_message(msg)
                        if len(merged_items) <= self.game.scroll_offset_equipment * items_per_page and self.game.scroll_offset_equipment > 0:
                            self.game.scroll_offset_equipment -= 1

                # 描述信息
                if getattr(item, "description", None):
                    self.draw_text(item.description, FONT_SMALL, TEXT_FAINT, x + 6, y_pos + button_height + 2, max_width=col_width - 12)

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
