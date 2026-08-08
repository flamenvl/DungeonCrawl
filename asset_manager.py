import os

import pygame

from settings import (
    ASSETS_DIR,
    CHEST_SPRITE_SIZE,
    ITEM_SPRITE_SIZE,
    MONSTER_SPRITE_SIZE,
    PLAYER_SPRITE_SIZE,
    TILE_HEIGHT,
    TILE_WIDTH,
)


class AssetManager:
    def __init__(self):
        self.images = {}
        self.load_all()

    def load_all(self):
        self.images["floor"] = self.load_image(
            "tiles/floor.png",
            (TILE_WIDTH, TILE_HEIGHT + 24),
            self.create_floor_sprite,
        )

        self.images["bridge"] = self.load_image(
            "tiles/bridge.png",
            (TILE_WIDTH, TILE_HEIGHT + 24),
            self.create_bridge_sprite,
        )

        self.images["player"] = self.load_image(
            "characters/player.png",
            PLAYER_SPRITE_SIZE,
            self.create_player_sprite,
        )

        self.images["slime"] = self.load_image(
            "monsters/slime.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (95, 210, 95)),
        )

        self.images["goblin"] = self.load_image(
            "monsters/goblin.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (220, 150, 70)),
        )

        self.images["skeleton"] = self.load_image(
            "monsters/skeleton.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (205, 205, 195)),
        )

        self.images["orc"] = self.load_image(
            "monsters/orc.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (95, 170, 80)),
        )

        self.images["dark_knight"] = self.load_image(
            "monsters/dark_knight.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (120, 80, 180)),
        )

        self.images["demon"] = self.load_image(
            "monsters/demon.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (210, 65, 80)),
        )

        self.images["dungeon_lord"] = self.load_image(
            "monsters/dungeon_lord.png",
            MONSTER_SPRITE_SIZE,
            lambda size: self.create_monster_sprite(size, (150, 40, 220)),
        )

        self.images["chest"] = self.load_image(
            "objects/chest.png",
            CHEST_SPRITE_SIZE,
            lambda size: self.create_chest_sprite(size, rare=False, opened=False),
        )

        self.images["rare_chest"] = self.load_image(
            "objects/rare_chest.png",
            CHEST_SPRITE_SIZE,
            lambda size: self.create_chest_sprite(size, rare=True, opened=False),
        )

        self.images["opened_chest"] = self.load_image(
            "objects/opened_chest.png",
            CHEST_SPRITE_SIZE,
            lambda size: self.create_chest_sprite(size, rare=False, opened=True),
        )

        self.images["sword"] = self.load_image(
            "items/sword.png",
            ITEM_SPRITE_SIZE,
            self.create_sword_sprite,
        )

        self.images["light_glow"] = self.load_image(
            "effects/light_glow.png",
            (360, 360),
            self.create_light_glow,
        )

    def load_image(self, relative_path, size, fallback_factory):
        path = os.path.join(ASSETS_DIR, relative_path)

        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(image, size)

        return fallback_factory(size)

    def get(self, name):
        return self.images[name]

    def create_floor_sprite(self, size):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)

        top = [
            (width // 2, 0),
            (width, TILE_HEIGHT // 2),
            (width // 2, TILE_HEIGHT),
            (0, TILE_HEIGHT // 2),
        ]

        left = [
            (0, TILE_HEIGHT // 2),
            (width // 2, TILE_HEIGHT),
            (width // 2, height),
            (0, TILE_HEIGHT // 2 + 24),
        ]

        right = [
            (width, TILE_HEIGHT // 2),
            (width // 2, TILE_HEIGHT),
            (width // 2, height),
            (width, TILE_HEIGHT // 2 + 24),
        ]

        pygame.draw.polygon(surface, (68, 68, 88), left)
        pygame.draw.polygon(surface, (50, 50, 70), right)
        pygame.draw.polygon(surface, (105, 105, 125), top)
        pygame.draw.polygon(surface, (35, 35, 50), top, 2)

        for offset in range(12, width, 24):
            pygame.draw.line(
                surface,
                (88, 88, 108),
                (offset, TILE_HEIGHT // 2),
                (width // 2, TILE_HEIGHT),
                1,
            )

        return surface

    def create_bridge_sprite(self, size):
        width, height = size
        surface = self.create_floor_sprite(size)

        overlay = pygame.Surface(size, pygame.SRCALPHA)

        top = [
            (width // 2, 0),
            (width, TILE_HEIGHT // 2),
            (width // 2, TILE_HEIGHT),
            (0, TILE_HEIGHT // 2),
        ]

        pygame.draw.polygon(overlay, (120, 86, 54, 120), top)
        pygame.draw.line(overlay, (175, 130, 75), top[0], top[2], 2)
        pygame.draw.line(overlay, (175, 130, 75), top[1], top[3], 2)

        surface.blit(overlay, (0, 0))
        return surface

    def create_player_sprite(self, size):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)

        cx = width // 2

        pygame.draw.ellipse(surface, (0, 0, 0, 90), (cx - 20, height - 18, 40, 12))

        pygame.draw.polygon(
            surface,
            (70, 115, 210),
            [
                (cx, 34),
                (cx - 20, 62),
                (cx - 14, 86),
                (cx + 14, 86),
                (cx + 20, 62),
            ],
        )

        pygame.draw.circle(surface, (232, 204, 170), (cx, 25), 12)

        pygame.draw.polygon(
            surface,
            (80, 55, 35),
            [
                (cx - 14, 20),
                (cx, 8),
                (cx + 14, 20),
                (cx + 10, 14),
                (cx - 8, 14),
            ],
        )

        pygame.draw.rect(surface, (180, 205, 255), (cx - 11, 47, 22, 22), border_radius=5)
        pygame.draw.line(surface, (220, 220, 245), (cx + 20, 46), (cx + 32, 22), 4)
        pygame.draw.circle(surface, (90, 130, 220), (cx - 20, 56), 9)

        return surface

    def create_monster_sprite(self, size, color):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)

        cx = width // 2

        pygame.draw.ellipse(surface, (0, 0, 0, 90), (cx - 22, height - 16, 44, 12))

        pygame.draw.circle(surface, color, (cx, height // 2), 23)
        pygame.draw.circle(surface, self.lighten(color, 35), (cx - 8, height // 2 - 8), 5)
        pygame.draw.circle(surface, self.lighten(color, 35), (cx + 8, height // 2 - 8), 5)
        pygame.draw.circle(surface, (20, 15, 20), (cx - 8, height // 2 - 8), 2)
        pygame.draw.circle(surface, (20, 15, 20), (cx + 8, height // 2 - 8), 2)

        pygame.draw.polygon(
            surface,
            self.darken(color, 40),
            [
                (cx - 14, height // 2 + 8),
                (cx - 3, height // 2 + 17),
                (cx + 14, height // 2 + 8),
            ],
        )

        return surface

    def create_chest_sprite(self, size, rare=False, opened=False):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)

        body = (204, 126, 40) if not rare else (190, 70, 235)
        trim = (255, 218, 95)

        pygame.draw.ellipse(surface, (0, 0, 0, 80), (8, height - 12, width - 16, 9))

        if opened:
            pygame.draw.rect(surface, (90, 58, 32), (12, 22, width - 24, 18), border_radius=4)
            pygame.draw.polygon(
                surface,
                (135, 82, 35),
                [
                    (14, 20),
                    (width - 14, 14),
                    (width - 10, 22),
                    (16, 28),
                ],
            )
            return surface

        pygame.draw.rect(surface, body, (10, 18, width - 20, 24), border_radius=4)
        pygame.draw.rect(surface, trim, (8, 13, width - 16, 12), border_radius=6)
        pygame.draw.rect(surface, (90, 55, 25), (width // 2 - 5, 25, 10, 12), border_radius=2)
        pygame.draw.line(surface, trim, (14, 30), (width - 14, 30), 2)

        return surface

    def create_sword_sprite(self, size):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)

        pygame.draw.line(surface, (220, 230, 245), (width - 12, 8), (15, height - 15), 5)
        pygame.draw.line(surface, (120, 135, 155), (width - 18, 14), (21, height - 9), 2)
        pygame.draw.line(surface, (120, 80, 45), (18, height - 22), (28, height - 12), 6)
        pygame.draw.circle(surface, (255, 210, 90), (14, height - 10), 5)

        return surface

    def create_light_glow(self, size):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center = (width // 2, height // 2)

        for radius in range(width // 2, 0, -8):
            alpha = int(55 * (1 - radius / (width // 2)))
            pygame.draw.circle(surface, (255, 190, 90, alpha), center, radius)

        return surface

    @staticmethod
    def lighten(color, amount):
        return tuple(min(255, channel + amount) for channel in color)

    @staticmethod
    def darken(color, amount):
        return tuple(max(0, channel - amount) for channel in color)