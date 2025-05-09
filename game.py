import pygame
import sys
import random
from pygame.locals import *
from collections import defaultdict

from data import Shop
from character import StatusEffect, Character, Enemy
from colors import *
from constants import *

# 初始化 pygame
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG 文字冒险游戏")

class RPGGame:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.player = None
        self.current_enemy = None
        self.current_location_idx = 0
        self.current_shop_idx = None

        self.gold = 0
        self.battle_turn = "player"
        self.shop_tab = "buy"
        self.dialogue_text = []
        self.dialogue_index = 0
        self.message_log = []
        self.scroll_offset_message_log = 0
        self.log_max_lines = 7

        self.scroll_offset_inventory = 0
        self.scroll_offset_shop = 0
        self.scroll_offset_skills = 0
        self.scroll_offset_equipment = 0
        self.item_page_inv = 0
        self.item_page_shop = 0
        self.items_per_page = 5

        self.battle_rewards = {"exp": 0, "gold": 0, "items": []}

        self.all_skills = []
        self.all_items = []
        self.all_equipments = []
        self.all_enemies_templates = []
        self.all_locations = []
        self.all_shops = []

        self.load_game_data()
        self.setup_initial_player_conditions()

    def setup_initial_player_conditions(self):
         # This will be called by start_new_game
        pass

    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 100:
            self.message_log.pop(0)
        self.scroll_offset_message_log = max(0, len(self.message_log))

    def load_game_data(self):
        self.all_skills = ALL_SKILLS
        self.all_items = ALL_ITEMS
        self.all_equipments = ALL_EQUIPMENTS

        enemy_skills_map = {s.name: s for s in self.all_skills}
        self.all_enemies_templates = [
            Enemy("史莱姆", 30, 10, 8, 2, 1, 15, 10,
                  [enemy_skills_map["普通攻击"]],
                  [{"item_obj": self.all_items[0], "chance": 0.3}]),
            Enemy("哥布林", 50, 15, 12, 4, 2, 25, 18,
                  [enemy_skills_map["普通攻击"], enemy_skills_map["强力一击"]],
                  [{"item_obj": self.all_items[0], "chance": 0.2}, {"item_obj": self.all_equipments[0], "chance": 0.05}]),
            Enemy("野狼", 70, 0, 15, 5, 3, 30, 22,
                  [enemy_skills_map["普通攻击"]],
                  [{"item_obj": self.all_items[2], "chance": 0.1}]),
            Enemy("强盗", 100, 20, 18, 7, 5, 50, 40,
                  [enemy_skills_map["普通攻击"], enemy_skills_map["强力一击"], enemy_skills_map["破甲击"]],
                  [{"item_obj": self.all_items[1], "chance": 0.2}, {"item_obj": self.all_equipments[4], "chance": 0.08}]),
            Enemy("森林妖精", 80, 50, 15, 10, 6, 60, 50,
                  [enemy_skills_map["普通攻击"], enemy_skills_map["火球术"], enemy_skills_map["治疗术"]],
                  [{"item_obj": self.all_items[3], "chance": 0.15}]),
            Enemy("石巨人", 250, 0, 30, 20, 10, 150, 100,
                  [enemy_skills_map["普通攻击"], enemy_skills_map["强力一击"]],
                  [{"item_obj": self.all_equipments[5], "chance": 0.1}]),
        ]

        self.all_shops = [
            Shop("新手村道具店", items_for_sale=[self.all_items[0], self.all_items[2], self.all_items[4]], 
                               equipments_for_sale=[self.all_equipments[0], self.all_equipments[1]]),
            Shop("森林驿站补给点", items_for_sale=[self.all_items[1], self.all_items[3], self.all_items[5], self.all_items[7]],
                                 equipments_for_sale=[self.all_equipments[4], self.all_equipments[5], self.all_equipments[6], self.all_equipments[7]])
        ]

        self.all_locations = ALL_LOCATIONS

    def start_new_game(self):
        self.player = Character("冒险者", 100, 100, 30, 30, 10, 5, level=1, exp=0, game_skills_ref=self.all_skills)
        self.player.skills.append(self.all_skills[0]) # 普通攻击
        self.player.skills.append(self.all_skills[1]) # 强力一击

        self.player.add_item_to_inventory(self.all_items[0], quantity=3)
        self.player.add_item_to_inventory(self.all_items[2], quantity=1)

        start_weapon = self.all_equipments[0] #新手剑
        self.player.add_item_to_inventory(start_weapon)
        msg_equip = self.player.equip(start_weapon)[1]

        self.gold = 100
        self.current_location_idx = 0
        self.message_log = ["欢迎来到 RPG 文字冒险游戏!", msg_equip, "你的旅程从这里开始。"]
        self.state = GameState.EXPLORING
        self.scroll_offset_inventory = 0
        self.scroll_offset_shop = 0
        self.item_page_inv = 0
        self.item_page_shop = 0

    def get_current_location(self):
        return self.all_locations[self.current_location_idx]

    def start_battle(self):
        loc_data = self.get_current_location()
        if not loc_data["enemies"]:
            self.add_message("这里似乎很安全，没有敌人。")
            return

        template = self.all_enemies_templates[random.choice(loc_data["enemies"])]
        self.current_enemy = Enemy(
            name=template.name,
            hp=template.base_max_hp,
            mp=template.base_max_mp,
            attack=template.base_attack,
            defense=template.base_defense,
            level=template.level,
            exp_reward=template.exp_reward,
            gold_reward=template.gold_reward,
            skills_refs=list(template.skills),
            drop_table=[d.copy() for d in template.drop_table]
        )
        self.add_message(f"遭遇敌人: {self.current_enemy.name} (等级 {self.current_enemy.level})!")
        self.state = GameState.BATTLE
        self.battle_turn = "player"
        self.battle_rewards = {"exp": 0, "gold": 0, "items": []}

    def _create_status_effect(self, skill, caster=None):
        name = skill.status_effect_name or skill.name
        effect_type = {
            "燃烧": "damage_over_time",
            "破甲": "defense_debuff",
            "冰冻": "attack_debuff"
        }.get(name, "attack_debuff" if "攻击" in skill.name else "defense_debuff")

        value = skill.effect_value or int(caster.attack * 0.2) if caster else 5
        return StatusEffect(name, effect_type, value, skill.effect_duration, f"{name}效果")

    def _apply_skill_effect(self, caster, target, skill):
        messages = []

        if caster.mp < skill.mp_cost:
            return [f"{caster.name} 法力不足，无法使用 {skill.name}!"], False

        caster.use_mp(skill.mp_cost)
        messages.append(f"{caster.name} 使用了 {skill.name}!")

        # 主效果应用
        if skill.skill_type == "damage":
            damage = int(caster.attack * skill.damage_multiplier)
            actual = target.take_damage(damage)
            messages.append(f"{target.name} 受到 {actual} 点伤害。")

        elif skill.skill_type == "heal":
            healed = caster.heal(skill.effect_value)
            messages.append(f"{caster.name} 恢复了 {healed} 点生命。")

        elif skill.skill_type == "buff_self":
            effect = self._create_status_effect(skill)
            caster.add_status_effect(effect)
            messages.append(f"{caster.name} 获得了 {effect.name} 效果！")

        elif skill.skill_type == "debuff_enemy":
            effect = self._create_status_effect(skill)
            target.add_status_effect(effect)
            messages.append(f"{target.name} 受到 {effect.name} 效果！")

        elif skill.skill_type == "lifesteal":
            damage = int(caster.attack * skill.damage_multiplier)
            dealt = target.take_damage(damage)
            healed = caster.heal(int(dealt * skill.effect_value))
            messages.append(f"{target.name} 受到 {dealt} 点伤害，{caster.name} 吸取了 {healed} 点生命！")

        # 附加状态效果（如燃烧）
        if skill.status_effect_name and skill.skill_type in ("damage", "debuff_enemy"):
            effect = self._create_status_effect(skill, caster)
            target.add_status_effect(effect)
            messages.append(f"{target.name} 陷入了 {effect.name} 状态！")

        return messages, True

    def player_action(self, skill_idx=None, item_idx=None):
        if self.state != GameState.BATTLE or self.battle_turn != "player":
            return

        if skill_idx is not None and 0 <= skill_idx < len(self.player.skills):
            skill = self.player.skills[skill_idx]
            msgs, success = self._apply_skill_effect(self.player, self.current_enemy, skill)
            for m in msgs: self.add_message(m)
            if success:
                if not self.current_enemy.is_alive():
                    self.battle_victory()
                else:
                    self.end_player_turn_in_battle()
            return

        elif item_idx is not None:
            self.add_message("物品使用逻辑在战斗中应通过物品菜单触发。")
            return

        self.add_message("无效的技能选择。")

    def end_player_turn_in_battle(self):
        if self.state == GameState.BATTLE:
            self.battle_turn = "enemy"

    def enemy_action(self):
        if self.state != GameState.BATTLE or self.battle_turn != "enemy":
            return
        if not self.current_enemy or not self.current_enemy.is_alive():
            return

        for msg in self.current_enemy.update_status_effects_at_turn_start():
            self.add_message(msg)

        if not self.current_enemy.is_alive():
            self.battle_victory()
            return

        skill = self.current_enemy.choose_action(self.player)
        msgs, _ = self._apply_skill_effect(self.current_enemy, self.player, skill)
        for m in msgs: self.add_message(m)

        if not self.player.is_alive():
            self.game_over()
        else:
            self.battle_turn = "player"
            for msg in self.player.update_status_effects_at_turn_start():
                self.add_message(msg)
            if not self.player.is_alive():
                self.game_over()

    def battle_victory(self):
        self.add_message(f"你击败了 {self.current_enemy.name}！")

        exp_reward = self.current_enemy.exp_reward
        gold_reward = self.current_enemy.gold_reward

        self.battle_rewards["exp"] = exp_reward
        self.battle_rewards["gold"] = gold_reward
        self.battle_rewards["items"] = []

        for drop_info in self.current_enemy.drop_table:
            if random.random() < drop_info["chance"]:
                dropped_item = drop_info["item_obj"]
                self.battle_rewards["items"].append(dropped_item)

        self.state = GameState.BATTLE_REWARD

    def display_battle_rewards(self):
        rewards = self.battle_rewards
        msgs = []

        if rewards["exp"]:
            leveled_up, times, level_up_infos = self.player.gain_exp(rewards["exp"])
            msgs.append(f"获得了 {rewards['exp']} 经验值。")
            if leveled_up:
                for i, info in enumerate(level_up_infos):
                    msgs.append(f"恭喜！你升到了 {self.player.level - len(level_up_infos) + i + 1} 级！")
                    msgs.append(f"  生命上限 +{info['hp_increase']}, 法力上限 +{info['mp_increase']}")
                    msgs.append(f"  攻击 +{info['attack_increase']}, 防御 +{info['defense_increase']}")
                    msgs.extend([f"  学会了新技能: {s}!" for s in info["learned_skills"]])

        if rewards["gold"]:
            self.gold += rewards["gold"]
            msgs.append(f"获得了 {rewards['gold']} 金币。")

        for item in rewards["items"]:
            self.player.add_item_to_inventory(item)
            msgs.append(f"获得了物品: {item.name}!")

        for msg in msgs:
            self.add_message(msg)

    def process_battle_rewards(self):
        self.display_battle_rewards()
        self.current_enemy = None
        self.state = GameState.EXPLORING

    def game_over(self):
        self.add_message("你被击败了！冒险结束...")
        self.state = GameState.GAME_OVER

    def get_item_target(self, item, explicit_target=None):
        if item.target == "self" or explicit_target == self.player:
            return self.player
        elif item.target == "enemy" and self.state == GameState.BATTLE:
            return self.current_enemy
        return None

    def apply_item_effect(self, item, target):
        messages = []
        used = False

        effect_type = item.item_type
        val = item.effect_value

        if effect_type == "heal_hp":
            healed = target.heal(val)
            messages.append(f"{target.name} 恢复了 {healed} 点生命值！")
            used = True
        elif effect_type == "heal_mp":
            restored = target.restore_mp(val)
            messages.append(f"{target.name} 恢复了 {restored} 点法力值！")
            used = True
        elif effect_type in ("buff_attack", "buff_defense"):
            status = StatusEffect(f"{item.name}效果", 
                                  "attack_buff" if "attack" in effect_type else "defense_buff", 
                                  val, item.duration, item.description)
            target.add_status_effect(status)
            messages.append(f"{target.name} 的{item.name}效果已激活！")
            used = True
        elif effect_type == "damage_enemy" and target == self.current_enemy:
            damage = target.take_damage(val)
            messages.append(f"{target.name} 受到 {damage} 点伤害！")
            used = True

        return used, messages

    # TODO 战斗时使用物品还是有问题
    def use_item(self, item, target=None):
        if not item: return False, "无效物品。"

        target_char = self.get_item_target(item, target)
        if not target_char:
            return False, f"无法对目标使用 {item.name}。"

        self.add_message(f"{self.player.name} 使用了 {item.name} 在 {target_char.name} 身上。")

        used, effect_msgs = self.apply_item_effect(item, target_char)

        if used:
            if item in self.player.inventory:
                self.player.inventory.remove(item)
            for msg in effect_msgs:
                self.add_message(msg)
            return True, ""
        return False, f"无法使用 {item.name}。"


    def change_location(self, new_location_idx):
        if 0 <= new_location_idx < len(self.all_locations):
            self.current_location_idx = new_location_idx
            loc = self.get_current_location()
            self.add_message(f"你来到了 {loc['name']}。")
            self.add_message(loc['description'])

            self.item_page_inv = 0
            self.scroll_offset_inventory = 0

            if loc["enemies"] and random.random() < 0.3:
                self.start_battle()
        else:
            self.add_message("无效的地点。")

    def attempt_escape_battle(self):
        if self.state != GameState.BATTLE:
            return
        if random.random() < 0.75:
            self.add_message("你成功逃离了战斗！")
            self.state = GameState.EXPLORING
            self.current_enemy = None
        else:
            self.add_message("逃跑失败！")
            self.end_player_turn_in_battle()

    def rest_at_location(self):
        loc = self.get_current_location()
        if loc.get("can_rest"):
            self.player.hp = self.player.max_hp
            self.player.mp = self.player.max_mp
            self.add_message("你休息了一下，完全恢复了状态！")
        else:
            self.add_message("这里无法休息。")

    def mouse_in_rect(self, x, y, width, height):
        mx, my = pygame.mouse.get_pos()
        return x <= mx <= x + width and y <= my <= y + height

    # --- 文字绘制函数 ---
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
        total_lines = len(self.message_log)

        # 限制滑动范围
        max_offset = max(0, total_lines - max_lines)
        self.scroll_offset_message_log = max(0, min(self.scroll_offset_message_log, max_offset))

        # 取出当前要显示的日志行
        start_idx = self.scroll_offset_message_log
        end_idx = min(total_lines, start_idx + max_lines)
        log_to_display = self.message_log[start_idx:end_idx]

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
            if self.clicked_this_frame:
                self.message_log.clear()
                self.scroll_offset_message_log = 0

        # --- 滑动条 ---
        if total_lines > max_lines:
            scrollbar_width = 10
            bar_x = x + width - scrollbar_width - 4
            bar_y = y + padding
            bar_height = height - 2 * padding
            scroll_ratio = max_lines / total_lines
            scroll_bar_h = max(int(bar_height * scroll_ratio), 20)
            scroll_bar_y = bar_y + int((self.scroll_offset_message_log / max_offset) * (bar_height - scroll_bar_h))

            pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, scrollbar_width, bar_height))  # 背景槽
            pygame.draw.rect(screen, (180, 180, 180), (bar_x, scroll_bar_y, scrollbar_width, scroll_bar_h))  # 滑块

            # 鼠标滚轮事件
            if self.mouse_in_rect(x, y, width, height):
                if self.scroll_up:
                    self.scroll_offset_message_log = max(0, self.scroll_offset_message_log - 1)
                elif self.scroll_down:
                    self.scroll_offset_message_log = min(max_offset, self.scroll_offset_message_log + 1)

    def draw_player_status_bar(self, x, y, width, height):
        pygame.draw.rect(screen, LIGHT_PANEL, (x, y, width, height))
        pygame.draw.rect(screen, TEXT_LIGHT, (x, y, width, height), 1)

        self.draw_text(f"{self.player.name} | Lvl: {self.player.level}", FONT_MEDIUM, TEXT_LIGHT, x + 10, y + 10)
        self.draw_text(f"HP: {self.player.hp}/{self.player.max_hp}", FONT_SMALL, BTN_GREEN if self.player.hp > self.player.max_hp * 0.3 else BTN_RED, x + 10, y + 40)
        self.draw_text(f"MP: {self.player.mp}/{self.player.max_mp}", FONT_SMALL, BTN_BLUE, x + 170, y + 40)
        self.draw_text(f"ATK: {self.player.attack} DEF: {self.player.defense}", FONT_SMALL, TEXT_FAINT, x + 10, y + 65)
        self.draw_text(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", FONT_SMALL, BTN_PURPLE, x + 170, y + 65)
        self.draw_text(f"金币: {self.gold}", FONT_SMALL, BTN_ORANGE, x + 170, y + 90)

        for effect in self.player.status_effects[:2]:
            self.draw_text(f"{effect.name}({effect.turns_remaining})", FONT_SMALL, BTN_PURPLE, x + 10, y + 90)

    def draw_main_menu(self):
        screen.fill(BG_DARK)
        self.draw_text("RPG 文字冒险游戏", FONT_TITLE, SHIRONERI, SCREEN_WIDTH//2, 150, "center")

        if self.draw_button("开始新游戏", SCREEN_WIDTH//2 - 100, 300, 200, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame: self.start_new_game()
        # Add Load Game Button if implemented
        if self.draw_button("退出游戏", SCREEN_WIDTH//2 - 100, 380, 200, 50, BTN_RED, BTN_RED_HOVER):
            if self.clicked_this_frame: pygame.quit(); sys.exit()

    def draw_exploring(self):
        screen.fill(BG_DARK)
        current_loc = self.get_current_location()

        # 玩家状态栏
        self.draw_player_status_bar(10, 10, 300, 120)

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
            if self.clicked_this_frame:
                if current_loc["enemies"]:
                    self.start_battle()
                else:
                    self.add_message("这里很安全，你四处看了看，没什么发现。")

        button_y += button_height + button_spacing
        if self.draw_button("物品栏", button_x_start, button_y, button_width, button_height, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame:
                self.state = GameState.INVENTORY
                self.item_page_inv = 0
                self.scroll_offset_inventory = 0

        button_y += button_height + button_spacing
        if self.draw_button("装备", button_x_start, button_y, button_width, button_height, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame:
                self.state = GameState.EQUIPMENT_SCREEN
                self.scroll_offset_equipment = 0

        button_y += button_height + button_spacing
        if self.draw_button("角色信息", button_x_start, button_y, button_width, button_height, BTN_ORANGE, BTN_ORANGE_HOVER):
            if self.clicked_this_frame:
                self.state = GameState.CHARACTER_INFO

        if current_loc.get("shop_idx") is not None:
            button_y += button_height + button_spacing
            if self.draw_button("进入商店", button_x_start, button_y, button_width, button_height, BTN_ORANGE, BTN_ORANGE_HOVER):
                if self.clicked_this_frame:
                    self.current_shop_idx = current_loc["shop_idx"]
                    self.state = GameState.SHOP
                    self.item_page_shop = 0
                    self.scroll_offset_shop = 0

        if current_loc.get("can_rest", False):
            button_y += button_height + button_spacing
            if self.draw_button("休息-20G", button_x_start, button_y, button_width, button_height, BTN_PURPLE, BTN_PURPLE_HOVER):
                if self.clicked_this_frame:
                    if self.gold >= 20:
                        self.gold -= 20
                        self.rest_at_location()
                    else:
                        self.add_message("金币不足，无法休息。")

        # TODO 跳转按钮有小的显示问题
        # 地点跳转按钮
        loc_btn_y_start = 180
        loc_btn_x = SCREEN_WIDTH - button_width - 30
        self.draw_text("前往:", FONT_MEDIUM, TEXT_LIGHT, loc_btn_x + button_width // 2, loc_btn_y_start - 25, "center")
        for i, loc_data in enumerate(self.all_locations):
            if i != self.current_location_idx:
                if self.draw_button(loc_data["name"], loc_btn_x, loc_btn_y_start, button_width, 35, BTN_GRAY, BTN_GRAY_LIGHT, KURO, FONT_SMALL):
                    if self.clicked_this_frame:
                        self.change_location(i)
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
                    if self.clicked_this_frame:
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
                    if self.clicked_this_frame:
                        setattr(self, scroll_offset_attr_name, current_page - 1)
            if current_page < total_pages - 1:
                if self.draw_button("下一页", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 130, 100, 38, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.clicked_this_frame:
                        setattr(self, scroll_offset_attr_name, current_page + 1)

        # 返回按钮
        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 34, BTN_RED, BTN_RED_HOVER):
            if self.clicked_this_frame:
                self.state = back_state
                if scroll_offset_attr_name == "item_page_inv":
                    self.item_page_inv = 0
                elif scroll_offset_attr_name == "item_page_shop":
                    self.item_page_shop = 0

    def draw_inventory(self):
        """
        绘制物品栏界面，根据当前游戏状态决定使用逻辑
        """

        def handle_item_use_from_inv(item_obj):
            """
            使用物品时的处理逻辑（根据战斗状态与目标判断）
            """
            # 目标选择：默认对玩家使用，若为敌方目标则切换
            target = self.current_enemy if self.state == GameState.BATTLE and item_obj.target == "enemy" else self.player

            success, message = self.use_item(item_obj, target)

            if not success:
                return

            # === 状态逻辑切换 ===
            if self.state == GameState.INVENTORY:
                self.state = GameState.EXPLORING  # 从物品栏回归探索模式
            elif self.state == GameState.BATTLE:
                if not self.current_enemy.is_alive():
                    self.battle_victory()
                elif not self.player.is_alive():
                    self.game_over()
                else:
                    self.end_player_turn_in_battle()

            # 若物品数量减少，页数也应回退
            if len(self.player.inventory) <= self.item_page_inv * self.items_per_page and self.item_page_inv > 0:
                self.item_page_inv -= 1

        # 返回状态设定：若当前敌人存在且非探索状态，则退回战斗界面，否则探索界面
        back_state = GameState.BATTLE if self.current_enemy and self.state != GameState.EXPLORING else GameState.EXPLORING
        # 绘制物品栏（统一 UI 面板调用）
        self._draw_generic_list_menu("物品栏", self.player.inventory, handle_item_use_from_inv, back_state, self.item_page_inv, "item_page_inv", self.items_per_page)

    def draw_battle(self):
        # 根据是否有敌人决定背景颜色
        screen.fill(BG_DARK if self.current_enemy else KURO)

        # 玩家状态面板
        if self.player:
            self.draw_player_status_bar(10, 10, SCREEN_WIDTH // 2 - 20, 120)

        # 敌人状态面板
        if self.current_enemy:
            pygame.draw.rect(screen, LIGHT_PANEL, (SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120))
            pygame.draw.rect(screen, TEXT_LIGHT, (SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120), 1)

            self.draw_text(f"{self.current_enemy.name} | Lv.{self.current_enemy.level}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2 + 20, 20)
            self.draw_text(f"HP: {self.current_enemy.hp}/{self.current_enemy.max_hp}", FONT_SMALL,
                           BTN_GREEN if self.current_enemy.hp > self.current_enemy.max_hp * 0.3 else BTN_RED,
                           SCREEN_WIDTH // 2 + 20, 50)
            self.draw_text(f"MP: {self.current_enemy.mp}/{self.current_enemy.max_mp}", FONT_SMALL, BTN_BLUE, SCREEN_WIDTH // 2 + 170, 50)
            self.draw_text(f"ATK: {self.current_enemy.attack} DEF: {self.current_enemy.defense}", FONT_SMALL, TEXT_FAINT, SCREEN_WIDTH // 2 + 20, 75)

            # 显示敌人状态效果（最多2个）
            y_offset = 100
            for effect in self.current_enemy.status_effects[:2]:
                self.draw_text(f"{effect.name}({effect.turns_remaining})", FONT_SMALL, BTN_PURPLE, SCREEN_WIDTH // 2 + 20, y_offset)
                y_offset += 15

        # 消息日志区域
        self.draw_message_log(10, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 20, 150)

        # 回合指示
        turn_text = "你的回合！" if self.battle_turn == "player" else f"{self.current_enemy.name} 的回合..."
        self.draw_text(turn_text, FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 160, "center")

        # 玩家行动区域（仅限玩家回合）
        if self.battle_turn == "player" and self.player.is_alive():
            skill_x, skill_y = 20, SCREEN_HEIGHT - 300
            self.draw_text("技能:", FONT_MEDIUM, TEXT_LIGHT, skill_x + 75, skill_y - 25, "center")

            # 技能分页逻辑
            skills_per_page = 3
            start = self.scroll_offset_skills * skills_per_page
            visible_skills = self.player.skills[start:start + skills_per_page]

            for i, skill in enumerate(visible_skills):
                idx = start + i
                label = f"{skill.name}" + (f"-MP:{skill.mp_cost}" if skill.mp_cost else '')
                btn_color = BTN_CYAN if self.player.mp >= skill.mp_cost else LIGHT_PANEL
                hover_color = BTN_CYAN_HOVER if btn_color == BTN_CYAN else LIGHT_PANEL

                if self.draw_button(label, skill_x, skill_y + i * 45, 200, 40, btn_color, hover_color):
                    if self.clicked_this_frame and self.player.mp >= skill.mp_cost:
                        self.player_action(skill_idx=idx)

            # 技能翻页按钮
            total_pages = (len(self.player.skills) - 1) // skills_per_page + 1
            if total_pages > 1:
                if self.scroll_offset_skills > 0:
                    if self.draw_button("↑", skill_x + 210, skill_y, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills -= 1
                if self.scroll_offset_skills < total_pages - 1:
                    if self.draw_button("↓", skill_x + 210, skill_y + 45, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills += 1

            # 其他行动（物品、逃跑）
            action_x = SCREEN_WIDTH - 220
            if self.draw_button("物品", action_x, skill_y, 200, 40, BTN_ORANGE, BTN_ORANGE_HOVER):
                if self.clicked_this_frame:
                    self.state = GameState.INVENTORY

            if self.draw_button("攻击", action_x, skill_y + 45, 200, 40, BTN_RED, BTN_RED_HOVER):
                if self.clicked_this_frame:
                    self.player_action(skill_idx=0)

            if self.draw_button("逃跑", action_x, skill_y + 90, 200, 40, BTN_GREEN, BTN_GREEN_HOVER):
                if self.clicked_this_frame:
                    self.attempt_escape_battle()

    def draw_battle_reward_screen(self):
        # 战斗胜利奖励界面
        screen.fill(BG_DARK)
        self.draw_text("战斗胜利！", FONT_LARGE, BTN_ORANGE, SCREEN_WIDTH // 2, 100, "center")

        y = 180
        self.draw_text(f"获得经验: {self.battle_rewards['exp']}", FONT_MEDIUM, SHIRONEZUMI, SCREEN_WIDTH // 2, y, "center")
        y += 40
        self.draw_text(f"获得金币: {self.battle_rewards['gold']}", FONT_MEDIUM, BTN_ORANGE, SCREEN_WIDTH // 2, y, "center")
        y += 40

        if self.battle_rewards['items']:
            self.draw_text("获得物品:", FONT_MEDIUM, SHIRONEZUMI, SCREEN_WIDTH // 2, y, "center")
            y += 30
            for item in self.battle_rewards['items']:
                self.draw_text(f"- {item.name}", FONT_SMALL, BTN_CYAN, SCREEN_WIDTH // 2, y, "center")
                y += 25

        if self.draw_button("继续", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame:
                self.process_battle_rewards()

    def draw_game_over(self):
        # 游戏结束界面
        screen.fill(SUMI)
        self.draw_text("游戏结束", FONT_LARGE, BTN_RED, SCREEN_WIDTH // 2, 200, "center")
        if self.player:
            self.draw_text(f"你 {self.player.name} 倒下了。", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 250, "center")
            self.draw_text(f"最终等级: {self.player.level}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 280, "center")

        if self.draw_button("返回主菜单", SCREEN_WIDTH // 2 - 100, 400, 200, 50, BTN_GRAY, BTN_GRAY_LIGHT):
            if self.clicked_this_frame:
                self.state = GameState.MAIN_MENU

    def draw_shop_screen(self):
        """绘制商店界面"""
        shop = self.all_shops[self.current_shop_idx]

        # 页签按钮
        tab_x = SCREEN_WIDTH // 2 - 130

        # 获取物品列表和处理逻辑
        if self.shop_tab == "buy":
            goods = shop.get_all_sellable_goods()

            def handle_buy_item(item):
                if self.gold >= item.price:
                    self.gold -= item.price
                    self.player.add_item_to_inventory(item)
                    self.add_message(f"购买了 {item.name}。")
                else:
                    self.add_message("金币不足！")

            self._draw_generic_list_menu(
                f"{shop.name} (金币: {self.gold})",
                goods,
                handle_buy_item,
                GameState.EXPLORING,
                self.item_page_shop, "item_page_shop", self.items_per_page,
                item_price_func=lambda item: item.price
            )

            if self.draw_button("出售", tab_x + 160, 60, 100, 30,
                            BTN_ORANGE if self.shop_tab == "sell" else BTN_RED,
                            BTN_ORANGE_HOVER if self.shop_tab == "sell" else BTN_RED_HOVER):
                if self.clicked_this_frame:
                    self.shop_tab = "sell"

        elif self.shop_tab == "sell":
            sellable = [item for item in self.player.inventory]
            sell_price = lambda item: item.price // 2 if hasattr(item, "price") else 1

            def handle_sell_item(item):
                price = sell_price(item)
                self.gold += price
                self.player.remove_item_from_inventory(item)
                self.add_message(f"售出 {item.name}，获得 {price} 金币。")

            self._draw_generic_list_menu(
                f"出售物品 (金币: {self.gold})",
                sellable,
                handle_sell_item,
                GameState.EXPLORING,
                self.item_page_shop, "item_page_shop", self.items_per_page,
                item_price_func=sell_price
            )

            if self.draw_button("购买", tab_x - 20, 60, 100, 30,
                            BTN_GREEN if self.shop_tab == "buy" else BTN_ORANGE,
                            BTN_GREEN_HOVER if self.shop_tab == "buy" else BTN_ORANGE_HOVER):
                if self.clicked_this_frame:
                    self.shop_tab = "buy"

    # TODO 合并相似物品，多列显示
    def draw_equipment_screen(self):
        """绘制装备界面"""
        screen.fill(BG_DARK)
        self.draw_text("装备栏", FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

        y = 80
        self.draw_text("当前装备：", FONT_MEDIUM, TEXT_LIGHT, 150, y, "center")

        # 显示角色当前装备
        for slot, item in self.player.equipment.items():
            slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
            text = f"{slot_name_map.get(slot, slot)}: {item.name if item else '无'}"
            self.draw_text(text, FONT_SMALL, BTN_CYAN, 50, y + 40)

            if item:
                if self.draw_button("卸下", 250, y + 35, 70, 30, BTN_RED, BTN_RED_HOVER, KURO, FONT_SMALL):
                    if self.clicked_this_frame:
                        _, msg = self.player.unequip(slot)
                        self.add_message(msg)
            y += 35

        # 显示物品栏中的可装备物品
        equippable = [it for it in self.player.inventory if isinstance(it, Equipment)]
        y += 80
        start = self.scroll_offset_equipment * self.items_per_page
        end = start + self.items_per_page
        visible = equippable[start:end]

        for i, item in enumerate(visible):
            if self.draw_button(item.name, 50, y + i * 45, 240, 40, BTN_GREEN, BTN_GREEN_HOVER):
                if self.clicked_this_frame:
                    _, msg = self.player.equip(item)
                    self.add_message(msg)
                    if len(equippable) <= self.scroll_offset_equipment * self.items_per_page and self.scroll_offset_equipment > 0:
                        self.scroll_offset_equipment -= 1

        # 分页按钮
        total_pages = (len(equippable) - 1) // self.items_per_page + 1
        if total_pages > 1:
            self.draw_text(f"页: {self.scroll_offset_equipment + 1}/{total_pages}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 80, "center")
            if self.scroll_offset_equipment > 0:
                if self.draw_button("上", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40, 40, 30, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.clicked_this_frame: self.scroll_offset_equipment -= 1
            if self.scroll_offset_equipment < total_pages - 1:
                if self.draw_button("下", SCREEN_WIDTH - 90, SCREEN_HEIGHT - 40, 40, 30, BTN_BLUE, BTN_BLUE_HOVER):
                    if self.clicked_this_frame: self.scroll_offset_equipment += 1

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 40, 150, 30, BTN_RED, BTN_RED_HOVER):
            if self.clicked_this_frame: self.state = GameState.EXPLORING

    def draw_character_info_screen(self):
        """绘制角色信息界面"""
        screen.fill(BG_DARK)
        self.draw_text("角色信息", FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")
        if not self.player:
            return

        y = 80
        x1, x2 = 50, 400

        info = [
            f"名字: {self.player.name}",
            f"等级: {self.player.level}",
            f"经验: {self.player.exp} / {self.player.exp_to_next_level}",
            f"金币: {self.gold}",
            f"生命值: {self.player.hp} / {self.player.max_hp}",
            f"法力值: {self.player.mp} / {self.player.max_mp}",
            f"攻击力: {self.player.attack} (基础: {self.player.base_attack})",
            f"防御力: {self.player.defense} (基础: {self.player.base_defense})"
        ]
        colors = [TEXT_LIGHT, TEXT_LIGHT, TEXT_LIGHT, BTN_ORANGE, BTN_GREEN, BTN_BLUE, TEXT_LIGHT, TEXT_LIGHT]

        for line, color in zip(info, colors):
            self.draw_text(line, FONT_MEDIUM, color, x1, y)
            y += 35 if "金币" not in line else 50

        y = 80
        self.draw_text("当前装备:", FONT_MEDIUM, TEXT_LIGHT, x2, y)
        y += 35
        slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
        for slot, item in self.player.equipment.items():
            name = item.name if item else "无"
            self.draw_text(f"{slot_name_map.get(slot, slot)}: {name}", FONT_SMALL, TEXT_FAINT, x2, y)
            y += 25

        y += 20
        self.draw_text("技能列表：", FONT_MEDIUM, TEXT_LIGHT, x2, y)
        y += 35
        for skill in self.player.skills[:6]:
            self.draw_text(f"- {skill.name} (MP: {skill.mp_cost})", FONT_SMALL, BTN_CYAN, x2, y)
            self.draw_text(f"  {skill.description}", FONT_SMALL, TEXT_FAINT, x2 + 10, y + 20, max_width=SCREEN_WIDTH - x2 - 20)
            y += 45
            if y > SCREEN_HEIGHT - 100:
                break

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 40, BTN_RED, BTN_RED_HOVER):
            if self.clicked_this_frame: self.state = GameState.EXPLORING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.clicked_this_frame = True
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_up = event.y > 0
                self.scroll_down = event.y < 0
            elif event.type == KEYDOWN:
                self.handle_keydown(event.key)

    def handle_keydown(self, key):
        if self.state == GameState.EXPLORING:
            if key == K_i: self.state = GameState.INVENTORY; self.item_page_inv = 0
            if key == K_e: self.state = GameState.EQUIPMENT_SCREEN; self.scroll_offset_equipment = 0
            if key == K_c: self.state = GameState.CHARACTER_INFO
        elif self.state in {GameState.INVENTORY, GameState.EQUIPMENT_SCREEN, GameState.CHARACTER_INFO, GameState.SHOP}:
            if key == K_ESCAPE:
                self.state = GameState.BATTLE if self.current_enemy else GameState.EXPLORING
        elif self.state == GameState.BATTLE and self.battle_turn == "player":
            if key in (K_1, K_2):
                idx = key - K_1
                if idx < len(self.player.skills):
                    self.player_action(skill_idx=idx)
            elif key == K_i:
                self.state = GameState.INVENTORY

    def run(self):
        clock = pygame.time.Clock()
        running = True
        enemy_action_timer = 0
        enemy_action_delay = 1200

        while running:
            self.clicked_this_frame = False
            self.scroll_up = False
            self.scroll_down = False

            self.handle_events()

            screen.fill(KURO)
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.EXPLORING:
                self.draw_exploring()
            elif self.state == GameState.BATTLE:
                self.draw_battle()
                if self.battle_turn == "enemy" and self.current_enemy and self.current_enemy.is_alive() and self.player.is_alive():
                    now = pygame.time.get_ticks()
                    if not enemy_action_timer:
                        enemy_action_timer = now
                    elif now - enemy_action_timer >= enemy_action_delay:
                        self.enemy_action()
                        enemy_action_timer = 0
            elif self.state == GameState.INVENTORY:
                self.draw_inventory()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.BATTLE_REWARD:
                self.draw_battle_reward_screen()
            elif self.state == GameState.SHOP:
                self.draw_shop_screen()
            elif self.state == GameState.EQUIPMENT_SCREEN:
                self.draw_equipment_screen()
            elif self.state == GameState.CHARACTER_INFO:
                self.draw_character_info_screen()

            pygame.display.flip()
            clock.tick(30)

def main():
    game = RPGGame()
    game.run()

if __name__ == "__main__":
    main()
