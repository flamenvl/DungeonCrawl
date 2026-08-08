from dataclasses import dataclass

from items import Item, ItemType


@dataclass
class Player:
    tile_x: int
    tile_y: int
    level: int = 2
    exp: int = 0
    exp_to_next: int = 100
    max_hp: int = 40
    hp: int = 40
    base_attack: int = 5
    base_defense: int = 2
    gold: int = 0
    weapon: Item | None = None
    armor: Item | None = None
    inventory: list[Item] | None = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

    @property
    def equipment_level_bonus(self) -> int:
        bonus = 0

        if self.weapon:
            bonus += max(1, self.weapon.attack_bonus // 6)

        if self.armor:
            bonus += max(1, self.armor.defense_bonus // 5)

        for item in self.inventory:
            if item.item_type == ItemType.ARTIFACT:
                bonus += max(1, (item.attack_bonus + item.defense_bonus + item.hp_bonus // 5) // 8)

        return bonus

    @property
    def combat_level(self) -> int:
        return self.level + self.equipment_level_bonus

    @property
    def attack(self) -> int:
        weapon_bonus = self.weapon.attack_bonus if self.weapon else 0
        artifact_bonus = sum(
            item.attack_bonus
            for item in self.inventory
            if item.item_type == ItemType.ARTIFACT
        )
        return self.base_attack + weapon_bonus + artifact_bonus

    @property
    def defense(self) -> int:
        armor_bonus = self.armor.defense_bonus if self.armor else 0
        artifact_bonus = sum(
            item.defense_bonus
            for item in self.inventory
            if item.item_type == ItemType.ARTIFACT
        )
        return self.base_defense + armor_bonus + artifact_bonus

    def gain_exp(self, amount: int):
        self.exp += amount

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp_to_next = int(self.exp_to_next * 1.35)
        self.max_hp += 12
        self.hp = self.max_hp
        self.base_attack += 2
        self.base_defense += 1

    def add_item(self, item: Item):
        if item.item_type == ItemType.GOLD:
            self.gold += item.gold_amount
            return

        if item.item_type == ItemType.POTION:
            self.inventory.append(item)
            return

        self.inventory.append(item)

    def equip_item(self, item: Item) -> str:
        old_combat_level = self.combat_level

        if item.item_type == ItemType.WEAPON:
            self.weapon = item
            level_diff = self.combat_level - old_combat_level
            return f"Экипировано оружие: {item.name}. Боевой уровень: +{level_diff}"

        if item.item_type == ItemType.ARMOR:
            self.armor = item
            level_diff = self.combat_level - old_combat_level
            return f"Экипирована броня: {item.name}. Боевой уровень: +{level_diff}"

        if item.item_type == ItemType.POTION:
            self.hp = min(self.max_hp, self.hp + item.hp_bonus)

            if item in self.inventory:
                self.inventory.remove(item)

            return f"Использовано зелье: {item.name}"

        if item.item_type == ItemType.ARTIFACT:
            return f"Артефакт уже усиливает боевой уровень: {item.name}"

        return "Этот предмет нельзя экипировать."