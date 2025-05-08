import pygame
import sys
import random
import math
from pygame.locals import *
from collections import defaultdict

# 初始化 pygame
pygame.init()
pygame.font.init()

# 通用颜色定义
KURO           = (8, 8, 8) # 黑
SUMI           = (28, 28, 28) # 墨
SHIRONEZUMI    = (189, 192, 186) # 白鼠
SHIRONERI      = (252, 250, 242) # 白練

TEXT_LIGHT     = (235, 235, 245)        # 亮文字，用于标题或高对比文字
TEXT_FAINT     = (180, 180, 200)        # 次级文字，用于描述或注释
LIGHT_PANEL    = (56, 60, 72)           # 面板背景色（深灰 One Dark）
BG_DARK        = (40, 44, 52)           # 主背景色

SCREEN_WIDTH, SCREEN_HEIGHT = 960, 720

GRAY, LIGHT_GRAY = (150, 150, 150), (200, 200, 200)
RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
GOLD, PURPLE = (255, 215, 0), (128, 0, 128)
CYAN, BROWN, ORANGE = (0, 255, 255), (165, 42, 42), (255, 165, 0)

# 美化颜色定义
BTN_HOVER     = (86, 182, 194)

# 按钮颜色（基础/悬停）——视觉层级明确、带轻柔亮度变化
BTN_GREEN        = (152, 195, 121)
BTN_GREEN_HOVER  = (184, 218, 137)
BTN_BLUE         = (97, 175, 239)
BTN_BLUE_HOVER   = (135, 195, 255)
BTN_PURPLE       = (198, 120, 221)
BTN_PURPLE_HOVER = (225, 150, 245)
BTN_ORANGE       = (229, 192, 123)
BTN_ORANGE_HOVER = (255, 220, 150)
BTN_GRAY         = (110, 115, 125)
BTN_GRAY_LIGHT   = (165, 170, 180)
BTN_RED          = (224, 108, 117)
BTN_RED_HOVER    = (255, 135, 145)
BTN_CYAN         = (86, 182, 194)
BTN_CYAN_HOVER   = (120, 210, 220)

WHITE = (245, 245, 255)                 # 柔和白，用于高亮信息


# 创建屏幕和字体
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG 文字冒险游戏")
font_small = pygame.font.SysFont('notosansscblack', 16)
font_medium = pygame.font.SysFont('notosansscblack', 22)
font_large = pygame.font.SysFont('notosansscblack', 28)
font_title = pygame.font.SysFont('notosansscblack', 38)

# 游戏状态
class GameState:
    MAIN_MENU = 0
    EXPLORING = 1
    BATTLE = 2
    DIALOGUE = 3  # 未完全实现，可扩展
    INVENTORY = 4
    GAME_OVER = 5
    VICTORY = 6   # 未完全实现，可扩展
    SHOP = 7
    EQUIPMENT_SCREEN = 8 # Changed from EQUIPMENT
    CHARACTER_INFO = 9
    BATTLE_REWARD = 10

# 装备类
class Equipment:
    def __init__(self, name, equip_type, attack_bonus, defense_bonus, hp_bonus, mp_bonus, description, price=0):
        self.name = name
        self.equip_type = equip_type  # 'weapon', 'armor', 'helmet', 'accessory'
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus
        self.mp_bonus = mp_bonus
        self.description = description
        self.price = price

    def __str__(self):
        bonuses = [
            f"攻击+{self.attack_bonus}" if self.attack_bonus else "",
            f"防御+{self.defense_bonus}" if self.defense_bonus else "",
            f"生命+{self.hp_bonus}" if self.hp_bonus else "",
            f"法力+{self.mp_bonus}" if self.mp_bonus else ""
        ]
        bonus_str = ", ".join(filter(None, bonuses))
        return f"{self.name} ({bonus_str})" if bonus_str else self.name

# 技能类
class Skill:
    def __init__(self, name, damage_multiplier, mp_cost, description, skill_type="damage",
                 effect_value=0, required_level=1, target="enemy", status_effect=None, effect_duration=0):
        self.name = name
        self.damage_multiplier = damage_multiplier
        self.mp_cost = mp_cost
        self.description = description
        self.skill_type = skill_type  # 'damage', 'heal', 'buff_self', 等
        self.effect_value = effect_value
        self.required_level = required_level
        self.target = target  # 'enemy', 'self', 'all_enemies'
        self.status_effect_name = status_effect
        self.effect_duration = effect_duration

# 物品类
class Item:
    def __init__(self, name, item_type, effect_value, description, price=0, duration=0, target="self"):
        self.name = name
        self.item_type = item_type  # 'heal_hp', 'buff_attack', 等
        self.effect_value = effect_value
        self.description = description
        self.price = price
        self.duration = duration
        self.target = target

# 状态效果类
class StatusEffect:
    def __init__(self, name, effect_type, value, duration, description):
        self.name = name
        self.effect_type = effect_type  # 'attack_buff', 'damage_over_time', 等
        self.value = value
        self.duration = duration
        self.description = description
        self.turns_remaining = duration

    def apply_effect_on_turn(self, character):
        """应用每回合的持续效果"""
        if self.effect_type == 'damage_over_time':
            character.hp = max(0, character.hp - self.value)
            return f"{character.name} 受到 {self.name} 效果，损失 {self.value} 点生命值！"
        elif self.effect_type == 'heal_over_time':
            old_hp = character.hp
            character.heal(self.value)
            return f"{character.name} 受到 {self.name} 效果，恢复 {character.hp - old_hp} 点生命值！"
        return ""

    def tick(self):
        """减少持续回合数，返回是否应移除效果"""
        if self.duration == -1:  # 永久效果，直到被驱散
            return False
        self.turns_remaining -= 1
        return self.turns_remaining < 0

# 角色类
class Character:
    def __init__(self, name, hp, max_hp, mp, max_mp, attack, defense, level=1, exp=0, game_skills_ref=None):
        self.name = name
        self.hp = hp
        self.base_max_hp = max_hp # Store base max_hp
        self.mp = mp
        self.base_max_mp = max_mp # Store base max_mp
        self.base_attack = attack
        self.base_defense = defense
        self.level = level
        self.exp = exp
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        self.skills = []
        self.inventory = [] # List of Item objects
        self.status_effects = [] # List of StatusEffect objects
        self.equipment = {
            'weapon': None,
            'armor': None,
            'helmet': None,
            'accessory': None
        }
        self.game_skills_ref = game_skills_ref # Reference to all game skills for leveling up

    def calculate_exp_to_next_level(self):
        return int(self.level * 100 * (1 + (self.level -1) * 0.1))


    @property
    def max_hp(self):
        total_max_hp = self.base_max_hp
        for slot, item in self.equipment.items():
            if item:
                total_max_hp += item.hp_bonus
        for effect in self.status_effects:
            if effect.effect_type == 'hp_buff':
                total_max_hp += effect.value
        return total_max_hp
    
    @property
    def max_mp(self):
        total_max_mp = self.base_max_mp
        for slot, item in self.equipment.items():
            if item:
                total_max_mp += item.mp_bonus
        for effect in self.status_effects:
            if effect.effect_type == 'mp_buff':
                total_max_mp += effect.value
        return total_max_mp

    @property
    def attack(self):
        total_attack = self.base_attack
        for slot, item in self.equipment.items():
            if item:
                total_attack += item.attack_bonus
        for effect in self.status_effects:
            if effect.effect_type == 'attack_buff':
                total_attack += effect.value
            elif effect.effect_type == 'attack_debuff':
                total_attack -= effect.value
        return max(0, total_attack)

    @property
    def defense(self):
        total_defense = self.base_defense
        for slot, item in self.equipment.items():
            if item:
                total_defense += item.defense_bonus
        for effect in self.status_effects:
            if effect.effect_type == 'defense_buff':
                total_defense += effect.value
            elif effect.effect_type == 'defense_debuff':
                total_defense -= effect.value
        return max(0, total_defense)

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def use_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def restore_mp(self, amount):
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old_mp

    def is_alive(self):
        return self.hp > 0

    def gain_exp(self, exp_amount):
        if not self.is_alive(): return False # Cannot gain exp if dead (relevant for party members if implemented)
        self.exp += exp_amount
        leveled_up_times = 0
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            level_up_details = self.level_up()
            leveled_up_times +=1
            # Messages for level up are handled by the game class
        return leveled_up_times > 0, leveled_up_times

    def level_up(self):
        self.level += 1
        
        # Store old stats for comparison/message
        old_max_hp = self.base_max_hp
        old_max_mp = self.base_max_mp
        old_attack = self.base_attack
        old_defense = self.base_defense

        self.base_max_hp = int(self.base_max_hp * 1.05) + 10 + self.level
        self.base_max_mp = int(self.base_max_mp * 1.05) + 5 + self.level // 2
        self.base_attack += 2 + math.floor(self.level / 4)
        self.base_defense += 1 + math.floor(self.level / 5)

        # Restore HP/MP fully on level up
        self.hp = self.max_hp
        self.mp = self.max_mp

        self.exp_to_next_level = self.calculate_exp_to_next_level()

        learned_skills_names = []
        if self.game_skills_ref:
            for skill_template in self.game_skills_ref:
                if skill_template.required_level == self.level and skill_template not in self.skills:
                    self.skills.append(skill_template)
                    learned_skills_names.append(skill_template.name)
        
        return {
            'hp_increase': self.base_max_hp - old_max_hp,
            'mp_increase': self.base_max_mp - old_max_mp,
            'attack_increase': self.base_attack - old_attack,
            'defense_increase': self.base_defense - old_defense,
            'learned_skills': learned_skills_names
        }

    def add_status_effect(self, effect_template):
        # Check if an effect with the same name already exists
        existing_effect = next((e for e in self.status_effects if e.name == effect_template.name), None)
        if existing_effect:
            # Refresh duration if re-applied, or stack if designed to stack (not implemented here)
            existing_effect.turns_remaining = effect_template.duration
        else:
            # Create a new instance of the effect
            new_effect = StatusEffect(effect_template.name, effect_template.effect_type, effect_template.value, effect_template.duration, effect_template.description)
            self.status_effects.append(new_effect)


    def update_status_effects_at_turn_start(self):
        messages = []
        effects_to_remove = []
        for effect in self.status_effects:
            # Apply effects like DoT/HoT
            message = effect.apply_effect_on_turn(self)
            if message:
                messages.append(message)
            
            # Tick duration (unless permanent)
            if effect.duration != -1:
                if effect.tick(): # tick returns True if duration is over
                    effects_to_remove.append(effect)
                    messages.append(f"{self.name}的 {effect.name} 效果结束了。")

        self.status_effects = [e for e in self.status_effects if e not in effects_to_remove]
        
        # Ensure HP doesn't drop below 0 from DoT after effects are processed
        if self.hp <= 0 and self.is_alive(): # Check is_alive to prevent multiple death messages
            self.hp = 0
            messages.append(f"{self.name} 因状态效果倒下了！")
            # Game over logic will be handled by the main game loop checking is_alive()

        return messages

    def equip(self, equipment_item):
        if not isinstance(equipment_item, Equipment):
            return None, "这不是一件装备。"
            
        slot = equipment_item.equip_type
        old_equipment = None
        if self.equipment.get(slot):
            old_equipment = self.unequip(slot) # Unequip current item in that slot
        
        self.equipment[slot] = equipment_item
        # Remove from inventory
        if equipment_item in self.inventory: # Assuming equipment is also an item in inventory
             self.inventory.remove(equipment_item)
        
        # Update HP/MP to not exceed new max values after equip
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)

        return old_equipment, f"装备了 {equipment_item.name}。"

    def unequip(self, equip_type):
        if self.equipment.get(equip_type):
            unequipped_item = self.equipment[equip_type]
            self.equipment[equip_type] = None
            # Add back to inventory if it's a managed item
            self.add_item_to_inventory(unequipped_item) # Add a method for this for clarity
            
            # HP/MP might need adjustment if max HP/MP decreased, ensure current HP/MP <= new max HP/MP
            self.hp = min(self.hp, self.max_hp)
            self.mp = min(self.mp, self.max_mp)
            return unequipped_item, f"卸下了 {unequipped_item.name}。"
        return None, "该部位没有装备。"

    def add_item_to_inventory(self, item_to_add, quantity=1):
        # For stackable items, increase count, otherwise add new entry
        # Simplified: assumes items are not stacked in this version, just add.
        for _ in range(quantity):
            self.inventory.append(item_to_add)
        # Sort inventory for consistency (optional)
        self.inventory.sort(key=lambda x: x.name)


# 敌人类
class Enemy(Character):
    def __init__(self, name, hp, mp, attack, defense, level, exp_reward, gold_reward, skills_refs=None, drop_table=None, description=""):
        super().__init__(name, hp, hp, mp, mp, attack, defense, level) # MaxHP/MP are same as initial HP/MP
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.skills = skills_refs if skills_refs else [] # Actual Skill objects
        self.drop_table = drop_table if drop_table else [] # List of dicts: {"item_obj": Item/Equipment, "chance": 0.X}
        self.description = description # For display in a bestiary or target info

    def choose_action(self, target_player): # Pass player to make more informed decisions
        # Simple AI:
        # 1. Heal if HP < 30% and has healing skill and MP
        healing_skills = [s for s in self.skills if s.skill_type == "heal" and s.target == "self" and self.mp >= s.mp_cost]
        if self.hp < self.max_hp * 0.3 and healing_skills:
            return random.choice(healing_skills)

        # 2. Use offensive skills if MP allows (prioritize stronger skills or skills target_player is weak to - not implemented)
        offensive_skills = [s for s in self.skills if s.skill_type != "heal" and self.mp >= s.mp_cost]
        if offensive_skills and random.random() < 0.7: # 70% chance to use skill if available
            return random.choice(offensive_skills)

        # 3. Default to basic attack (assuming first skill is basic or a no-cost attack)
        basic_attack_skill = next((s for s in self.skills if s.mp_cost == 0), None)
        if basic_attack_skill:
            return basic_attack_skill
        # Fallback if no zero-cost skill defined, though enemies should have one
        # This situation should ideally be avoided by good enemy design
        return Skill("猛击", 1.0, 0, "敌人胡乱攻击", "damage")


# 商店类
class Shop:
    def __init__(self, name, items_for_sale=None, equipments_for_sale=None, sell_modifier=0.5):
        self.name = name
        self.items_for_sale = items_for_sale if items_for_sale else [] # List of Item objects
        self.equipments_for_sale = equipments_for_sale if equipments_for_sale else [] # List of Equipment objects
        self.sell_modifier = sell_modifier # Player sells items for 50% of their price

    def get_all_sellable_goods(self):
        return self.items_for_sale + self.equipments_for_sale


# 游戏类
class RPGGame:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.player = None
        self.current_enemy = None
        # self.enemies list is defined in load_game_data
        # self.locations list is defined in load_game_data
        self.current_location_idx = 0
        self.dialogue_text = []
        self.dialogue_index = 0
        self.message_log = []
        self.log_max_lines = 7 # Max lines for message log on screen
        self.gold = 0
        self.battle_turn = "player" # "player" or "enemy"
        # self.shops list is defined in load_game_data
        self.current_shop_idx = None # Index of the current shop
        
        self.scroll_offset_inventory = 0
        self.scroll_offset_shop = 0
        self.scroll_offset_skills = 0
        self.scroll_offset_equipment = 0

        self.battle_rewards = {"exp": 0, "gold": 0, "items": []}
        self.item_page_inv = 0 # For pagination in inventory/shop
        self.item_page_shop = 0
        self.items_per_page = 5

        self.all_skills = []
        self.all_items = []
        self.all_equipments = []
        self.all_enemies_templates = []
        self.all_locations = []
        self.all_shops = []

        self.message_log = []  # 消息内容列表
        self.scroll_offset_message_log = 0  # 当前滚动偏移量

        self.load_game_data()
        self.setup_initial_player_conditions()


    def setup_initial_player_conditions(self):
         # This will be called by start_new_game
        pass


    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > 100:
            self.message_log.pop(0) # 限制日志总长度

    def load_game_data(self):
        self.all_skills = ALL_SKILLS
        self.all_items = ALL_ITEMS
        self.all_equipments = ALL_EQUIPMENTS

        # 4. Define All Enemy Templates
        enemy_skills_map = {s.name: s for s in self.all_skills}
        self.all_enemies_templates = [
            Enemy("史莱姆", 30, 10, 8, 2, 1, 15, 10,
                  [enemy_skills_map["普通攻击"]],
                  [{"item_obj": self.all_items[0], "chance": 0.3}]), # Drops small healing potion
            Enemy("哥布林", 50, 15, 12, 4, 2, 25, 18,
                  [enemy_skills_map["普通攻击"], enemy_skills_map["强力一击"]],
                  [{"item_obj": self.all_items[0], "chance": 0.2}, {"item_obj": self.all_equipments[0], "chance": 0.05}]),
            Enemy("野狼", 70, 0, 15, 5, 3, 30, 22,
                  [enemy_skills_map["普通攻击"]],
                  [{"item_obj": self.all_items[2], "chance": 0.1}]), # Drops small mana potion
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

        # 5. Define All Shops
        self.all_shops = [
            Shop("新手村道具店", items_for_sale=[self.all_items[0], self.all_items[2], self.all_items[4]], 
                               equipments_for_sale=[self.all_equipments[0], self.all_equipments[1]]),
            Shop("森林驿站补给点", items_for_sale=[self.all_items[1], self.all_items[3], self.all_items[5], self.all_items[7]],
                                 equipments_for_sale=[self.all_equipments[4], self.all_equipments[5], self.all_equipments[6], self.all_equipments[7]])
        ]

        # 6. Define All Locations
        self.all_locations = ALL_LOCATIONS

    def start_new_game(self):
        self.player = Character("冒险者", 100, 100, 30, 30, 10, 5, level=1, exp=0, game_skills_ref=self.all_skills)
        self.player.skills.append(self.all_skills[0]) # Start with "普通攻击"
        self.player.skills.append(self.all_skills[1]) # Start with "强力一击"

        # Starting inventory
        self.player.add_item_to_inventory(self.all_items[0], quantity=3) # 3 small heal potions
        self.player.add_item_to_inventory(self.all_items[2], quantity=1) # 1 small mana potion

        # Starting equipment
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
        current_loc_data = self.get_current_location()
        if not current_loc_data["enemies"]:
            self.add_message("这里似乎很安全，没有敌人。")
            return

        enemy_template_idx = random.choice(current_loc_data["enemies"])
        enemy_template = self.all_enemies_templates[enemy_template_idx]

        # Create a new instance of the enemy for the battle
        self.current_enemy = Enemy(
            name=enemy_template.name,
            hp=enemy_template.base_max_hp, # Use base_max_hp for full health
            mp=enemy_template.base_max_mp,
            attack=enemy_template.base_attack,
            defense=enemy_template.base_defense,
            level=enemy_template.level,
            exp_reward=enemy_template.exp_reward,
            gold_reward=enemy_template.gold_reward,
            skills_refs=[s for s in enemy_template.skills], # Copy skills list
            drop_table=[d.copy() for d in enemy_template.drop_table] # Copy drop table
        )
        # Enemy also needs game_skills_ref if they can level up (not typical)
        # For simplicity, enemy skills are fixed.

        self.add_message(f"遭遇敌人: {self.current_enemy.name} (等级 {self.current_enemy.level})!")
        self.state = GameState.BATTLE
        self.battle_turn = "player"
        self.battle_rewards = {"exp": 0, "gold": 0, "items": []} # Reset rewards

    def _apply_skill_effect(self, caster, target, skill):
        messages = []
        
        # MP Cost
        if caster.mp < skill.mp_cost:
            messages.append(f"{caster.name} 法力不足，无法使用 {skill.name}!")
            return messages, False # Skill failed
        caster.use_mp(skill.mp_cost)
        messages.append(f"{caster.name} 使用了 {skill.name}!")

        # Apply skill based on type
        if skill.skill_type == "damage":
            damage = int(caster.attack * skill.damage_multiplier)
            actual_damage = target.take_damage(damage)
            messages.append(f"{target.name} 受到 {actual_damage} 点伤害。")
        elif skill.skill_type == "heal":
            # Assuming target is caster for heal, or specified by skill.target
            actual_healed = caster.heal(skill.effect_value) # caster or target based on skill.target
            messages.append(f"{caster.name} 恢复了 {actual_healed} 点生命。")
        elif skill.skill_type == "buff_self":
            effect = StatusEffect(skill.status_effect_name or skill.name, "attack_buff" if "攻击" in skill.name else "defense_buff", skill.effect_value, skill.effect_duration, skill.description)
            caster.add_status_effect(effect)
            messages.append(f"{caster.name} 获得了 {effect.name} 效果！")
        elif skill.skill_type == "debuff_enemy":
            effect = StatusEffect(skill.status_effect_name or skill.name, "attack_debuff" if "攻击" in skill.name else "defense_debuff", skill.effect_value, skill.effect_duration, skill.description)
            target.add_status_effect(effect) # target is enemy
            messages.append(f"{target.name} 受到 {effect.name} 效果！")
        elif skill.skill_type == "lifesteal":
            damage = int(caster.attack * skill.damage_multiplier)
            actual_damage = target.take_damage(damage)
            healed_amount = caster.heal(int(actual_damage * skill.effect_value))
            messages.append(f"{target.name} 受到 {actual_damage} 点伤害。{caster.name} 吸取了 {healed_amount} 点生命！")
        
        if skill.status_effect_name and skill.skill_type in ["damage", "debuff_enemy"]: # Apply status effects tied to damage/debuff skills
             # Determine effect type more robustly if needed
            effect_type_str = "damage_over_time" if skill.status_effect_name == "燃烧" else "defense_debuff" # Simplified
            if skill.status_effect_name == "破甲": effect_type_str = "defense_debuff"
            if skill.status_effect_name == "冰冻": effect_type_str = "attack_debuff" # Example
            
            status_val = skill.effect_value if skill.effect_value > 0 else int(caster.attack * 0.2) # Generic value for DoT if not specified
            if skill.skill_type == "debuff_enemy": status_val = skill.effect_value

            effect = StatusEffect(skill.status_effect_name, effect_type_str, status_val, skill.effect_duration, f"{skill.status_effect_name}效果")
            target.add_status_effect(effect)
            messages.append(f"{target.name} 陷入了 {skill.status_effect_name} 状态！")

        return messages, True # Skill succeeded

    def player_action(self, skill_idx=None, item_idx=None):
        if self.state != GameState.BATTLE or self.battle_turn != "player":
            return

        action_taken = False
        if skill_idx is not None:
            if 0 <= skill_idx < len(self.player.skills):
                skill_to_use = self.player.skills[skill_idx]
                
                skill_messages, success = self._apply_skill_effect(self.player, self.current_enemy, skill_to_use)
                for msg in skill_messages: self.add_message(msg)
                action_taken = success
            else:
                self.add_message("无效的技能选择。")
                return # Don't end turn if invalid selection

        elif item_idx is not None:
            # This logic will be handled by use_item, which then sets action_taken
            # For now, assume use_item is called from inventory screen which then calls end_player_turn_in_battle
            self.add_message("物品使用逻辑在战斗中应通过物品菜单触发。") # Placeholder
            return


        if action_taken:
            if not self.current_enemy.is_alive():
                self.battle_victory()
            else:
                self.end_player_turn_in_battle()


    def end_player_turn_in_battle(self):
        if self.state == GameState.BATTLE: # Ensure still in battle
            # Player's status effects tick (if they tick at end of turn)
            # For now, effects tick at start of turn.
            self.battle_turn = "enemy"


    def enemy_action(self):
        if self.state != GameState.BATTLE or self.battle_turn != "enemy" or not self.current_enemy or not self.current_enemy.is_alive():
            return

        self.add_message(f"--- {self.current_enemy.name}的回合 ---")
        
        # Enemy status effects update at start of its turn
        enemy_status_messages = self.current_enemy.update_status_effects_at_turn_start()
        for msg in enemy_status_messages: self.add_message(msg)
        
        if not self.current_enemy.is_alive(): # Check if DoT killed enemy
            self.battle_victory() # This might be abrupt, consider different flow
            return

        chosen_skill = self.current_enemy.choose_action(self.player) # AI chooses skill
        
        skill_messages, success = self._apply_skill_effect(self.current_enemy, self.player, chosen_skill)
        for msg in skill_messages: self.add_message(msg)

        if not self.player.is_alive():
            self.game_over()
        else:
            self.battle_turn = "player"
             # Player's status effects update at start of their turn
            player_status_messages = self.player.update_status_effects_at_turn_start()
            for msg in player_status_messages: self.add_message(msg)
            if not self.player.is_alive(): # Check if DoT killed player
                self.game_over()
                return
            self.add_message("--- 你的回合 ---")


    def battle_victory(self):
        self.add_message(f"你击败了 {self.current_enemy.name}！")
        
        exp_reward = self.current_enemy.exp_reward
        gold_reward = self.current_enemy.gold_reward
        
        self.battle_rewards["exp"] = exp_reward
        self.battle_rewards["gold"] = gold_reward
        self.battle_rewards["items"] = []

        # Item Drops
        for drop_info in self.current_enemy.drop_table:
            if random.random() < drop_info["chance"]:
                dropped_item = drop_info["item_obj"] # This should be an instance or a way to get one
                self.battle_rewards["items"].append(dropped_item)
                # self.player.add_item_to_inventory(dropped_item) # Add directly or show on reward screen
                # self.add_message(f"获得了物品: {dropped_item.name}!")

        self.state = GameState.BATTLE_REWARD
        # Player exp gain and gold gain will be processed after battle reward screen
        # self.current_enemy = None # Clear after rewards are processed

    def process_battle_rewards(self):
        exp_gain_msg = []
        if self.battle_rewards["exp"] > 0:
            leveled_up, times = self.player.gain_exp(self.battle_rewards["exp"])
            exp_gain_msg.append(f"获得了 {self.battle_rewards['exp']} 经验值。")
            if leveled_up:
                for _ in range(times): # Could consolidate messages if multiple level ups
                     # Level up details are complex, get them from player.level_up if needed here
                    level_up_details = self.player.level_up_details_cache # Assume level_up stores its last result
                    exp_gain_msg.append(f"恭喜！你升到了 {self.player.level} 级！")
                    exp_gain_msg.append(f"  生命上限 +{level_up_details['hp_increase']}, 法力上限 +{level_up_details['mp_increase']}")
                    exp_gain_msg.append(f"  攻击 +{level_up_details['attack_increase']}, 防御 +{level_up_details['defense_increase']}")
                    if level_up_details['learned_skills']:
                        for skill_name in level_up_details['learned_skills']:
                            exp_gain_msg.append(f"  学会了新技能: {skill_name}!")
        
        if self.battle_rewards["gold"] > 0:
            self.gold += self.battle_rewards["gold"]
            exp_gain_msg.append(f"获得了 {self.battle_rewards['gold']} 金币。")

        for item in self.battle_rewards["items"]:
            self.player.add_item_to_inventory(item)
            exp_gain_msg.append(f"获得了物品: {item.name}!")

        for msg in exp_gain_msg:
            self.add_message(msg)
        
        self.current_enemy = None # Clear current enemy
        self.state = GameState.EXPLORING


    def game_over(self):
        self.add_message("你被击败了！冒险结束...")
        self.state = GameState.GAME_OVER

    def use_item(self, item_obj_in_inventory, target=None): # Target defaults to player
        if not item_obj_in_inventory: return False, "无效物品。"
        
        item = item_obj_in_inventory # item is already the object
        
        user = self.player # Assuming player uses item on self or enemy
        messages = []
        used = False

        if item.target == "self" or target == self.player : # Default target is player
            target_char = self.player
        elif item.target == "enemy" and self.current_enemy and self.state == GameState.BATTLE:
            target_char = self.current_enemy
        else: # No valid target or context
            return False, f"无法对目标使用 {item.name}。"

        messages.append(f"{user.name} 使用了 {item.name} 在 {target_char.name} 身上。")

        if item.item_type == "heal_hp":
            healed = target_char.heal(item.effect_value)
            messages.append(f"{target_char.name} 恢复了 {healed} 点生命值！")
            used = True
        elif item.item_type == "heal_mp":
            restored = target_char.restore_mp(item.effect_value)
            messages.append(f"{target_char.name} 恢复了 {restored} 点法力值！")
            used = True
        elif item.item_type == "buff_attack" or item.item_type == "buff_defense":
            effect_type = "attack_buff" if "attack" in item.item_type else "defense_buff"
            status = StatusEffect(f"{item.name}效果", effect_type, item.effect_value, item.duration, item.description)
            target_char.add_status_effect(status)
            messages.append(f"{target_char.name} 的{item.name}效果已激活！")
            used = True
        elif item.item_type == "damage_enemy":
            if target_char == self.current_enemy:
                damage = item.effect_value # Fixed damage for items
                actual_damage = target_char.take_damage(damage)
                messages.append(f"{target_char.name} 受到 {actual_damage} 点伤害！")
                used = True
            else:
                messages.append(f"不能对友方使用 {item.name}。")
        # Add more item types: full_restore, cure_status, exp_gain etc.

        if used:
            if item in self.player.inventory: # Ensure it's actually in inventory
                self.player.inventory.remove(item)
            for msg in messages: self.add_message(msg)
            return True, "" # Success
        else:
            # for msg in messages: self.add_message(msg) # Add any specific failure messages
            return False, f"无法使用 {item.name}。"


    def change_location(self, new_location_idx):
        if 0 <= new_location_idx < len(self.all_locations):
            self.current_location_idx = new_location_idx
            current_loc = self.get_current_location()
            self.add_message(f"你来到了 {current_loc['name']}。")
            self.add_message(current_loc['description'])
            
            # Reset pagination for any context specific lists
            self.item_page_inv = 0
            self.scroll_offset_inventory = 0
            
            # Chance to encounter enemy immediately upon entering some locations (not towns)
            if current_loc["enemies"] and random.random() < 0.3: # 30% chance if enemies present
                self.start_battle()
        else:
            self.add_message("无效的地点。")

    def attempt_escape_battle(self):
        if self.state != GameState.BATTLE: return

        if random.random() < 0.75:
            self.add_message("你成功逃离了战斗！")
            self.state = GameState.EXPLORING
            self.current_enemy = None
        else:
            self.add_message("逃跑失败！")
            self.end_player_turn_in_battle() # Enemy gets a turn

    def rest_at_location(self):
        current_loc = self.get_current_location()
        if current_loc.get("can_rest", False):
            self.player.hp = self.player.max_hp
            self.player.mp = self.player.max_mp
            # Clear some negative status effects? (optional)
            # self.player.status_effects = [e for e in self.player.status_effects if e.is_positive_or_permanent()]
            self.add_message("你休息了一下，完全恢复了状态！")
        else:
            self.add_message("这里无法休息。")


    # --- Drawing Functions ---
    def draw_text(self, text, font, color, x, y, align="left", max_width=None):
        if max_width:
            words = text.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            line_height_total = 0
            for i, line_text in enumerate(lines):
                text_surface = font.render(line_text.strip(), True, color)
                text_rect = text_surface.get_rect()
                if align == "center":
                    text_rect.centerx = x
                elif align == "right":
                    text_rect.right = x
                else:  # left
                    text_rect.left = x
                text_rect.top = y + i * (font.get_linesize())
                screen.blit(text_surface, text_rect)
                line_height_total += font.get_linesize()
            return line_height_total
        else:
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            if align == "center":
                text_rect.center = (x, y)
            elif align == "right":
                text_rect.right = x
                text_rect.top = y
            else:  # left
                text_rect.left = x
                text_rect.top = y
            screen.blit(text_surface, text_rect)
            return text_rect.height

    def draw_button(self, text, x, y, width, height,
                inactive_color, active_color,
                text_color=KURO, font_to_use=None,
                border_color=None, border_width=0):
        """渲染按钮，并在鼠标悬停时改变颜色"""

        font_to_use = font_to_use or font_medium
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

    def mouse_in_rect(self, x, y, width, height):
        mx, my = pygame.mouse.get_pos()
        return x <= mx <= x + width and y <= my <= y + height

    def draw_message_log(self, x, y, width, height):
        # 背景与边框
        pygame.draw.rect(screen, LIGHT_PANEL, (x, y, width, height))
        pygame.draw.rect(screen, TEXT_LIGHT, (x, y, width, height), 1)

        padding = 5
        line_height = font_small.get_linesize()
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
            self.draw_text(message, font_small, TEXT_FAINT, x + padding, current_y, max_width=width - 2 * padding)
            current_y += line_height * (1 + message.count('\n'))
            if current_y > y + height - line_height:
                break

        # --- 清除按钮 ---
        clear_btn_w, clear_btn_h = 50, 24
        if self.draw_button("清除", x + width - clear_btn_w - 18, y + height - clear_btn_h - 12,
                            clear_btn_w, clear_btn_h, BTN_RED, BTN_RED_HOVER, font_to_use=font_small):
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
        if not self.player: return
        self.draw_text(f"{self.player.name} | Lvl: {self.player.level}", font_medium, TEXT_LIGHT, x + 10, y + 10)
        self.draw_text(f"HP: {self.player.hp}/{self.player.max_hp}", font_small, BTN_GREEN if self.player.hp > self.player.max_hp * 0.3 else BTN_RED, x + 10, y + 40)
        self.draw_text(f"MP: {self.player.mp}/{self.player.max_mp}", font_small, BTN_BLUE, x + 170, y + 40)
        self.draw_text(f"ATK: {self.player.attack} DEF: {self.player.defense}", font_small, TEXT_FAINT, x + 10, y + 65)
        self.draw_text(f"EXP: {self.player.exp}/{self.player.exp_to_next_level}", font_small, BTN_PURPLE, x + 170, y + 65)
        self.draw_text(f"金币: {self.gold}", font_small, BTN_ORANGE, x + 170, y + 90)

    def draw_main_menu(self):
        screen.fill(BG_DARK)
        self.draw_text("RPG 文字冒险游戏", font_title, SHIRONERI, SCREEN_WIDTH//2, 150, "center")

        if self.draw_button("开始新游戏", SCREEN_WIDTH//2 - 100, 300, 200, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame: self.start_new_game()
        # Add Load Game Button if implemented
        if self.draw_button("退出游戏", SCREEN_WIDTH//2 - 100, 400, 200, 50, BTN_BLUE, BTN_BLUE_HOVER):
            if self.clicked_this_frame: pygame.quit(); sys.exit()

    def draw_exploring(self):
        screen.fill(BG_DARK)
        current_loc = self.get_current_location()

        # 玩家状态栏
        self.draw_player_status_bar(10, 10, 300, 120)

        # 地点信息框
        pygame.draw.rect(screen, LIGHT_PANEL, (SCREEN_WIDTH - 330, 10, 320, 120))
        self.draw_text(f"当前位置: {current_loc['name']}", font_medium, TEXT_LIGHT, SCREEN_WIDTH - 320, 20)
        self.draw_text(current_loc['description'], font_small, TEXT_FAINT, SCREEN_WIDTH - 320, 50, max_width=310)

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
            if self.draw_button("休息-20$", button_x_start, button_y, button_width, button_height, BTN_PURPLE, BTN_PURPLE_HOVER):
                if self.clicked_this_frame:
                    if self.gold >= 20:
                        self.gold -= 20
                        self.rest_at_location()
                    else:
                        self.add_message("金币不足，无法休息。")

        # 地点跳转按钮
        loc_btn_y_start = 180
        loc_btn_x = SCREEN_WIDTH - button_width - 30
        self.draw_text("前往:", font_medium, TEXT_LIGHT, loc_btn_x + button_width // 2, loc_btn_y_start - 25, "center")
        for i, loc_data in enumerate(self.all_locations):
            if i != self.current_location_idx:
                if self.draw_button(loc_data["name"], loc_btn_x, loc_btn_y_start, button_width, 35, BTN_GRAY, BTN_GRAY_LIGHT, KURO, font_small):
                    if self.clicked_this_frame:
                        self.change_location(i)
                loc_btn_y_start += 35 + 10

    def _draw_generic_list_menu(self, title, items_to_display, item_handler_func, back_state, current_page, scroll_offset_attr_name, items_per_page=5, item_price_func=None, item_desc_func=None):
        screen.fill(BG_DARK)
        self.draw_text(title, font_large, TEXT_LIGHT, SCREEN_WIDTH // 2, 30, "center")

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
            self.draw_text("空空如也。", font_medium, TEXT_LIGHT, SCREEN_WIDTH // 2, 120, "center")
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

                if self.draw_button(item_text, x, y, col_width, button_height, BTN_GREEN, BTN_GREEN_HOVER, KURO, font_medium):
                    if self.clicked_this_frame:
                        item_handler_func(item)

                # 描述文字显示在按钮下方
                desc = item_desc_func(item) if item_desc_func else getattr(item, 'description', None)
                if desc:
                    self.draw_text(desc, font_small, TEXT_FAINT, x + 6, y + button_height + 2, max_width=col_width - 12)

        # 分页导航
        total_pages = (len(merged_items) - 1) // (items_per_page * 2) + 1
        if total_pages > 1:
            self.draw_text(f"页: {current_page + 1}/{total_pages}", font_medium, TEXT_FAINT, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130, "center")
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
        def handle_item_use_from_inv(item_obj):
            # Determine target (player for most items, enemy if in battle and item is offensive)
            target_char = self.player
            if self.state == GameState.BATTLE and item_obj.target == "enemy":
                target_char = self.current_enemy
            
            success, message = self.use_item(item_obj, target_char)
            if success:
                if self.state == GameState.INVENTORY : # If used outside battle
                    self.state = GameState.EXPLORING # Go back to exploring after use
                elif self.state == GameState.BATTLE: # If used in battle
                    if not self.current_enemy.is_alive():
                        self.battle_victory()
                    elif not self.player.is_alive(): # Self-damage items?
                        self.game_over()
                    else: # End player's turn in battle
                        self.end_player_turn_in_battle()
                    # After using an item in battle, usually return to battle screen
                    # The use_item might change state if battle ends.
                    # For now, assume we return to inventory and user clicks "Back" or item use forces battle screen
                    # To simplify, let's make it so using an item from inv during battle returns to battle screen
                    if self.state == GameState.BATTLE: # Check again if state changed
                        pass # Stay in battle, turn changes
                    else: # Battle ended due to item use
                        pass
                # If item_page_inv needs reset if list shrinks
                if len(self.player.inventory) <= self.item_page_inv * self.items_per_page and self.item_page_inv > 0:
                    self.item_page_inv -=1


        back_state = GameState.BATTLE if self.current_enemy and self.state != GameState.EXPLORING else GameState.EXPLORING
        self._draw_generic_list_menu("物品栏", self.player.inventory, handle_item_use_from_inv, back_state, self.item_page_inv, "item_page_inv", self.items_per_page)


    def draw_battle(self):
        screen.fill(BG_DARK if self.current_enemy else KURO) # Darker red for battle

        # Player and Enemy Status Panels
        if self.player:
            self.draw_player_status_bar(10, 10, SCREEN_WIDTH // 2 - 20, 120)
        if self.current_enemy:
            pygame.draw.rect(screen, LIGHT_PANEL, (SCREEN_WIDTH // 2 + 10, 10, SCREEN_WIDTH // 2 - 20, 120))
            self.draw_text(f"{self.current_enemy.name} | Lvl: {self.current_enemy.level}", font_medium, TEXT_LIGHT, SCREEN_WIDTH // 2 + 20, 20)
            self.draw_text(f"HP: {self.current_enemy.hp}/{self.current_enemy.max_hp}", font_small, BTN_GREEN if self.current_enemy.hp > self.current_enemy.max_hp * 0.3 else BTN_RED, SCREEN_WIDTH // 2 + 20, 50)
            self.draw_text(f"MP: {self.current_enemy.mp}/{self.current_enemy.max_mp}", font_small, BTN_BLUE, SCREEN_WIDTH // 2 + 220, 50)
            self.draw_text(f"ATK: {self.current_enemy.attack} DEF: {self.current_enemy.defense}", font_small, TEXT_FAINT, SCREEN_WIDTH // 2 + 20, 75)
            # Display enemy status effects
            y_offset_status = 95
            for effect in self.current_enemy.status_effects[:2]: # Show first 2
                self.draw_text(f"{effect.name}({effect.turns_remaining})", font_small, BTN_PURPLE, SCREEN_WIDTH // 2 + 20, y_offset_status)
                y_offset_status += 15


        # Message Log
        log_y = SCREEN_HEIGHT - 160
        self.draw_message_log(10, log_y, SCREEN_WIDTH - 20, 150)

        # Battle Turn Indicator
        turn_text = "你的回合！" if self.battle_turn == "player" else f"{self.current_enemy.name} 的回合..."
        self.draw_text(turn_text, font_medium, TEXT_LIGHT, SCREEN_WIDTH // 2, 140, "center")

        # Action Panel (Player's Turn)
        action_panel_y = SCREEN_HEIGHT - 300 # Adjusted Y for message log
        if self.battle_turn == "player" and self.player.is_alive():
            # Skills
            skill_button_x = 20
            skill_button_y = action_panel_y
            self.draw_text("技能:", font_medium, TEXT_LIGHT, skill_button_x + 75, skill_button_y - 25, "center")

            # Pagination for skills
            skills_per_page_battle = 3
            start_skill_idx = self.scroll_offset_skills * skills_per_page_battle
            end_skill_idx = start_skill_idx + skills_per_page_battle
            visible_skills = self.player.skills[start_skill_idx:end_skill_idx]

            for i, skill in enumerate(visible_skills):
                actual_skill_idx = start_skill_idx + i
                skill_text = f"{skill.name}" + str(f"-MP:{skill.mp_cost}" if skill.mp_cost != 0 else '')
                color = BTN_GREEN if self.player.mp >= skill.mp_cost else LIGHT_PANEL # Grey out if not enough MP
                if self.draw_button(skill_text, skill_button_x, skill_button_y + i * 45, 180, 40, color, BTN_GREEN_HOVER if color == BTN_GREEN else LIGHT_PANEL):
                    if self.clicked_this_frame and self.player.mp >= skill.mp_cost:
                        self.player_action(skill_idx=actual_skill_idx)

            # Skill Pagination Buttons
            total_skill_pages = (len(self.player.skills) -1) // skills_per_page_battle + 1
            if total_skill_pages > 1:
                if self.scroll_offset_skills > 0:
                    if self.draw_button("↑", skill_button_x + 200, skill_button_y, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills -=1
                if self.scroll_offset_skills < total_skill_pages - 1:
                     if self.draw_button("↓", skill_button_x + 200, skill_button_y + 45, 40, 40, BTN_BLUE, BTN_BLUE_HOVER):
                        if self.clicked_this_frame: self.scroll_offset_skills +=1


            # Other Actions (Items, Escape)
            action_button_x = SCREEN_WIDTH - 200
            if self.draw_button("物品", action_button_x, action_panel_y, 180, 40, BTN_BLUE, BTN_BLUE_HOVER):
                if self.clicked_this_frame: self.state = GameState.INVENTORY # Go to inventory from battle
            
            if self.draw_button("逃跑", action_button_x, action_panel_y + 45, 180, 40, BTN_ORANGE, BTN_ORANGE_HOVER):
                if self.clicked_this_frame: self.attempt_escape_battle()

        elif self.battle_turn == "enemy" and self.current_enemy and self.current_enemy.is_alive():
            # Enemy action is triggered by timer in run loop or directly
            pass # UI mostly static during enemy turn, messages update

    def draw_battle_reward_screen(self):
        screen.fill(KURO)
        self.draw_text("战斗胜利！", font_large, GOLD, SCREEN_WIDTH // 2, 100, "center")

        y_offset = 180
        self.draw_text(f"获得经验: {self.battle_rewards['exp']}", font_medium, WHITE, SCREEN_WIDTH // 2, y_offset, "center")
        y_offset += 40
        self.draw_text(f"获得金币: {self.battle_rewards['gold']}", font_medium, GOLD, SCREEN_WIDTH // 2, y_offset, "center")
        y_offset += 40

        if self.battle_rewards['items']:
            self.draw_text("获得物品:", font_medium, WHITE, SCREEN_WIDTH // 2, y_offset, "center")
            y_offset += 30
            for item in self.battle_rewards['items']:
                self.draw_text(f"- {item.name}", font_small, CYAN, SCREEN_WIDTH // 2, y_offset, "center")
                y_offset += 25
        
        if self.draw_button("继续", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50, BLUE, GREEN):
            if self.clicked_this_frame:
                self.process_battle_rewards() # This will change state to EXPLORING

    def draw_game_over(self):
        screen.fill(KURO)
        self.draw_text("游戏结束", font_large, RED, SCREEN_WIDTH//2, 200, "center")
        if self.player:
            self.draw_text(f"你的冒险者 {self.player.name} 倒下了。", font_medium, WHITE, SCREEN_WIDTH//2, 250, "center")
            self.draw_text(f"最终等级: {self.player.level}", font_medium, WHITE, SCREEN_WIDTH//2, 280, "center")
        
        if self.draw_button("返回主菜单", SCREEN_WIDTH//2 - 100, 400, 200, 50, BLUE, GOLD):
            if self.clicked_this_frame: self.state = GameState.MAIN_MENU


    def draw_shop_screen(self):
        if self.current_shop_idx is None or not (0 <= self.current_shop_idx < len(self.all_shops)):
            self.add_message("错误：无效的商店。")
            self.state = GameState.EXPLORING
            return
        
        shop = self.all_shops[self.current_shop_idx]
        sellable_goods = shop.get_all_sellable_goods() # Combined list of items and equipment

        def handle_buy_item(item_obj):
            if self.gold >= item_obj.price:
                self.gold -= item_obj.price
                self.player.add_item_to_inventory(item_obj) # Assuming item_obj is a template, new instance might be needed if consumables are unique
                self.add_message(f"购买了 {item_obj.name}。")
            else:
                self.add_message("金币不足！")

        # For selling, need a different list (player's inventory) and different handler
        # This simple _draw_generic_list_menu is for one list. A full shop needs buy/sell tabs.
        # For now, only buying.
        self._draw_generic_list_menu(f"{shop.name} (金币: {self.gold})",
                                     sellable_goods,
                                     handle_buy_item,
                                     GameState.EXPLORING,
                                     self.item_page_shop, "item_page_shop", self.items_per_page,
                                     item_price_func=lambda item: item.price)
        # Add a "Sell" button that could switch to a sell view.


    def draw_equipment_screen(self):
        screen.fill(self.DARK_BLUE) # Different background for equipment
        self.draw_text("装备栏", font_large, WHITE, SCREEN_WIDTH // 2, 30, "center")

        # Display Current Equipment
        y_curr_eq = 80
        self.draw_text("当前装备:", font_medium, WHITE, 150, y_curr_eq, "center")
        for slot, item in self.player.equipment.items():
            slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
            display_name = item.name if item else "无"
            text = f"{slot_name_map.get(slot, slot)}: {display_name}"
            self.draw_text(text, font_small, CYAN, 50, y_curr_eq + 40)
            if item:
                if self.draw_button("卸下", 250, y_curr_eq + 35, 70, 30, RED, ORANGE, WHITE, font_small):
                    if self.clicked_this_frame:
                        _, msg = self.player.unequip(slot)
                        self.add_message(msg)
            y_curr_eq += 35
        
        # Display Equippable Items from Inventory
        equippable_items = [it for it in self.player.inventory if isinstance(it, Equipment)]
        y_inv_eq = y_curr_eq + 40
        self.draw_text("可装备物品 (来自物品栏):", font_medium, WHITE, SCREEN_WIDTH // 2, y_inv_eq, "center")
        y_inv_eq += 40

        start_idx = self.scroll_offset_equipment * self.items_per_page
        end_idx = start_idx + self.items_per_page
        visible_equippable = equippable_items[start_idx:end_idx]

        for i, item_to_equip in enumerate(visible_equippable):
            text = f"{item_to_equip.name} ({item_to_equip.equip_type})"
            if self.draw_button(text, 50, y_inv_eq + i * 45, 300, 40, GREEN, GOLD):
                if self.clicked_this_frame:
                    # Check if already in inventory handled by equip
                    _, msg = self.player.equip(item_to_equip) # equip handles removing from inv
                    self.add_message(msg)
                    # Potentially refresh list or page
                    if len(equippable_items) <= self.scroll_offset_equipment * self.items_per_page and self.scroll_offset_equipment > 0 :
                         self.scroll_offset_equipment -=1


        # Pagination for equippable items
        total_pages = (len(equippable_items) -1) // self.items_per_page + 1
        if total_pages > 1:
             self.draw_text(f"页: {self.scroll_offset_equipment + 1}/{total_pages}", font_medium, WHITE, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 80, "center")
             if self.scroll_offset_equipment > 0:
                if self.draw_button("上", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40, 40, 30, BLUE, CYAN):
                    if self.clicked_this_frame: self.scroll_offset_equipment -=1
             if self.scroll_offset_equipment < total_pages -1:
                if self.draw_button("下", SCREEN_WIDTH - 90, SCREEN_HEIGHT - 40, 40, 30, BLUE, CYAN):
                    if self.clicked_this_frame: self.scroll_offset_equipment +=1


        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 40, 150, 30, RED, ORANGE):
            if self.clicked_this_frame: self.state = GameState.EXPLORING


    def draw_character_info_screen(self):
        screen.fill(self.DARK_GREEN)
        self.draw_text("角色信息", font_large, WHITE, SCREEN_WIDTH // 2, 30, "center")

        if not self.player: return

        y_offset = 80
        col1_x = 50
        col2_x = 400

        # Basic Stats
        self.draw_text(f"名字: {self.player.name}", font_medium, WHITE, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"等级: {self.player.level}", font_medium, WHITE, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"经验: {self.player.exp} / {self.player.exp_to_next_level}", font_medium, WHITE, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"金币: {self.gold}", font_medium, GOLD, col1_x, y_offset)
        y_offset += 50 # Gap

        self.draw_text(f"生命值: {self.player.hp} / {self.player.max_hp}", font_medium, GREEN, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"法力值: {self.player.mp} / {self.player.max_mp}", font_medium, BLUE, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"攻击力: {self.player.attack} (基础: {self.player.base_attack})", font_medium, RED, col1_x, y_offset)
        y_offset += 35
        self.draw_text(f"防御力: {self.player.defense} (基础: {self.player.base_defense})", font_medium, CYAN, col1_x, y_offset)

        # Equipment in second column
        y_offset = 80 # Reset for second column
        self.draw_text("当前装备:", font_medium, WHITE, col2_x, y_offset)
        y_offset += 35
        slot_name_map = {'weapon': "武器", 'armor': "护甲", 'helmet': "头盔", 'accessory': "饰品"}
        for slot, item in self.player.equipment.items():
            display_name = item.name if item else "无"
            self.draw_text(f"{slot_name_map.get(slot, slot)}: {display_name}", font_small, LIGHT_GRAY, col2_x, y_offset)
            y_offset += 25
        
        # Skills
        y_offset += 20
        self.draw_text("技能列表:", font_medium, WHITE, col2_x, y_offset)
        y_offset += 35
        for skill in self.player.skills[:6]: # Show first 6 skills
            self.draw_text(f"- {skill.name} (MP: {skill.mp_cost})", font_small, PURPLE, col2_x, y_offset)
            self.draw_text(f"  {skill.description}", font_small, GRAY, col2_x + 10, y_offset + 20, max_width=SCREEN_WIDTH - col2_x - 20)
            y_offset += 45
            if y_offset > SCREEN_HEIGHT - 100: break # Prevent overflow

        if self.draw_button("返回", SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 60, 150, 40, RED, ORANGE):
            if self.clicked_this_frame: self.state = GameState.EXPLORING
            
    DARK_RED = (100,0,0)
    DARK_GREEN = (0,100,0)
    DARK_BLUE = (0,0,100)
    DARK_GRAY = (50,50,50)


    def run(self):
        clock = pygame.time.Clock()
        running = True
        enemy_action_timer = 0
        enemy_action_delay = 1500  # milliseconds for enemy to "think"

        while running:
            self.clicked_this_frame = False # Reset click state
            self.scroll_up = False
            self.scroll_down = False

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        self.clicked_this_frame = True
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scroll_up = True
                    elif event.y < 0:
                        self.scroll_down = True

                if event.type == KEYDOWN: # Keyboard shortcuts
                    if self.state == GameState.EXPLORING:
                        if event.key == K_i: self.state = GameState.INVENTORY; self.item_page_inv = 0
                        if event.key == K_e: self.state = GameState.EQUIPMENT_SCREEN; self.scroll_offset_equipment = 0
                        if event.key == K_c: self.state = GameState.CHARACTER_INFO
                    elif self.state == GameState.INVENTORY or self.state == GameState.EQUIPMENT_SCREEN or \
                         self.state == GameState.CHARACTER_INFO or self.state == GameState.SHOP:
                        if event.key == K_ESCAPE: 
                            self.state = GameState.BATTLE if self.current_enemy and self.state != GameState.EXPLORING else GameState.EXPLORING
                    elif self.state == GameState.BATTLE and self.battle_turn == "player":
                        if event.key == K_1 and len(self.player.skills) > 0: self.player_action(skill_idx=0)
                        if event.key == K_2 and len(self.player.skills) > 1: self.player_action(skill_idx=1)
                        # Add more skill hotkeys if needed
                        if event.key == K_i: self.state = GameState.INVENTORY


            screen.fill(KURO) # Default background

            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.EXPLORING:
                self.draw_exploring()
            elif self.state == GameState.BATTLE:
                self.draw_battle()
                if self.battle_turn == "enemy" and self.current_enemy and self.current_enemy.is_alive() and self.player.is_alive():
                    current_time = pygame.time.get_ticks()
                    if enemy_action_timer == 0: # Start timer if not already started
                        enemy_action_timer = current_time
                    if current_time - enemy_action_timer >= enemy_action_delay:
                        self.enemy_action()
                        enemy_action_timer = 0 # Reset timer for next enemy turn
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
            # Add other states like VICTORY, DIALOGUE if implemented
                
            pygame.display.flip()
            clock.tick(30) # FPS
            
        pygame.quit()
        sys.exit()


ALL_SKILLS = [
    Skill("普通攻击", 1.0, 0, "基本攻击", "damage", required_level=1),
    Skill("强力一击", 1.5, 5, "造成1.5倍伤害", "damage", required_level=1),
    Skill("火球术", 1.2, 8, "小范围火焰伤害", "damage", status_effect="燃烧", effect_duration=3, required_level=2), # DoT
    Skill("治疗术", 0, 10, "恢复少量生命", "heal", effect_value=50, target="self", required_level=3),
    Skill("雷击", 2.0, 15, "强力单体雷电伤害", "damage", required_level=5),
    Skill("守护祷言", 0, 12, "提升自身防御3回合", "buff_self", effect_value=10, status_effect="防御提升", effect_duration=3, required_level=4),
    Skill("破甲击", 1.3, 10, "攻击并降低目标防御2回合", "debuff_enemy", effect_value=5, status_effect="破甲", effect_duration=2, required_level=6),
    Skill("生命汲取", 1.0, 18, "吸取伤害50%的生命", "lifesteal", effect_value=0.5, required_level=7), # effect_value is % of damage healed
    Skill("群体治疗", 0, 25, "恢复全队中量生命", "heal", effect_value=80, target="self", required_level=10), # Target self for now, extend for party
    Skill("烈焰风暴", 1.8, 30, "强力火焰魔法", "damage", status_effect="燃烧", effect_duration=3, required_level=12),
    Skill("寒冰箭", 1.5, 20, "冰冻攻击，可能降低敌方速度", "debuff_enemy", effect_value=5, status_effect="冰冻", effect_duration=2, required_level=8) # Placeholder for speed debuff
]

ALL_ITEMS = [
    Item("小型治疗药水", "heal_hp", 50, "恢复50点生命值", 20),
    Item("中型治疗药水", "heal_hp", 120, "恢复120点生命值", 50),
    Item("小型法力药水", "heal_mp", 30, "恢复30点法力值", 30),
    Item("中型法力药水", "heal_mp", 80, "恢复80点法力值", 70),
    Item("解毒草", "cure_status", 0, "解除中毒状态", 40), # Example for status cure
    Item("磨刀石", "buff_attack", 5, "攻击小幅提升3回合", 60, duration=3),
    Item("硬化剂", "buff_defense", 5, "防御小幅提升3回合", 60, duration=3),
    Item("炸弹", "damage_enemy", 75, "对敌人造成75点伤害", 100, target="enemy"),
    Item("传送卷轴", "teleport", 0, "返回上一个城镇(未实现)", 150) # Special item
]

ALL_EQUIPMENTS = [
    Equipment("新手剑", "weapon", 5, 0, 0, 0, "给新手准备的剑", 50),
    Equipment("皮甲", "armor", 0, 3, 10, 0, "简单的皮制护甲", 70),
    Equipment("木盾", "accessory", 0, 2, 0, 0, "一个简陋的木盾", 30), # Accessory slot can be shield
    Equipment("法师帽", "helmet", 0, 1, 0, 10, "增加少量法力上限", 60),

    Equipment("铁剑", "weapon", 10, 0, 0, 0, "标准的铁剑", 200),
    Equipment("锁子甲", "armor", 0, 8, 20, 0, "提供良好保护的锁子甲", 250),
    Equipment("铁盔", "helmet", 0, 4, 0, 0, "保护头部的铁盔", 180),
    Equipment("力量指环", "accessory", 3, 0, 0, 5, "小幅提升力量和法力", 150),

    Equipment("精灵之刃", "weapon", 18, 2, 10, 10, "轻巧而锋利的剑", 750),
    Equipment("秘银甲", "armor", 2, 15, 50, 20, "魔法金属制成的护甲", 1200),
    Equipment("贤者之冠", "helmet", 0, 5, 10, 30, "大幅提升法力上限和恢复", 800),
    Equipment("守护者护符", "accessory", 0, 5, 30, 0, "强大的守护力量", 600),
]

ALL_LOCATIONS = [
    {
        "name": "宁静小村", "description": "一个和平的小村庄，冒险的起点。",
        "enemies": [], # No enemies in the first village
        "shop_idx": 0, # Index of shop in self.all_shops
        "can_rest": True
    },
    {
        "name": "村外小径", "description": "连接村庄和森林的小路。",
        "enemies": [0, 1], # Indices from self.all_enemies_templates
        "shop_idx": None,
        "can_rest": False
    },
    {
        "name": "迷雾森林", "description": "充满未知危险的森林。",
        "enemies": [1, 2, 3, 4],
        "shop_idx": 1, # A shop deeper in or at edge of forest
        "can_rest": False
    },
    {
        "name": "巨人山谷入口", "description": "传说有巨人出没的山谷。",
        "enemies": [3, 5],
        "shop_idx": None,
        "can_rest": False
    }
    # Add more locations
]


# 主函数
def main():
    # Define new colors used in RPGGame if they are class members
    RPGGame.DARK_RED = (100,0,0)
    RPGGame.DARK_GREEN = (0,100,0)
    RPGGame.DARK_BLUE = (0,0,100)
    RPGGame.DARK_GRAY = (50,50,50)
    RPGGame.LIGHT_GRAY = (200,200,200) # ensure all colors are accessible

    game = RPGGame()
    game.run()

if __name__ == "__main__":
    main()