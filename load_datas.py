import toml

def load_skills_from_toml(path: str):
    from data import Skill
    data = toml.load(path)
    skills = []
    for s in data.get("skills", []):
        skill = Skill(
            name=s["name"],
            damage_multiplier=s["power_multiplier"],
            mp_cost=s["mp_cost"],
            description=s["description"],
            skill_type=s["type"],
            effect_value=s.get("effect_value"),
            required_level=s.get("required_level"),
            target=s.get("target"),
            status_effect=s.get("status_effect"),
            effect_duration=s.get("effect_duration"),
        )
        skills.append(skill)
    return skills

def load_items_from_toml(path: str):
    from data import Item
    data = toml.load(path)
    items = []
    for _, its in data.get("items", {}).items():
        for s in its:
            item = Item(
                name=s["name"],
                item_type=s["type"],
                effect_value=s.get("value", ),
                description=s["description"],
                price=s.get("price"),
                duration=s.get("duration"),
                target=s.get("target"),
            )
            items.append(item)
    return items

def load_equipment_from_toml(path: str):
    from data import Equipment
    data = toml.load(path)
    equipments = []
    for category, items in data.get("equipments", {}).items():
        for s in items:
            equipment = Equipment(
                name=s["name"],
                equip_type=s.get("type", category.rstrip('s')),
                attack_bonus=s.get("atk", 0),
                defense_bonus=s.get("def", 0),
                hp_bonus=s.get("hp", 0),
                mp_bonus=s.get("mp", 0),
                description=s.get("description", ""),
                price=s.get("price", 0),
            )
            equipments.append(equipment)
    return equipments
