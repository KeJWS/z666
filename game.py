import debug

import pygame
import sys
import random
from pygame.locals import *

import constants as cs
from character import StatusEffect, Character
from game_ui import GameUI, screen
from colors import *
from constants import GameState

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
        self.message_log = []
        self.scroll_offset_message_log = 0

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
        self.all_locations = []
        self.all_shops = []

        self.load_game_data()
        self.setup_initial_player_conditions()

        self.ui = GameUI(self)

    def setup_initial_player_conditions(self):
        # This will be called by start_new_game
        self.current_enemy = None
        pass

    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 100:
            self.message_log.pop(0)
        self.scroll_offset_message_log = max(0, len(self.message_log))

    def load_game_data(self):
        self.all_skills = cs.ALL_SKILLS
        self.all_items = cs.ALL_ITEMS
        self.all_equipments = cs.ALL_EQUIPMENTS
        self.enemy_map = cs.game_data["enemy_map"]
        self.all_locations = cs.ALL_LOCATIONS
        self.all_shops = cs.ALL_SHOPS

    def start_new_game(self):
        self.setup_initial_player_conditions()

        self.player = Character("冒险者", 100, 30, 10, 5, level=1, exp=0, game_skills_ref=self.all_skills)
        self.player.skills.extend(self.all_skills[:2])  # 添加普通攻击与强力一击

        # 初始物品与装备
        for item, qty in [(self.all_items[0], 3), (self.all_items[2], 1)]:
            self.player.add_item_to_inventory(item, quantity=qty)
        start_weapon = self.all_equipments[0]
        self.player.add_item_to_inventory(start_weapon)
        msg_equip = self.player.equip(start_weapon)[1]

        self.gold = 100
        self.current_location_idx = 0
        self.message_log = ["欢迎来到 RPG 文字冒险游戏!", msg_equip, "你的旅程从这里开始。"]
        self.state = GameState.EXPLORING

        # 滚动偏移初始化
        self.scroll_offset_inventory = self.scroll_offset_shop = 0
        self.item_page_inv = self.item_page_shop = 0

        if debug.DEBUG:
            self.gold += 9000
            self.player.skills.extend(cs.game_data["skills"][2:])
            for item in cs.game_data["items"]:
                self.player.add_item_to_inventory(item)
            for equip in cs.game_data["equipments"]:
                self.player.add_item_to_inventory(equip)

    def get_current_location(self):
        return self.all_locations[self.current_location_idx]

    def start_battle(self):
        loc_data = self.get_current_location()
        if not loc_data["enemies"]:
            self.add_message("这里似乎很安全，没有敌人。")
            return

        enemy_name = random.choice(loc_data["enemies"])
        self.current_enemy = self.enemy_map[enemy_name].clone()
        enemy = self.current_enemy

        self.add_message(f"遭遇敌人: {enemy.name} (等级 {enemy.level})!")
        self._enemy_try_equip(enemy)

        self.state = GameState.BATTLE
        self.battle_turn = "player"
        self.battle_rewards = {"exp": 0, "gold": 0, "items": []}

    def _enemy_try_equip(self, enemy):
        for entry in getattr(enemy, "potential_equips", []):
            if random.random() < entry.get("chance", 0.2):
                equip = entry["equip_obj"]
                enemy.equip(equip)
                enemy.gold_reward += equip.price
                enemy.exp_reward += 25 * enemy.level
                enemy.hp = enemy.max_hp
                enemy.mp = enemy.max_mp
                self.add_message(f"{enemy.name} 装备了 {equip.name}！")

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

        # 技能类型处理
        if skill.skill_type in {"damage", "lifesteal"}:
            damage = int(caster.attack * skill.damage_multiplier)
            dealt = target.take_damage(damage)
            messages.append(f"{target.name} 受到 {dealt} 点伤害。")
            if skill.skill_type == "lifesteal":
                healed = caster.heal(int(dealt * skill.effect_value))
                messages.append(f"{caster.name} 吸取了 {healed} 点生命！")

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

        if item_idx is not None and 0 <= item_idx < len(self.player.inventory):
            item = self.player.inventory[item_idx]
            success, _ = self.use_item(item, self.player)
            if success:
                self.show_item_popup = False
                if not self.current_enemy.is_alive():
                    self.battle_victory()
                else:
                    self.end_player_turn_in_battle()
            return

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
            status = StatusEffect(f"{item.name}", 
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

            if loc["enemies"] and random.random() < 0.15:
                self.start_battle()

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
            self.player.status_effects = []
            self.add_message("你休息了一下，完全恢复了状态！")

    def mouse_in_rect(self, x, y, width, height):
        mx, my = pygame.mouse.get_pos()
        return x <= mx <= x + width and y <= my <= y + height

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

    def run(self):
        clock = pygame.time.Clock()
        running = True
        enemy_action_timer = 0
        enemy_action_delay = 1000

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
                self.ui.draw_battle()
                if self.battle_turn == "enemy" and self.current_enemy and self.current_enemy.is_alive() and self.player.is_alive():
                    now = pygame.time.get_ticks()
                    if not enemy_action_timer:
                        enemy_action_timer = now
                    elif now - enemy_action_timer >= enemy_action_delay:
                        self.enemy_action()
                        enemy_action_timer = 0
            elif self.state == GameState.INVENTORY:
                self.ui.draw_inventory()
            elif self.state == GameState.GAME_OVER:
                self.ui.draw_game_over()
            elif self.state == GameState.BATTLE_REWARD:
                self.ui.draw_battle_reward_screen()
            elif self.state == GameState.SHOP:
                self.ui.draw_shop_screen()
            elif self.state == GameState.EQUIPMENT_SCREEN:
                self.ui.draw_equipment_screen()
            elif self.state == GameState.CHARACTER_INFO:
                self.ui.draw_character_info_screen()

            pygame.display.flip()
            clock.tick(30)

def main():
    game = RPGGame()
    game.run()

if __name__ == "__main__":
    main()
