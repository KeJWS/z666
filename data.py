import random

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

class Shop:
    def __init__(self, name, items_for_sale=None, equipments_for_sale=None, sell_modifier=0.5):
        self.name = name
        self.items_for_sale = items_for_sale or []
        self.equipments_for_sale = equipments_for_sale or []
        self.sell_modifier = sell_modifier

    def get_all_sellable_goods(self):
        return self.items_for_sale + self.equipments_for_sale
