import csv
import json
from enum import Enum

class Param(str, Enum):
    Equip_Type = 'etypeId'
    Weapon_Type = 'wtypeId'
    Max_HP = 'params0'
    Max_MP = 'params1'
    Attack = 'params2'
    Defense = 'params3'
    M_Attack = 'params4'
    M_Defense = 'params5'
    Agility = 'params6'
    Luck = 'params7'

class Battler:
    ATTRS = ['max_hp', 'max_mp', 'attack', 'defense', 'm_attack', 'm_defense', 'agility', 'luck']

    def __init__(self, id, name, *stats):
        self.id = id
        self.name = name
        for attr, val in zip(self.ATTRS, stats):
            setattr(self, attr, int(val))
        self.hp = self.max_hp
        self.mp = self.max_mp

    def __str__(self):
        stats = " ".join(f"{attr}:{getattr(self, attr)}" for attr in ['hp', 'mp'] + self.ATTRS[2:])
        return f"[{self.id}] {self.name} - {stats}"

    def clone(self):
        return self.__class__(self.id, self.name, *(getattr(self, attr) for attr in self.ATTRS))

class Player(Battler):
    def __init__(self, id, name, *stats):
        super().__init__(id, name, *stats)
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50
        self.money = 0
        self.is_ally = True

class Enemy(Battler):
    def __init__(self, id, name, exp, gold, *stats):
        super().__init__(id, name, *stats)
        self.exp = int(exp)
        self.gold = int(gold)

    def __str__(self):
        base = super().__str__()
        extra = f"{' exp:' + str(self.exp) if self.exp else ''}{' gold:' + str(self.gold) if self.gold else ''}"
        return base + extra

    def clone(self):
        return self.__class__(
            self.id, self.name, *(getattr(self, attr) for attr in self.ATTRS),
            exp=self.exp, gold=self.gold
        )

class Ally(Battler):
    def __init__(self, id, name, *stats):
        super().__init__(id, name, *stats)
        self.is_ally = True

class Item:
    def __init__(self, id, name, description, price, amount=1):
        self.id = id
        self.name = name
        self.description = description
        self.price = int(price)
        self.amount = amount

    def __str__(self):
        return f"[{self.id}] {self.name} - info:{self.description} price:{self.price}"

    def clone(self, amount=1):
        return Item(self.id, self.name, self.description, self.price, amount)

class Equipment(Item):
    ATTRS = Battler.ATTRS

    def __init__(self, id, name, description, price, equip_type, *stats, amount=1):
        super().__init__(id, name, description, price, amount)
        self.equip_type = int(equip_type)
        for attr, val in zip(self.ATTRS, stats):
            setattr(self, attr, int(val))

    def __str__(self):
        stats = [
            f"hp:{self.max_hp}" if self.max_hp else "",
            f"mp:{self.max_mp}" if self.max_mp else "",
            f"atk:{self.attack}" if self.attack else "",
            f"def:{self.defense}" if self.defense else "",
            f"mat:{self.m_attack}" if self.m_attack else "",
            f"mdf:{self.m_defense}" if self.m_defense else "",
            f"agi:{self.agility}" if self.agility else "",
            f"luk:{self.luck}" if self.luck else "",
            f"price:{self.price}" if self.price else ""
        ]
        return f"[{self.id}] {self.name} - " + " ".join(filter(None, stats))

    def clone(self, amount=1):
        return self.__class__(
            self.id, self.name, self.description, self.price, self.equip_type,
            *(getattr(self, attr) for attr in self.ATTRS), amount
        )

class Weapon(Equipment):
    def __init__(self, id, name, description, price, equip_type, weapon_type, *stats, amount=1):
        super().__init__(id, name, description, price, equip_type, *stats, amount)
        self.weapon_type = int(weapon_type)

class Armor(Equipment):
    pass

def load_equipment_from_csv(csv_path, cls, fields, skip_first_row=False, skip_fields=None):
    equipment = {}
    skip_fields = skip_fields or []
    with open(csv_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if skip_first_row:
            next(reader, None)
        for row in reader:
            if any(not row.get(field, '').strip() for field in skip_fields):
                continue
            values = [row.get(k, '').strip() or 0 for k in fields]
            item = cls(*values)
            equipment[item.id] = item

    return equipment

def export_and_preview(data_dict, file_path, preview_count=10, label="数据"):
    lines = [str(obj) for obj in data_dict.values()]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n===== 前 {preview_count} 行 =====")
    print("\n".join(lines[:preview_count]))
    print("...")
    print(f"\n===== 尾 {preview_count} 行 =====")
    print("\n".join(lines[-preview_count:]))
    print("...")
    print(f"\n已将全部 {len(lines)} 条{label}写入 {file_path}")


def dump_weapons_json(weapons: dict, file_path: str):
    data = {k: vars(v) for k, v in weapons.items()}
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

WEAPON_FIELDS = ['id', 'name', 'description', 'price', Param.Equip_Type, Param.Weapon_Type, 
                 Param.Max_HP, Param.Max_MP, Param.Attack, Param.Defense,
                 Param.M_Attack, Param.M_Defense, Param.Agility, Param.Luck]

ARMOR_FIELDS = ['id', 'name', 'description', 'price', Param.Equip_Type,
                Param.Max_HP, Param.Max_MP, Param.Attack, Param.Defense,
                Param.M_Attack, Param.M_Defense, Param.Agility, Param.Luck]

ENEMY_FIELDS = ['id', 'name', 'exp', 'gold',
                Param.Max_HP, Param.Max_MP, Param.Attack, Param.Defense,
                Param.M_Attack, Param.M_Defense, Param.Agility, Param.Luck]

WEAPONS = load_equipment_from_csv("z666/DatabaseWeapons.csv", Weapon, WEAPON_FIELDS, True, skip_fields=["name", "description"])
ARMORS = load_equipment_from_csv("z666/DatabaseArmors.csv", Armor, ARMOR_FIELDS, True, skip_fields=["name", "description"])
ENEMIES = load_equipment_from_csv("z666/DatabaseEnemies.csv", Enemy, ENEMY_FIELDS, True, skip_fields=["name"])

if __name__ == "__main__":
    # export_and_preview(WEAPONS, "z666/weapon_output.ini", label="武器")
    # export_and_preview(ARMORS, "z666/armor_output.ini", label="防具")
    # export_and_preview(ENEMIES, "z666/enemy_output.ini", label="敌人")

    print(WEAPONS['2'])
    print()
    print("\n".join(f"{k}: {v}" for k, v in vars(WEAPONS['2']).items()))
    print()
    dump_weapons_json(WEAPONS, "z666/weapons_dump.json")
