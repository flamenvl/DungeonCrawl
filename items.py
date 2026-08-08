import random
from dataclasses import dataclass
from enum import Enum


class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    GOLD = "gold"
    ARTIFACT = "artifact"


class ItemRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Item:
    name: str
    item_type: ItemType
    level: int
    attack_bonus: int = 0
    defense_bonus: int = 0
    hp_bonus: int = 0
    gold_amount: int = 0
    rarity: ItemRarity = ItemRarity.COMMON

    def stats_text(self) -> str:
        parts = []

        if self.attack_bonus:
            parts.append(f"+{self.attack_bonus} атака")

        if self.defense_bonus:
            parts.append(f"+{self.defense_bonus} защита")

        if self.hp_bonus:
            parts.append(f"+{self.hp_bonus} HP")

        if self.gold_amount:
            parts.append(f"{self.gold_amount} золота")

        return ", ".join(parts) if parts else "без характеристик"


def generate_boss_loot(level: int) -> Item:
    attack_bonus = level * 5 + random.randint(10, 20)
    defense_bonus = max(1, level // 2)

    return Item(
        name=f"Легендарный клинок босса ур. {level}",
        item_type=ItemType.WEAPON,
        level=level,
        attack_bonus=attack_bonus,
        defense_bonus=defense_bonus,
        rarity=ItemRarity.LEGENDARY,
    )


def generate_loot(level: int, from_monster: bool = False, rare: bool = False) -> Item:
    roll = random.random()

    rarity = ItemRarity.COMMON

    if level >= 70:
        rarity = ItemRarity.LEGENDARY if rare else ItemRarity.EPIC
    elif level >= 40:
        rarity = ItemRarity.EPIC if rare else ItemRarity.RARE
    elif level >= 15:
        rarity = ItemRarity.RARE if rare else ItemRarity.COMMON
    elif rare:
        rarity = ItemRarity.RARE

    if rare:
        if roll < 0.45:
            return Item(
                name=f"Клинок глубин ур. {level}",
                item_type=ItemType.WEAPON,
                level=level,
                attack_bonus=level * 4 + random.randint(4, 10),
                rarity=rarity,
            )

        if roll < 0.85:
            return Item(
                name=f"Доспех хранителя ур. {level}",
                item_type=ItemType.ARMOR,
                level=level,
                defense_bonus=level * 3 + random.randint(3, 8),
                rarity=rarity,
            )

        return Item(
            name=f"Артефакт древнего подземелья ур. {level}",
            item_type=ItemType.ARTIFACT,
            level=level,
            attack_bonus=level * 2,
            defense_bonus=level * 2,
            hp_bonus=level * 8,
            rarity=ItemRarity.EPIC if level < 70 else ItemRarity.LEGENDARY,
        )

    if from_monster:
        if roll < 0.45:
            gold = random.randint(10, 30) * level
            return Item(
                name=f"{gold} золота",
                item_type=ItemType.GOLD,
                level=level,
                gold_amount=gold,
            )

        if roll < 0.7:
            hp = 20 + level * 5
            return Item(
                name=f"Зелье лечения +{hp} HP",
                item_type=ItemType.POTION,
                level=level,
                hp_bonus=hp,
                rarity=rarity,
            )

        if roll < 0.85:
            return Item(
                name=f"Меч этажа {level}",
                item_type=ItemType.WEAPON,
                level=level,
                attack_bonus=level * 3 + random.randint(1, 6),
                rarity=rarity,
            )

        return Item(
            name=f"Броня этажа {level}",
            item_type=ItemType.ARMOR,
            level=level,
            defense_bonus=level * 2 + random.randint(1, 5),
            rarity=rarity,
        )

    if roll < 0.5:
        return Item(
            name=f"Оружие из сундука ур. {level}",
            item_type=ItemType.WEAPON,
            level=level,
            attack_bonus=level * 3 + random.randint(2, 8),
            rarity=rarity,
        )

    return Item(
        name=f"Броня из сундука ур. {level}",
        item_type=ItemType.ARMOR,
        level=level,
        defense_bonus=level * 2 + random.randint(2, 7),
        rarity=rarity,
    )