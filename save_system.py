import json
import os
from dataclasses import asdict

from dungeon import Chest
from items import Item, ItemRarity, ItemType
from monster import Monster
from player import Player
from settings import SAVE_FILE


def item_from_dict(data: dict) -> Item:
    return Item(
        name=data["name"],
        item_type=ItemType(data["item_type"]),
        level=data["level"],
        attack_bonus=data.get("attack_bonus", 0),
        defense_bonus=data.get("defense_bonus", 0),
        hp_bonus=data.get("hp_bonus", 0),
        gold_amount=data.get("gold_amount", 0),
        rarity=ItemRarity(data.get("rarity", ItemRarity.COMMON)),
    )


def monster_from_dict(data: dict) -> Monster:
    monster = Monster(
        tile_x=data["tile_x"],
        tile_y=data["tile_y"],
        level=data["level"],
        monster_type=data["monster_type"],
        hp=data["hp"],
        alive=data.get("alive", True),
        guarding=data.get("guarding", False),
        is_boss=data.get("is_boss", False),
    )

    monster.max_hp = data.get("max_hp", monster.hp)
    monster.current_hp = data.get("current_hp", monster.hp)

    return monster


def save_game(player: Player, dungeon_floor: int, monsters: list[Monster], chests: list[Chest]):
    data = {
        "dungeon_floor": dungeon_floor,
        "player": {
            "tile_x": player.tile_x,
            "tile_y": player.tile_y,
            "level": player.level,
            "exp": player.exp,
            "exp_to_next": player.exp_to_next,
            "max_hp": player.max_hp,
            "hp": player.hp,
            "base_attack": player.base_attack,
            "base_defense": player.base_defense,
            "gold": player.gold,
            "weapon": asdict(player.weapon) if player.weapon else None,
            "armor": asdict(player.armor) if player.armor else None,
            "inventory": [asdict(item) for item in player.inventory],
        },
        "monsters": [asdict(monster) for monster in monsters],
        "chests": [asdict(chest) for chest in chests],
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None

    with open(SAVE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    dungeon_floor = data.get("dungeon_floor", 1)

    player_data = data["player"]

    player = Player(
        tile_x=player_data["tile_x"],
        tile_y=player_data["tile_y"],
        level=player_data["level"],
        exp=player_data["exp"],
        exp_to_next=player_data["exp_to_next"],
        max_hp=player_data["max_hp"],
        hp=player_data["hp"],
        base_attack=player_data["base_attack"],
        base_defense=player_data["base_defense"],
        gold=player_data["gold"],
        inventory=[],
    )

    if player_data["weapon"]:
        player.weapon = item_from_dict(player_data["weapon"])

    if player_data["armor"]:
        player.armor = item_from_dict(player_data["armor"])

    player.inventory = [
        item_from_dict(item_data)
        for item_data in player_data["inventory"]
    ]

    monsters = [
        monster_from_dict(monster_data)
        for monster_data in data["monsters"]
    ]

    chests = [
        Chest(**chest_data)
        for chest_data in data["chests"]
    ]

    return player, dungeon_floor, monsters, chests