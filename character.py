import random

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

class Character:
    def __init__(self, name, max_hp, max_mp, attack, defense, level=1, exp=0, game_skills_ref=None):
        self.name = name
        self.hp = max_hp
        self.mp = max_mp
        self.base_max_hp = max_hp
        self.base_max_mp = max_mp
        self.base_attack = attack
        self.base_defense = defense
        self.level = level
        self.exp = exp
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        self.skills = []
        self.inventory = []
        self.status_effects = []
        self.equipment = dict.fromkeys(['weapon', 'armor', 'helmet', 'accessory'])
        self.game_skills_ref = game_skills_ref

    def calculate_exp_to_next_level(self):
        return int(self.level * 100 * (1 + (self.level - 1) * 0.1))

    def _calculate_with_equipment_and_effects(self, base, equip_attr, effect_type_pos, effect_type_neg=None):
        total = base
        for item in self.equipment.values():
            if item:
                total += getattr(item, equip_attr, 0)
        for effect in self.status_effects:
            if effect.effect_type == effect_type_pos:
                total += effect.value
            elif effect_type_neg and effect.effect_type == effect_type_neg:
                total -= effect.value
        return max(0, total)

    @property
    def max_hp(self):
        return self._calculate_with_equipment_and_effects(self.base_max_hp, 'hp_bonus', 'hp_buff')

    @property
    def max_mp(self):
        return self._calculate_with_equipment_and_effects(self.base_max_mp, 'mp_bonus', 'mp_buff')

    @property
    def attack(self):
        return self._calculate_with_equipment_and_effects(self.base_attack, 'attack_bonus', 'attack_buff', 'attack_debuff')

    @property
    def defense(self):
        return self._calculate_with_equipment_and_effects(self.base_defense, 'defense_bonus', 'defense_buff', 'defense_debuff')

    def take_damage(self, damage):
        actual = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount):
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def use_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def restore_mp(self, amount):
        old = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old

    def is_alive(self):
        return self.hp > 0

    def gain_exp(self, exp_amount):
        if not self.is_alive():
            return False, 0, []

        self.exp += exp_amount
        leveled_up = 0
        all_level_ups = []

        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            info = self.level_up()
            all_level_ups.append(info)
            leveled_up += 1

        return leveled_up > 0, leveled_up, all_level_ups

    def level_up(self):
        self.level += 1
        old_stats = {
            'hp': self.base_max_hp,
            'mp': self.base_max_mp,
            'atk': self.base_attack,
            'def': self.base_defense
        }

        self.base_max_hp += int(self.base_max_hp * 0.05) + 10 + self.level
        self.base_max_mp += int(self.base_max_mp * 0.05) + 5 + self.level // 2
        self.base_attack += 2 + self.level // 4
        self.base_defense += 1 + self.level // 5

        self.hp = self.max_hp
        self.mp = self.max_mp
        self.exp_to_next_level = self.calculate_exp_to_next_level()

        learned = []
        if self.game_skills_ref:
            for skill in self.game_skills_ref:
                if skill.required_level == self.level and skill not in self.skills:
                    self.skills.append(skill)
                    learned.append(skill.name)

        return {
            'hp_increase': self.base_max_hp - old_stats['hp'],
            'mp_increase': self.base_max_mp - old_stats['mp'],
            'attack_increase': self.base_attack - old_stats['atk'],
            'defense_increase': self.base_defense - old_stats['def'],
            'learned_skills': learned
        }

    def add_status_effect(self, effect_template):
        existing = next((e for e in self.status_effects if e.name == effect_template.name), None)
        if existing:
            existing.turns_remaining = effect_template.duration
        else:
            new_effect = StatusEffect(
                effect_template.name,
                effect_template.effect_type,
                effect_template.value,
                effect_template.duration,
                effect_template.description
            )
            self.status_effects.append(new_effect)

    def update_status_effects_at_turn_start(self):
        messages = []
        to_remove = []
        for effect in self.status_effects:
            msg = effect.apply_effect_on_turn(self)
            if msg:
                messages.append(msg)
            if effect.duration != -1 and effect.tick():
                to_remove.append(effect)
                messages.append(f"{self.name}的 {effect.name} 效果结束了。")

        self.status_effects = [e for e in self.status_effects if e not in to_remove]

        if self.hp <= 0 and self.is_alive():
            self.hp = 0
            messages.append(f"{self.name} 因状态效果倒下了！")

        return messages

    def equip(self, item):
        slot = item.equip_type
        old_item = self.unequip(slot)[0] if self.equipment.get(slot) else None
        self.equipment[slot] = item
        if item in self.inventory:
            self.inventory.remove(item)
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)
        return old_item, f"装备了 {item.name}。"

    def unequip(self, slot):
        item = self.equipment.get(slot)
        if item:
            self.equipment[slot] = None
            self.add_item_to_inventory(item)
            self.hp = min(self.hp, self.max_hp)
            self.mp = min(self.mp, self.max_mp)
            return item, f"卸下了 {item.name}。"
        return None, "该部位没有装备。"

    def add_item_to_inventory(self, item, quantity=1):
        self.inventory.extend([item] * quantity)
        self.inventory.sort(key=lambda x: x.name)

    def remove_item_from_inventory(self, item, quantity=1):
        removed = 0
        for i in range(len(self.inventory) - 1, -1, -1):
            if self.inventory[i] is item:
                del self.inventory[i]
                removed += 1
                if removed >= quantity:
                    break

class Enemy(Character):
    def __init__(self, name, max_hp, max_mp, attack, defense, level, exp_reward, gold_reward, skills_refs=None, drop_table=None, description="", potential_equips=None):
        super().__init__(name, max_hp, max_mp, attack, defense, level)
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.skills = skills_refs or []
        self.drop_table = drop_table or []
        self.description = description
        self.potential_equips = potential_equips or []

    def choose_action(self, target_player):
        from data import Skill
        if self.hp < self.max_hp * 0.3:
            healing = [s for s in self.skills if s.skill_type == "heal" and s.target == "self" and self.mp >= s.mp_cost]
            if healing:
                return random.choice(healing)

        offensives = [s for s in self.skills if s.skill_type != "heal" and self.mp >= s.mp_cost]
        if offensives and random.random() < 0.7:
            return random.choice(offensives)

        return next((s for s in self.skills if s.mp_cost == 0), Skill("猛击", 1.2, 0, "敌人胡乱攻击", "damage"))

    def clone(self):
        new_enemy = Enemy(
            name=self.name,
            max_hp=self.base_max_hp,
            max_mp=self.base_max_mp,
            attack=self.base_attack,
            defense=self.base_defense,
            level=self.level,
            exp_reward=self.exp_reward,
            gold_reward=self.gold_reward,
            skills_refs=self.skills[:],
            drop_table=self.drop_table[:],
            description=self.description,
            potential_equips=self.potential_equips[:]
        )
        return new_enemy
