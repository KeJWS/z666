import pygame
import sys
import random
from pygame.locals import *

from data import Shop
from character import StatusEffect, Character, Enemy
from game_ui import GameUI, screen
from colors import *
from constants import *

# 初始化 pygame
pygame.init()
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

        self.ui = GameUI(self)

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

        self.all_locations = ALL_LOCATIONS
        self.all_shops = ALL_SHOPS

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

    def draw_inventory(self):
        """
        绘制物品栏界面，根据当前游戏状态决定使用逻辑
        """

        def handle_item_use_from_inv(item_obj):
            """
            使用物品时的处理逻辑（根据战斗状态与目标判断）
            """
            if isinstance(item_obj, Equipment):
                _, msg = self.player.equip(item_obj)
                self.add_message(msg)
                return

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
        self.ui._draw_generic_list_menu("物品栏", self.player.inventory, handle_item_use_from_inv, back_state, self.item_page_inv, "item_page_inv", self.items_per_page)

    def draw_battle(self):
        # 根据是否有敌人决定背景颜色
        screen.fill(BG_DARK if self.current_enemy else KURO)

        # 玩家状态面板
        if self.player:
            self.ui.draw_player_status_bar(10, 10, SCREEN_WIDTH // 2 - 20, 120)

        # 敌人状态面板
        if self.current_enemy:
            pygame.draw.rect(screen, LIGHT_PANEL, (SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120))
            pygame.draw.rect(screen, TEXT_LIGHT, (SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120), 1)

            self.ui.draw_text(f"{self.current_enemy.name} | Lv.{self.current_enemy.level}", FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2 + 20, 20)
            self.ui.draw_text(f"HP: {self.current_enemy.hp}/{self.current_enemy.max_hp}", FONT_SMALL,
                           BTN_GREEN if self.current_enemy.hp > self.current_enemy.max_hp * 0.3 else BTN_RED,
                           SCREEN_WIDTH // 2 + 20, 50)
            self.ui.draw_text(f"MP: {self.current_enemy.mp}/{self.current_enemy.max_mp}", FONT_SMALL, BTN_BLUE, SCREEN_WIDTH // 2 + 170, 50)
            self.ui.draw_text(f"ATK: {self.current_enemy.attack} DEF: {self.current_enemy.defense}", FONT_SMALL, TEXT_FAINT, SCREEN_WIDTH // 2 + 20, 75)

            # 显示敌人状态效果（最多2个）
            y_offset = 100
            for effect in self.current_enemy.status_effects[:2]:
                self.ui.draw_text(f"{effect.name}({effect.turns_remaining})", FONT_SMALL, BTN_PURPLE, SCREEN_WIDTH // 2 + 20, y_offset)
                y_offset += 15

        # 消息日志区域
        self.ui.draw_message_log(10, SCREEN_HEIGHT - 160, SCREEN_WIDTH - 20, 150)

        # 回合指示
        turn_text = "你的回合！" if self.battle_turn == "player" else f"{self.current_enemy.name} 的回合..."
        self.ui.draw_text(turn_text, FONT_MEDIUM, TEXT_LIGHT, SCREEN_WIDTH // 2, 160, "center")

        # 玩家行动区域（仅限玩家回合）
        if self.battle_turn == "player" and self.player.is_alive():
            skill_x, skill_y = 20, SCREEN_HEIGHT - 300
            self.ui.draw_text("技能:", FONT_MEDIUM, TEXT_LIGHT, skill_x + 75, skill_y - 25, "center")

            # 技能分页逻辑
            skills_per_page = 3
            start = self.scroll_offset_skills * skills_per_page
            visible_skills = self.player.skills[start:start + skills_per_page]

            for i, skill in enumerate(visible_skills):
                idx = start + i
                label = f"{skill.name}" + (f"-MP:{skill.mp_cost}" if skill.mp_cost else '')
                btn_color = BTN_CYAN if self.player.mp >= skill.mp_cost else LIGHT_PANEL
                hover_color = BTN_CYAN_HOVER if btn_color == BTN_CYAN else LIGHT_PANEL

                if self.ui.draw_button(label, skill_x, skill_y + i * 45, 200, 40, btn_color, hover_color):
                    if self.clicked_this_frame and self.player.mp >= skill.mp_cost:
                        self.player_action(skill_idx=idx)

            # 技能翻页按钮
            total_pages = (len(self.player.skills) - 1) // skills_per_page + 1
            if total_pages > 1:
                if self.scroll_offset_skills > 0:
                    if self.ui.draw_button("↑", skill_x + 210, skill_y, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills -= 1
                if self.scroll_offset_skills < total_pages - 1:
                    if self.ui.draw_button("↓", skill_x + 210, skill_y + 45, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills += 1

            # 其他行动（物品、逃跑）
            action_x = SCREEN_WIDTH - 220
            if self.ui.draw_button("物品", action_x, skill_y, 200, 40, BTN_ORANGE, BTN_ORANGE_HOVER):
                if self.clicked_this_frame:
                    self.state = GameState.INVENTORY

            if self.ui.draw_button("攻击", action_x, skill_y + 45, 200, 40, BTN_RED, BTN_RED_HOVER):
                if self.clicked_this_frame:
                    self.player_action(skill_idx=0)

            if self.ui.draw_button("逃跑", action_x, skill_y + 90, 200, 40, BTN_GREEN, BTN_GREEN_HOVER):
                if self.clicked_this_frame:
                    self.attempt_escape_battle()

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

            self.ui._draw_generic_list_menu(
                f"{shop.name} (金币: {self.gold})",
                goods,
                handle_buy_item,
                GameState.EXPLORING,
                self.item_page_shop, "item_page_shop", self.items_per_page,
                item_price_func=lambda item: item.price
            )

            if self.ui.draw_button("出售", tab_x + 160, 60, 100, 30,
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

            self.ui._draw_generic_list_menu(
                f"出售物品 (金币: {self.gold})",
                sellable,
                handle_sell_item,
                GameState.EXPLORING,
                self.item_page_shop, "item_page_shop", self.items_per_page,
                item_price_func=sell_price
            )

            if self.ui.draw_button("购买", tab_x - 20, 60, 100, 30,
                            BTN_GREEN if self.shop_tab == "buy" else BTN_ORANGE,
                            BTN_GREEN_HOVER if self.shop_tab == "buy" else BTN_ORANGE_HOVER):
                if self.clicked_this_frame:
                    self.shop_tab = "buy"

    def draw_character_info_screen(self):
        """绘制角色信息界面"""
        screen.fill(BG_DARK)
        self.ui.draw_text("角色信息", FONT_LARGE, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")
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
        colors = [TEXT_LIGHT, SHIRONEZUMI, SHIRONEZUMI, BTN_ORANGE, BTN_GREEN, BTN_BLUE, SHIRONEZUMI, SHIRONEZUMI]

        for line, color in zip(info, colors):
            self.ui.draw_text(line, FONT_MEDIUM, color, x1, y)
            y += 35 if "金币" not in line else 50

        y = 80
        self.ui.draw_text("当前装备:", FONT_MEDIUM, TEXT_LIGHT, x2, y)
        y += 35
        slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
        for slot, item in self.player.equipment.items():
            name = item.name if item else "无"
            self.ui.draw_text(f"{slot_name_map.get(slot, slot)}: {name}", FONT_SMALL, TEXT_FAINT, x2, y)
            y += 25

        y += 20
        self.ui.draw_text("技能列表：", FONT_MEDIUM, TEXT_LIGHT, x2, y)
        y += 35
        for skill in self.player.skills[:6]:
            self.ui.draw_text(f"- {skill.name} (MP: {skill.mp_cost})", FONT_SMALL, BTN_CYAN, x2, y)
            self.ui.draw_text(f"  {skill.description}", FONT_SMALL, TEXT_FAINT, x2 + 10, y + 20, max_width=SCREEN_WIDTH - x2 - 20)
            y += 45
            if y > SCREEN_HEIGHT - 100:
                break

        if self.ui.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 40, BTN_RED, BTN_RED_HOVER):
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
                self.ui.draw_main_menu()
            elif self.state == GameState.EXPLORING:
                self.ui.draw_exploring()
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
                self.ui.draw_game_over()
            elif self.state == GameState.BATTLE_REWARD:
                self.ui.draw_battle_reward_screen()
            elif self.state == GameState.SHOP:
                self.draw_shop_screen()
            elif self.state == GameState.EQUIPMENT_SCREEN:
                self.ui.draw_equipment_screen()
            elif self.state == GameState.CHARACTER_INFO:
                self.draw_character_info_screen()

            pygame.display.flip()
            clock.tick(30)

def main():
    game = RPGGame()
    game.run()

if __name__ == "__main__":
    main()
