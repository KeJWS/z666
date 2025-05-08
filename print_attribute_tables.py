import random
from rich.console import Console
from rich.table import Table

console = Console()

# 保持输出稳定（可选）
random.seed(42)

# 属性列表（来自 BASES）
ATTRIBUTES = [
    "max_hp", "max_mp",
    "attack", "defense",
    "m_attack", "m_defense",
    "agility", "luck"
]

# 属性评级缩放因子（与现有一致）
ATTRIBUTE_SCALE = {
    "decrease_more": (-0.75, -0.5),
    "decrease": (-0.5, -0.3),
    "decrease_little": (-0.25, -0.1),
    "very_low": (0.3, 0.5),
    "low": (0.5, 0.75),
    "medium": (0.7, 1),
    "high": (1.2, 1.5),
    "very_high": (1.7, 2.5),
    "best": (2.9, 3.5),
}

# 每项属性每级基础成长值
BASES = {
    "max_hp": 50,
    "max_mp": 30,
    "attack": 10,
    "defense": 10,
    "m_attack": 10,
    "m_defense": 10,
    "agility": 10,
    "luck": 10,
}

def generate_stat(level: int, rating: str, base_per_level: int) -> int:
    """根据等级、评级、基础值生成数值"""
    if rating in ATTRIBUTE_SCALE:
        factor = random.uniform(*ATTRIBUTE_SCALE[rating])
        return int(level * base_per_level * factor)
    return 0

def print_attribute_tables():
    ratings = list(ATTRIBUTE_SCALE.keys())
    levels = range(1, 11)

    for attr in ATTRIBUTES:
        table = Table(title=f"[bold cyan]{attr} 属性表[/bold cyan]（评级 × 等级）", show_lines=True)
        table.add_column("评级/等级", justify="center")
        for lv in levels:
            table.add_column(f"Lv{lv}", justify="right")

        for rating in ratings:
            row = [rating]
            for lv in levels:
                val = generate_stat(lv, rating, BASES[attr])
                row.append(str(val))
            table.add_row(*row)

        console.print(table)
        console.print("\n")

if __name__ == "__main__":
    print_attribute_tables()
