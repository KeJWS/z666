from enum import Enum, auto

from data import Shop
from character import Enemy
import load_datas

# 游戏状态
class GameState(Enum):
    MAIN_MENU = auto()
    EXPLORING = auto()
    BATTLE = auto()
    DIALOGUE = auto()  # 未完全实现，可扩展
    INVENTORY = auto()
    GAME_OVER = auto()
    VICTORY = auto()   # 未完全实现，可扩展
    SHOP = auto()
    EQUIPMENT_SCREEN = auto()
    CHARACTER_INFO = auto()
    BATTLE_REWARD = auto()

def load_game_data():
    # 加载技能
    all_skills = load_datas.load_skills_from_toml("Data/skills.toml")
    skill_map = {s.name: s for s in all_skills}

    # 加载物品
    all_items = load_datas.load_items_from_toml("Data/items.toml")
    item_map = {i.name: i for i in all_items}

    # 加载装备
    all_equipments = load_datas.load_equipment_from_toml("Data/equipments.toml")
    equip_map = {e.name: e for e in all_equipments}

    enemies = [
        Enemy(
            "史莱姆", 30, 10, 8, 2, 1, 15, 10,
            [skill_map["普通攻击"]],
            [{"item_obj": item_map["小型治疗药水"], "chance": 0.3}]
        ),
        Enemy(
            "哥布林", 50, 15, 12, 4, 2, 25, 18,
            [skill_map["普通攻击"], skill_map["强力一击"]],
            [{"item_obj": item_map["小型治疗药水"], "chance": 0.2}, {"item_obj": equip_map["新手剑"], "chance": 0.05}],
            potential_equips=[{"equip_obj": equip_map["新手剑"], "chance": 0.3}, {"equip_obj": equip_map["皮甲"]}]
        ),
        Enemy(
            "野狼", 70, 0, 17, 5, 3, 30, 22,
            [skill_map["普通攻击"]],
            [{"item_obj": item_map["小型法力药水"], "chance": 0.1}]
        ),
        Enemy(
            "强盗", 100, 20, 18, 4, 5, 50, 40,
            [skill_map["普通攻击"], skill_map["强力一击"], skill_map["破甲击"]],
            [{"item_obj": item_map["中型治疗药水"], "chance": 0.2}, {"item_obj": equip_map["铁剑"], "chance": 0.08}],
            potential_equips=[{"equip_obj": equip_map["铁剑"], "chance": 0.3}, {"equip_obj": equip_map["皮甲"]}]
        ),
        Enemy(
            "森林妖精", 100, 50, 15, 10, 5, 60, 50,
            [skill_map["普通攻击"], skill_map["火球术"], skill_map["治疗术"]],
            [{"item_obj": item_map["中型法力药水"], "chance": 0.15}]
        ),
        Enemy(
            "石巨人", 270, 0, 30, 20, 7, 150, 100,
            [skill_map["普通攻击"], skill_map["强力一击"]],
            [{"item_obj": equip_map["锁子甲"], "chance": 0.1}],
            potential_equips=[{"equip_obj": equip_map["锁子甲"], "chance": 0.3}]
        ),
    ]
    enemy_map = {e.name: e for e in enemies}

    locations = [
        {
            "name": "宁静小村", "description": "一个和平的小村庄，冒险的起点。",
            "enemies": [],
            "shop_idx": 0,
            "can_rest": True
        },
        {
            "name": "村外小径", "description": "连接村庄和森林的小路。",
            "enemies": ["史莱姆", "哥布林"],
            "shop_idx": None,
            "can_rest": False
        },
        {
            "name": "迷雾森林", "description": "充满未知危险的森林。",
            "enemies": ["哥布林", "野狼", "强盗", "森林妖精"],
            "shop_idx": 1,
            "can_rest": False
        },
        {
            "name": "巨人山谷入口", "description": "传说有巨人出没的山谷。",
            "enemies": ["强盗", "石巨人"],
            "shop_idx": None,
            "can_rest": False
        }
    ]

    shops = [
        Shop(
            "新手村道具店",
            items_for_sale=[item_map[n] for n in ["小型治疗药水", "小型法力药水", "解毒草"]],
            equipments_for_sale=[equip_map["新手剑"], equip_map["皮甲"]]
        ),
        Shop(
            "森林驿站补给点",
            items_for_sale=[item_map[n] for n in ["中型治疗药水", "中型法力药水", "磨刀石", "硬化剂"]],
            equipments_for_sale=[equip_map[n] for n in ["铁剑", "锁子甲", "铁盔", "力量指环"]]
        )
    ]

    return {
        "skills": all_skills,
        "skill_map": skill_map,
        "items": all_items,
        "item_map": item_map,
        "equipments": all_equipments,
        "equip_map": equip_map,
        "enemies": enemies,
        "enemy_map": enemy_map,
        "locations": locations,
        "shops": shops,
    }

game_data = load_game_data()

ALL_SKILLS = game_data["skills"]
ALL_ITEMS = game_data["items"]
ALL_EQUIPMENTS = game_data["equipments"]
ALL_ENEMIES = game_data["enemies"]
ALL_LOCATIONS = game_data["locations"]
ALL_SHOPS = game_data["shops"]
