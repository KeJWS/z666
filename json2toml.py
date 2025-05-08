import json
from tomlkit import document, table, dumps

# 读取 JSON 数据
with open('z666/weapons_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建 TOML 文档对象
doc = document()

# weapon 表数组初始化
weapons = []

for item in data.values():
    weapon_table = table()
    weapon_table.add('id', int(item['id']))
    weapon_table.add('name', item['name'])
    weapon_table.add('description', item['description'].replace("\n", "").replace("\\n", "").strip())
    weapon_table.add('price', int(item['price']))
    weapon_table.add('equip_type', int(item['equip_type']))
    weapon_table.add('weapon_type', int(item['weapon_type']))

    weapon_table.add('max_hp', int(item['max_hp'])) if int(item['max_hp']) != 0 else None
    weapon_table.add('max_mp', int(item['max_mp'])) if int(item['max_mp']) != 0 else None
    weapon_table.add('atk', int(item['attack'])) if int(item['attack']) != 0 else None
    weapon_table.add('def', int(item['defense'])) if int(item['defense']) != 0 else None
    weapon_table.add('mat', int(item['m_attack'])) if int(item['m_attack']) != 0 else None
    weapon_table.add('mdf', int(item['m_defense'])) if int(item['m_defense']) != 0 else None
    weapon_table.add('agi', int(item['agility'])) if int(item['agility']) != 0 else None
    weapon_table.add('luk', int(item['luck'])) if int(item['luck']) != 0 else None

    weapons.append(weapon_table)

doc['weapon'] = weapons

# 输出到文件
with open("z666/weapons_output.toml", "w", encoding="utf-8") as f:
    f.write(dumps(doc))
