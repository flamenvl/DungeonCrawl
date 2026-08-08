import math

import pygame

from asset_manager import AssetManager
from items import ItemType
from settings import (
    BG_COLOR,
    GOLD_COLOR,
    GREEN,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TEXT_COLOR,
    TILE_HEIGHT,
    TILE_WIDTH,
)


class Renderer:
    def __init__(self, screen, player, dungeon):
        self.screen = screen
        self.player = player
        self.dungeon = dungeon
        self.assets = AssetManager()

        self.camera_x = SCREEN_WIDTH // 2
        self.camera_y = 90

        self.font = pygame.font.SysFont("arial", 18)
        self.big_font = pygame.font.SysFont("arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("arial", 14)

    def tile_to_screen(self, tile_x, tile_y):
        screen_x = (tile_x - tile_y) * TILE_WIDTH // 2 + self.camera_x
        screen_y = (tile_x + tile_y) * TILE_HEIGHT // 2 + self.camera_y
        return screen_x, screen_y

    def rarity_color(self, rarity):
        colors = {
            "common": (220, 220, 220),
            "rare": (80, 160, 255),
            "epic": (190, 90, 255),
            "legendary": (255, 180, 50),
        }

        return colors.get(str(rarity.value if hasattr(rarity, "value") else rarity), TEXT_COLOR)

    def draw_background(self):
        self.screen.fill(BG_COLOR)

        for i in range(18):
            x = 80 + i * 78
            y = 620 + int(math.sin(i) * 12)
            pygame.draw.circle(self.screen, (28, 28, 42), (x, y), 50)

        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (120, 80, 220, 40), (900, 210), 260)
        pygame.draw.circle(glow_surface, (255, 180, 80, 30), (520, 300), 220)

        self.screen.blit(glow_surface, (0, 0))

    def draw_light_effect(self, tile_x, tile_y, alpha=130):
        sx, sy = self.tile_to_screen(tile_x, tile_y)
        glow = self.assets.get("light_glow").copy()
        glow.set_alpha(alpha)

        rect = glow.get_rect(center=(sx, sy + TILE_HEIGHT // 2))
        self.screen.blit(glow, rect)

    def draw_tile(self, x, y, tile_type):
        sx, sy = self.tile_to_screen(x, y)

        sprite_name = "bridge" if tile_type == 2 else "floor"
        sprite = self.assets.get(sprite_name)

        rect = sprite.get_rect()
        rect.midtop = (sx, sy)

        self.screen.blit(sprite, rect)

    def draw_player(self):
        sx, sy = self.tile_to_screen(self.player.tile_x, self.player.tile_y)
        sprite = self.assets.get("player")

        rect = sprite.get_rect()
        rect.midbottom = (sx, sy + TILE_HEIGHT + 4)

        self.screen.blit(sprite, rect)

        if self.player.weapon:
            sword = self.assets.get("sword")
            sword_rect = sword.get_rect()
            sword_rect.center = (sx + 28, sy + 28)
            self.screen.blit(sword, sword_rect)

        level_text = self.small_font.render(f"Lv {self.player.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, level_text.get_rect(center=(sx, rect.top - 8)))

    def get_monster_sprite_name(self, monster):
        monster_name = monster.monster_type.lower().replace(" ", "_")

        if monster_name in {
            "slime",
            "goblin",
            "skeleton",
            "orc",
            "dark_knight",
            "demon",
            "dungeon_lord",
        }:
            return monster_name

        return "dungeon_lord" if monster.is_boss else "slime"

    def draw_monster(self, monster):
        if not monster.alive:
            return

        sx, sy = self.tile_to_screen(monster.tile_x, monster.tile_y)

        if monster.is_boss:
            self.draw_light_effect(monster.tile_x, monster.tile_y, alpha=110)

        sprite = self.assets.get(self.get_monster_sprite_name(monster))

        rect = sprite.get_rect()
        rect.midbottom = (sx, sy + TILE_HEIGHT + 2)

        if monster.is_boss:
            boss_sprite = pygame.transform.smoothscale(
                sprite,
                (int(sprite.get_width() * 1.35), int(sprite.get_height() * 1.35)),
            )
            rect = boss_sprite.get_rect()
            rect.midbottom = (sx, sy + TILE_HEIGHT + 6)
            self.screen.blit(boss_sprite, rect)
        else:
            self.screen.blit(sprite, rect)

        label_color = GOLD_COLOR if monster.is_boss else GREEN if self.player.level >= monster.level else RED
        label = f"BOSS Lv {monster.level}" if monster.is_boss else f"Lv {monster.level}"
        level_text = self.font.render(label, True, label_color)

        bg_rect = level_text.get_rect(center=(sx, rect.top - 10))
        bg_rect.inflate_ip(12, 6)

        pygame.draw.rect(self.screen, (18, 18, 28), bg_rect, border_radius=6)
        pygame.draw.rect(self.screen, label_color, bg_rect, 1, border_radius=6)

        self.screen.blit(level_text, level_text.get_rect(center=bg_rect.center))

    def draw_chest(self, chest):
        sx, sy = self.tile_to_screen(chest.tile_x, chest.tile_y)

        if chest.opened:
            sprite = self.assets.get("opened_chest")
        elif chest.rare:
            sprite = self.assets.get("rare_chest")
        else:
            sprite = self.assets.get("chest")

        rect = sprite.get_rect()
        rect.midbottom = (sx, sy + TILE_HEIGHT + 2)

        self.screen.blit(sprite, rect)

        if not chest.opened and chest.rare:
            self.draw_light_effect(chest.tile_x, chest.tile_y, alpha=80)

    def draw_dungeon(self):
        drawables = []

        for y, row in enumerate(self.dungeon.map_data):
            for x, tile_type in enumerate(row):
                if tile_type != 0:
                    drawables.append(("tile", x, y, tile_type))

        for chest in self.dungeon.chests:
            drawables.append(("chest", chest.tile_x, chest.tile_y, chest))

        for monster in self.dungeon.monsters:
            drawables.append(("monster", monster.tile_x, monster.tile_y, monster))

        drawables.append(("player", self.player.tile_x, self.player.tile_y, self.player))

        drawables.sort(key=lambda obj: obj[1] + obj[2])

        for drawable in drawables:
            kind = drawable[0]

            if kind == "tile":
                _, x, y, tile_type = drawable
                self.draw_tile(x, y, tile_type)
            elif kind == "chest":
                self.draw_chest(drawable[3])
            elif kind == "monster":
                self.draw_monster(drawable[3])
            elif kind == "player":
                self.draw_player()

    def draw_ui_panel(self, current_zone):
        panel_rect = pygame.Rect(20, 20, 360, 260)

        pygame.draw.rect(self.screen, (24, 24, 36), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (90, 90, 120), panel_rect, 2, border_radius=12)

        title = self.big_font.render("Dungeon Crawl", True, GOLD_COLOR)
        self.screen.blit(title, (40, 32))

        floor_text = self.small_font.render(f"Этаж: {self.dungeon.floor}/100", True, GOLD_COLOR)
        self.screen.blit(floor_text, (40, 62))

        zone_text = self.small_font.render(f"Зона: {current_zone.value}", True, (180, 210, 255))
        self.screen.blit(zone_text, (40, 80))

        stats = [
            f"Уровень: {self.player.level}",
            f"Боевой уровень: {self.player.combat_level}",
            f"Бонус экипировки: +{self.player.equipment_level_bonus}",
            f"Опыт: {self.player.exp}/{self.player.exp_to_next}",
            f"HP: {self.player.hp}/{self.player.max_hp}",
            f"Атака: {self.player.attack}",
            f"Защита: {self.player.defense}",
            f"Золото: {self.player.gold}",
        ]

        y = 106

        for stat in stats:
            text = self.font.render(stat, True, TEXT_COLOR)
            self.screen.blit(text, (40, y))
            y += 22

        weapon = self.player.weapon.name if self.player.weapon else "нет"
        armor = self.player.armor.name if self.player.armor else "нет"

        weapon_text = self.small_font.render(f"Оружие: {weapon}", True, (210, 230, 255))
        armor_text = self.small_font.render(f"Броня: {armor}", True, (210, 230, 255))

        self.screen.blit(weapon_text, (40, 282))
        self.screen.blit(armor_text, (40, 300))

    def get_item_level_bonus(self, item):
        if item.item_type == ItemType.WEAPON:
            return max(1, item.attack_bonus // 6)

        if item.item_type == ItemType.ARMOR:
            return max(1, item.defense_bonus // 5)

        if item.item_type == ItemType.ARTIFACT:
            return max(1, (item.attack_bonus + item.defense_bonus + item.hp_bonus // 5) // 8)

        return 0

    def get_item_comparison_text(self, item):
        item_level_bonus = self.get_item_level_bonus(item)

        if item.item_type == ItemType.WEAPON:
            current_attack = self.player.weapon.attack_bonus if self.player.weapon else 0
            current_level_bonus = self.get_item_level_bonus(self.player.weapon) if self.player.weapon else 0

            attack_diff = item.attack_bonus - current_attack
            level_diff = item_level_bonus - current_level_bonus

            return f"Атака {'+' if attack_diff >= 0 else ''}{attack_diff}, боевой уровень {'+' if level_diff >= 0 else ''}{level_diff}"

        if item.item_type == ItemType.ARMOR:
            current_defense = self.player.armor.defense_bonus if self.player.armor else 0
            current_level_bonus = self.get_item_level_bonus(self.player.armor) if self.player.armor else 0

            defense_diff = item.defense_bonus - current_defense
            level_diff = item_level_bonus - current_level_bonus

            return f"Защита {'+' if defense_diff >= 0 else ''}{defense_diff}, боевой уровень {'+' if level_diff >= 0 else ''}{level_diff}"

        if item.item_type == ItemType.POTION:
            return f"Использование: восстановит {item.hp_bonus} HP"

        if item.item_type == ItemType.ARTIFACT:
            return f"Артефакт даёт боевой уровень +{item_level_bonus}"

        return ""

    def draw_inventory(self, selected_index):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(260, 80, 760, 560)
        pygame.draw.rect(self.screen, (26, 26, 40), panel, border_radius=14)
        pygame.draw.rect(self.screen, (120, 120, 160), panel, 2, border_radius=14)

        title = self.big_font.render("Инвентарь", True, GOLD_COLOR)
        self.screen.blit(title, (panel.x + 28, panel.y + 24))

        help_text = self.small_font.render("↑/↓ — выбрать | Enter — экипировать/использовать | I/Esc — закрыть", True, (190, 190, 210))
        self.screen.blit(help_text, (panel.x + 28, panel.y + 58))

        if not self.player.inventory:
            empty = self.font.render("Инвентарь пуст.", True, TEXT_COLOR)
            self.screen.blit(empty, (panel.x + 28, panel.y + 110))
            return

        start_y = panel.y + 100

        for index, item in enumerate(self.player.inventory):
            y = start_y + index * 34

            if y > panel.bottom - 120:
                break

            selected = index == selected_index

            if selected:
                select_rect = pygame.Rect(panel.x + 20, y - 4, panel.width - 40, 30)
                pygame.draw.rect(self.screen, (55, 55, 85), select_rect, border_radius=8)

            color = self.rarity_color(item.rarity)
            equipped_marker = ""

            if self.player.weapon is item:
                equipped_marker = " [оружие]"

            if self.player.armor is item:
                equipped_marker = " [броня]"

            line = f"{index + 1}. {item.name}{equipped_marker}"
            text = self.font.render(line, True, color)
            self.screen.blit(text, (panel.x + 34, y))

            stats = self.small_font.render(item.stats_text(), True, (210, 210, 220))
            self.screen.blit(stats, (panel.x + 420, y + 3))

        selected_item = self.player.inventory[selected_index]
        details_box = pygame.Rect(panel.x + 24, panel.bottom - 110, panel.width - 48, 82)

        pygame.draw.rect(self.screen, (18, 18, 30), details_box, border_radius=10)
        pygame.draw.rect(self.screen, self.rarity_color(selected_item.rarity), details_box, 1, border_radius=10)

        name_text = self.font.render(selected_item.name, True, self.rarity_color(selected_item.rarity))
        self.screen.blit(name_text, (details_box.x + 18, details_box.y + 12))

        stats_text = self.small_font.render(selected_item.stats_text(), True, TEXT_COLOR)
        self.screen.blit(stats_text, (details_box.x + 18, details_box.y + 38))

        comparison_text = self.small_font.render(self.get_item_comparison_text(selected_item), True, (180, 220, 255))
        self.screen.blit(comparison_text, (details_box.x + 18, details_box.y + 58))


    def draw_message(self, message, message_timer):
        if message_timer <= 0:
            return

        box = pygame.Rect(400, SCREEN_HEIGHT - 90, 840, 60)

        pygame.draw.rect(self.screen, (24, 24, 36), box, border_radius=12)
        pygame.draw.rect(self.screen, (100, 100, 130), box, 2, border_radius=12)

        text = self.font.render(message, True, TEXT_COLOR)
        self.screen.blit(text, (box.x + 20, box.y + 20))

    def draw_controls(self):
        lines = [
            "WASD / стрелки — движение",
            "E — открыть сундук",
            "I — инвентарь",
            "Enter — экипировать",
            "F5 — сохранить",
            "L — загрузить",
        ]

        x = SCREEN_WIDTH - 310
        y = 24

        for line in lines:
            text = self.small_font.render(line, True, (190, 190, 210))
            self.screen.blit(text, (x, y))
            y += 20

    def draw(self, message, message_timer, inventory_open=False, selected_inventory_index=0, current_zone=None):
        self.draw_background()

        for chest in self.dungeon.chests:
            if chest.rare and not chest.opened:
                self.draw_light_effect(chest.tile_x, chest.tile_y, alpha=55)

        self.draw_dungeon()

        if current_zone is not None:
            self.draw_ui_panel(current_zone)

        self.draw_controls()
        self.draw_message(message, message_timer)

        if inventory_open:
            self.draw_inventory(selected_inventory_index)

        pygame.display.flip()