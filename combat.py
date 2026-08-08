import random
from dataclasses import dataclass, field

from items import ItemType


@dataclass
class CombatLog:
    lines: list[str] = field(default_factory=list)

    def add(self, text: str):
        self.lines.append(text)
        self.lines = self.lines[-6:]


class CombatAction:
    ATTACK = "attack"
    HEAVY_ATTACK = "heavy_attack"
    DEFEND = "defend"
    POTION = "potion"
    RUN = "run"


class CombatSystem:
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster
        self.monster.reset_combat_hp()

        self.player_defending = False
        self.finished = False
        self.victory = False
        self.escaped = False

        self.log = CombatLog()
        self.log.add(f"Начался бой: {monster.monster_type} ур. {monster.level}!")

    @property
    def player_crit_chance(self) -> float:
        weapon_bonus = 0.04 if self.player.weapon else 0
        level_bonus = min(0.12, self.player.level * 0.008)
        return 0.08 + weapon_bonus + level_bonus

    @property
    def player_dodge_chance(self) -> float:
        armor_penalty = 0.03 if self.player.armor else 0
        level_bonus = min(0.10, self.player.level * 0.006)
        return max(0.04, 0.10 + level_bonus - armor_penalty)

    def get_first_potion(self):
        for item in self.player.inventory:
            if item.item_type == ItemType.POTION:
                return item

        return None

    def perform_action(self, action: str):
        if self.finished:
            return

        self.player_defending = False

        if action == CombatAction.ATTACK:
            self.player_attack(multiplier=1.0, accuracy=0.92, action_name="атака")
            if not self.finished:
                self.monster_turn()

        elif action == CombatAction.HEAVY_ATTACK:
            self.player_attack(multiplier=1.6, accuracy=0.68, action_name="сильный удар")
            if not self.finished:
                self.monster_turn()

        elif action == CombatAction.DEFEND:
            self.player_defending = True
            self.log.add("Вы заняли защитную стойку.")
            self.monster_turn()

        elif action == CombatAction.POTION:
            self.use_potion()
            if not self.finished:
                self.monster_turn()

        elif action == CombatAction.RUN:
            self.try_run()

    def player_attack(self, multiplier: float, accuracy: float, action_name: str):
        if random.random() > accuracy:
            self.log.add(f"Ваш {action_name} промахнулся!")
            return

        if random.random() < self.monster.dodge_chance:
            self.log.add(f"{self.monster.monster_type} уклонился!")
            return

        damage = int((self.player.attack * multiplier) - self.monster.defense)
        damage = max(1, damage)

        critical = random.random() < self.player_crit_chance

        if critical:
            damage = int(damage * 1.8)

        self.monster.current_hp -= damage
        self.monster.current_hp = max(0, self.monster.current_hp)

        if critical:
            self.log.add(f"КРИТ! Вы нанесли {damage} урона.")
        else:
            self.log.add(f"Вы нанесли {damage} урона.")

        if self.monster.current_hp <= 0:
            self.finished = True
            self.victory = True
            self.monster.alive = False
            self.log.add(f"{self.monster.monster_type} побеждён!")

    def monster_turn(self):
        if self.finished:
            return

        if random.random() < self.player_dodge_chance:
            self.log.add("Вы уклонились от атаки!")
            return

        damage = self.monster.attack - self.player.defense
        damage = max(1, damage)

        if self.player_defending:
            damage = max(1, damage // 2)

        critical = random.random() < self.monster.crit_chance

        if critical:
            damage = int(damage * 1.7)

        self.player.hp -= damage
        self.player.hp = max(0, self.player.hp)

        if critical:
            self.log.add(f"КРИТ врага! Вы получили {damage} урона.")
        else:
            self.log.add(f"Враг нанёс {damage} урона.")

        if self.player.hp <= 0:
            self.finished = True
            self.victory = False
            self.log.add("Вы проиграли бой!")

    def use_potion(self):
        potion = self.get_first_potion()

        if potion is None:
            self.log.add("У вас нет зелий.")
            return

        self.player.hp = min(self.player.max_hp, self.player.hp + potion.hp_bonus)
        self.player.inventory.remove(potion)

        self.log.add(f"Вы выпили зелье и восстановили {potion.hp_bonus} HP.")

    def try_run(self):
        if self.monster.is_boss:
            self.log.add("От босса нельзя сбежать!")
            self.monster_turn()
            return

        run_chance = 0.55 + max(0, self.player.level - self.monster.level) * 0.08
        run_chance = min(0.85, run_chance)

        if random.random() < run_chance:
            self.finished = True
            self.escaped = True
            self.victory = False
            self.log.add("Вы успешно сбежали из боя.")
        else:
            self.log.add("Побег не удался!")
            self.monster_turn()