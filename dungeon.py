from dataclasses import dataclass
from enum import Enum

from settings import MAP_WIDTH, MAP_HEIGHT
from monster import Monster


MAX_FLOOR = 100


class DungeonZone(str, Enum):
    START = "Стартовая зона"
    MID = "Средняя зона"
    DANGER = "Опасная зона"
    TREASURE = "Сокровищница"
    FINAL = "Финальная зона"


@dataclass
class Chest:
    tile_x: int
    tile_y: int
    opened: bool = False
    rare: bool = False


class Dungeon:
    def __init__(self, floor: int = 1):
        self.floor = max(1, min(MAX_FLOOR, floor))
        self.map_data = self.create_map()
        self.zone_map = self.create_zone_map()
        self.monsters = self.create_monsters()
        self.chests = self.create_chests()

    def next_floor(self):
        if self.floor >= MAX_FLOOR:
            return False

        self.floor += 1
        self.map_data = self.create_map()
        self.zone_map = self.create_zone_map()
        self.monsters = self.create_monsters()
        self.chests = self.create_chests()
        return True

    def floor_level(self, bonus: int = 0) -> int:
        return max(1, self.floor + bonus)

    def create_zone_map(self):
        zones = {}

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if x <= 4 and y <= 4:
                    zones[(x, y)] = DungeonZone.START
                elif x <= 8 and y <= 8:
                    zones[(x, y)] = DungeonZone.MID
                elif x <= 11 and y <= 11:
                    zones[(x, y)] = DungeonZone.DANGER
                elif y >= 10 and x <= 7:
                    zones[(x, y)] = DungeonZone.TREASURE
                else:
                    zones[(x, y)] = DungeonZone.FINAL

        return zones

    def get_zone_at(self, x: int, y: int) -> DungeonZone:
        return self.zone_map.get((x, y), DungeonZone.START)

    def create_map(self):
        data = []

        for y in range(MAP_HEIGHT):
            row = []

            for x in range(MAP_WIDTH):
                if x in (0, MAP_WIDTH - 1) or y in (0, MAP_HEIGHT - 1):
                    row.append(0)
                elif (x, y) in {
                    (4, 4),
                    (5, 4),
                    (9, 2),
                    (10, 2),
                    (2, 10),
                    (3, 10),
                }:
                    row.append(0)
                else:
                    row.append(1)

            data.append(row)

        for x, y in [
            (6, 4),
            (7, 4),
            (8, 4),
            (9, 4),
            (4, 9),
            (5, 9),
            (6, 9),
        ]:
            data[y][x] = 2

        return data

    def create_monsters(self):
        floor = self.floor

        monster_sets = [
            ("Slime", 0, 20),
            ("Goblin", 1, 30),
            ("Skeleton", 2, 45),
            ("Orc", 3, 60),
            ("Dark Knight", 4, 80),
            ("Demon", 5, 110),
            ("Dungeon Lord", 6, 150),
        ]

        monsters = []
        positions = [
            (3, 2),
            (5, 3),
            (8, 3),
            (10, 5),
            (7, 8),
            (11, 9),
            (9, 11),
        ]

        for index, ((monster_type, level_bonus, base_hp), position) in enumerate(zip(monster_sets, positions)):
            level = self.floor_level(level_bonus)
            hp = base_hp + floor * 18 + level * 6
            guarding = index >= 2

            monsters.append(
                Monster(
                    position[0],
                    position[1],
                    level,
                    monster_type,
                    hp,
                    guarding=guarding,
                )
            )

        boss_level = self.floor_level(9)
        boss_name = "Ancient Dragon" if floor < MAX_FLOOR else "Повелитель 100-го этажа"
        boss_hp = 240 + floor * 35 + boss_level * 10

        monsters.append(
            Monster(
                12,
                12,
                boss_level,
                boss_name,
                boss_hp,
                guarding=True,
                is_boss=True,
            )
        )

        return monsters

    def create_chests(self):
        return [
            Chest(4, 2, rare=self.floor >= 10),
            Chest(9, 5, rare=True),
            Chest(6, 8, rare=self.floor >= 25),
            Chest(12, 10, rare=True),
            Chest(10, 12, rare=self.floor >= 50),
        ]

    def is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= MAP_WIDTH or y >= MAP_HEIGHT:
            return False

        if self.map_data[y][x] == 0:
            return False

        for monster in self.monsters:
            if monster.alive and monster.tile_x == x and monster.tile_y == y:
                return False

        return True

    def monster_at(self, x: int, y: int):
        for monster in self.monsters:
            if monster.alive and monster.tile_x == x and monster.tile_y == y:
                return monster

        return None

    def chest_at(self, x: int, y: int):
        for chest in self.chests:
            if not chest.opened and chest.tile_x == x and chest.tile_y == y:
                return chest

        return None

    @staticmethod
    def adjacent_positions(x: int, y: int):
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]