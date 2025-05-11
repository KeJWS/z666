import pprint

def print_enemy_details(enemy):
    """打印敌人详细信息，包括基础数据、掉落物品、潜在装备和技能。"""
    print("\n")
    enemy_data = vars(enemy)
    pprint.pprint(enemy_data, depth=None, width=120)

    print("\n遍历并打印 drop_table 里的物品")
    for item_entry in enemy_data["drop_table"]:
        pprint.pprint(item_entry["item_obj"].__dict__, depth=None)

    print("\n遍历并打印 potential_equips 里的装备")
    for equip_entry in enemy_data["potential_equips"]:
        pprint.pprint(equip_entry["equip_obj"].__dict__, depth=None)

    print("\n遍历并打印技能")
    for skill in enemy_data["skills"]:
        pprint.pprint(skill.__dict__, depth=None)
