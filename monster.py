from dataclasses import dataclass


@dataclass
class Monster:
    tile_x: int
    tile_y: int
    level: int
    monster_type: str
    hp: int
    alive: bool = True
    guarding: bool = False
    is_boss: bool = False

    def __post_init__(self):
        self.max_hp = self.hp
        self.current_hp = self.hp

    @property
    def exp_reward(self) -> int:
        if self.is_boss:
            return 400 + self.level * 50

        return 40 + self.level * 25

    @property
    def attack(self) -> int:
        base = 4 + self.level * 3

        if self.is_boss:
            base += self.level * 2

        return base

    @property
    def defense(self) -> int:
        base = 1 + self.level

        if self.is_boss:
            base += 4

        return base

    @property
    def crit_chance(self) -> float:
        return 0.08 + min(0.12, self.level * 0.01)

    @property
    def dodge_chance(self) -> float:
        return 0.04 + min(0.10, self.level * 0.006)

    def reset_combat_hp(self):
        if not hasattr(self, "current_hp"):
            self.current_hp = self.hp

        if not hasattr(self, "max_hp"):
            self.max_hp = self.hp