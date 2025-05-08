import toml

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
    ATTRS = ['max_hp', 'max_mp', 'attack', 'defense', 'm_attack', 'm_defense', 'agility', 'luck']

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

def load_weapons_from_toml(path):
    data = toml.load(path)
    weapons_dict = {}

    for entry in data.get("weapon", []):
        weapon = Weapon(
            entry.get("id"),
            entry.get("name"),
            entry.get("description"),
            entry.get("price"),
            entry.get("equip_type"),
            entry.get("weapon_type"),
            entry.get("hp", 0),
            entry.get("mp", 0),
            entry.get("atk", 0),
            entry.get("def", 0),
            entry.get("mat", 0),
            entry.get("mdf", 0),
            entry.get("agi", 0),
            entry.get("luk", 0)
        )
        weapons_dict[weapon.id] = weapon

    return weapons_dict

if __name__ == "__main__":
    weapons = load_weapons_from_toml("weapons_output.toml")
    print(weapons[2])
    print("\n")
    print("\n".join(f"{k}: {v}" for k, v in vars(weapons[2]).items()))
