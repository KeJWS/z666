import csv
import random
import toml
from rich.console import Console
from rich.table import Table
from typing import Dict, Any, List, Tuple, Optional

console = Console()

# 属性评级对应的缩放因子范围
ATTRIBUTE_SCALE: Dict[str, Tuple[float, float]] = {
    "decrease_more": (-0.75, -0.5),
    "decrease": (-0.5, -0.3),
    "decrease_little": (-0.25, -0.1),
    "very_low": (0.3, 0.5),
    "low": (0.5, 0.7),
    "medium": (0.7, 1),
    "high": (1.2, 1.45),
    "very_high": (1.7, 2.4),
    "best": (2.7, 3.2),
}

# 各项属性的基础值，用于计算属性成长
BASES: Dict[str, int] = {
    "max_hp": 50,
    "max_mp": 30,
    "attack": 12,
    "defense": 12,
    "m_attack": 12,
    "m_defense": 12,
    "agility": 10,
    "luck": 10,
}

# TOML 文件中的键名到标准属性键名的映射
TOML_KEY_MAP: Dict[str, str] = {
    "atk": "attack",
    "def": "defense",
    "mat": "m_attack",
    "mdf": "m_defense",
    "agi": "agility",
    "luk": "luck",
    "max_hp": "max_hp",
    "max_mp": "max_mp"
}

# CSV 文件头部字段顺序
CSV_HEADER: List[str] = [
    "id", "name", "description", "price", "equip_type", "weapon_type", "level"
] + list(BASES.keys())

def generate_stat(level: int, rating: str, base_per_level: int) -> int:
    """
    根据等级、评级和基础成长值生成单个属性值。

    Args:
        level: 装备等级。
        rating: 属性评级 (例如 "high", "low")。
        base_per_level: 该属性每级的基础成长值。

    Returns:
        计算得到的属性值，如果评级无效则返回 0。
    """
    if rating in ATTRIBUTE_SCALE:
        factor = random.uniform(*ATTRIBUTE_SCALE[rating])
        return int(level * base_per_level * factor)
    return 0

def calculate_price(stats: Dict[str, int], level: int) -> int:
    """
    根据装备的属性和等级计算其价格。

    Args:
        stats: 包含装备各项属性值的字典。
        level: 装备等级。

    Returns:
        计算得到的装备价格。
    """
    # 每项属性的基础权重，可自定义
    weights: Dict[str, float] = {
        "max_hp": 1.5,
        "max_mp": 2,
        "attack": 6.5,
        "defense": 5,
        "m_attack": 6.5,
        "m_defense": 5,
        "agility": 4.5,
        "luck": 4.5,
    }

    # 总价值 = Σ (属性值 × 权重)
    total_value = sum(stats.get(key, 0) * weights.get(key, 1.0) for key in BASES)
    # 价格受等级影响，并加入基础价格，最后四舍五入到十位
    price = total_value * max(level / 2.3, 1.2) + 45
    return int(round(price, -1))

def _parse_equipment_stats(equip_def: Dict[str, Any], level: int) -> Dict[str, int]:
    """
    从原始装备定义中解析并计算所有属性值。

    Args:
        equip_def: 从 TOML 文件中读取的单个装备定义。
        level: 装备等级。

    Returns:
        一个包含所有计算后属性值的字典。
    """
    stats: Dict[str, int] = {key: 0 for key in BASES}
    for toml_key, stat_key in TOML_KEY_MAP.items():
        rating = equip_def.get(toml_key)
        if rating:
            stats[stat_key] = generate_stat(level, rating, BASES[stat_key])
    return stats

def generate_equipment_row(equip_def: Dict[str, Any]) -> List[Any]:
    """
    根据单个装备定义生成 CSV 文件中的一行数据。

    Args:
        equip_def: 从 TOML 文件中读取的单个装备定义。

    Returns:
        一个列表，包含 CSV 文件中一行的所有字段值。
    """
    level = equip_def.get("level", 1)
    stats = _parse_equipment_stats(equip_def, level)
    price = calculate_price(stats, level)

    # 清理描述文本中的换行符
    description = equip_def.get("description", "")
    cleaned_description = description.replace("\n", "").replace("\r", "").replace("\\n", "").strip()

    row_data = [
        equip_def.get("id"),
        equip_def.get("name"),
        cleaned_description,
        # equip_def.get("price", 0),
        price,
        equip_def.get("equip_type", 0),
        equip_def.get("weapon_type", 0),
        level,
    ]

    # 按照 CSV_HEADER 中定义的属性顺序添加属性值
    row_data.extend(stats.get(stat_name, 0) for stat_name in BASES)
    return row_data

def load_equipment_from_toml(toml_path: str) -> List[Dict[str, Any]]:
    """
    从 TOML 文件加载装备定义。

    Args:
        toml_path: TOML 文件的路径。

    Returns:
        一个包含所有装备定义的列表。
    """
    data = toml.load(toml_path)
    return data.get("weapon", [])

def generate_equipment_csv(toml_path: str, output_csv_path: Optional[str] = None) -> None:
    """
    从 TOML 文件生成装备数据的 CSV 文件或打印到控制台。

    Args:
        toml_path: 输入的 TOML 文件路径。
        output_csv_path: 输出的 CSV 文件路径。如果为 None，则打印到控制台。
    """
    equipment_defs = load_equipment_from_toml(toml_path)

    rows: List[List[Any]] = [CSV_HEADER]
    for equip in equipment_defs:
        row = generate_equipment_row(equip)
        rows.append(row)

    if output_csv_path:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(rows)
        print(f"[✓] 装备 CSV 已保存至：{output_csv_path}")
    else:
        # 控制台输出时，确保所有单元格都转换为字符串
        for row in rows:
            print(",".join(map(str, row)))

def print_weapon_stat_table():
    ratings = [
        "very_low", "low", "medium", "high", "very_high", "best"
    ]
    levels = range(1, 11)
    sample_stat = "max_hp"

    table = Table(title=f"Weapon '{sample_stat}' 属性表（不同评级 × 等级）", show_lines=True)
    table.add_column("评级/等级", justify="center")
    for lv in levels:
        table.add_column(f"LV{lv}", justify="right")

    for rating in ratings:
        row = [rating]
        for lv in levels:
            stat_val = generate_stat(lv, rating, BASES[sample_stat])
            row.append(str(stat_val))
        table.add_row(*row)

    console.print(table)

if __name__ == "__main__":
    generate_equipment_csv("z666/weapons.toml", "z666/weapons.csv")
    print("\n")
    print_weapon_stat_table()
