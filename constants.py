from enum import Enum, auto

from data import Skill, Item, Equipment

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

ALL_SKILLS = [
    Skill("普通攻击", 1.0, 0, "基本攻击", "damage", required_level=1),
    Skill("强力一击", 1.5, 5, "造成1.5倍伤害", "damage", required_level=1),
    Skill("火球术", 1.2, 8, "小范围火焰伤害", "damage", status_effect="燃烧", effect_duration=3, required_level=2),
    Skill("治疗术", 0, 10, "恢复少量生命", "heal", effect_value=50, target="self", required_level=3),
    Skill("雷击", 2.0, 15, "强力单体雷电伤害", "damage", required_level=5),
    Skill("守护祷言", 0, 12, "提升自身防御3回合", "buff_self", effect_value=10, status_effect="防御提升", effect_duration=3, required_level=4),
    Skill("破甲击", 1.3, 10, "攻击并降低目标防御2回合", "debuff_enemy", effect_value=5, status_effect="破甲", effect_duration=2, required_level=6),
    Skill("生命汲取", 1.0, 18, "吸取伤害50%的生命", "lifesteal", effect_value=0.5, required_level=7),
    Skill("群体治疗", 0, 25, "恢复全队中量生命", "heal", effect_value=80, target="self", required_level=10),
    Skill("烈焰风暴", 1.8, 30, "强力火焰魔法", "damage", status_effect="燃烧", effect_duration=3, required_level=12),
    Skill("寒冰箭", 1.5, 20, "冰冻攻击，可能降低敌方速度", "debuff_enemy", effect_value=5, status_effect="冰冻", effect_duration=2, required_level=8)
]

ALL_ITEMS = [
    Item("小型治疗药水", "heal_hp", 50, "恢复50点生命值", 20),
    Item("中型治疗药水", "heal_hp", 120, "恢复120点生命值", 50),
    Item("小型法力药水", "heal_mp", 30, "恢复30点法力值", 30),
    Item("中型法力药水", "heal_mp", 80, "恢复80点法力值", 70),
    Item("解毒草", "cure_status", 0, "解除中毒状态", 40),
    Item("磨刀石", "buff_attack", 5, "攻击小幅提升3回合", 60, duration=3),
    Item("硬化剂", "buff_defense", 5, "防御小幅提升3回合", 60, duration=3),
    Item("炸弹", "damage_enemy", 75, "对敌人造成75点伤害", 100, target="enemy")
]

ALL_EQUIPMENTS = [
    Equipment("新手剑", "weapon", 5, 0, 0, 0, "给新手准备的剑", 50),
    Equipment("皮甲", "armor", 0, 3, 10, 0, "简单的皮制护甲", 70),
    Equipment("木盾", "accessory", 0, 2, 0, 0, "一个简陋的木盾", 30),
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
        "enemies": [],
        "shop_idx": 0,
        "can_rest": True
    },
    {
        "name": "村外小径", "description": "连接村庄和森林的小路。",
        "enemies": [0, 1],
        "shop_idx": None,
        "can_rest": False
    },
    {
        "name": "迷雾森林", "description": "充满未知危险的森林。",
        "enemies": [1, 2, 3, 4],
        "shop_idx": 1,
        "can_rest": False
    },
    {
        "name": "巨人山谷入口", "description": "传说有巨人出没的山谷。",
        "enemies": [3, 5],
        "shop_idx": None,
        "can_rest": False
    }
]
