import pygame

from dungeon import Dungeon, MAX_FLOOR
from items import generate_boss_loot, generate_loot
from player import Player
from save_system import load_game, save_game
from settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from ui import Renderer


class DungeonGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Dungeon Crawl RPG Prototype")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.player = Player(tile_x=1, tile_y=1)
        self.dungeon = Dungeon()

        self.renderer = Renderer(self.screen, self.player, self.dungeon)

        self.message = "Исследуйте подземелье. Победите босса, чтобы перейти на следующий этаж."
        self.message_timer = 300

        self.inventory_open = False
        self.selected_inventory_index = 0
        self.current_zone = self.dungeon.get_zone_at(self.player.tile_x, self.player.tile_y)

        self.running = True

    def set_message(self, text):
        self.message = text
        self.message_timer = 360

    def try_move_player(self, dx, dy):
        if self.inventory_open:
            return

        new_x = self.player.tile_x + dx
        new_y = self.player.tile_y + dy

        target_monster = self.dungeon.monster_at(new_x, new_y)

        if target_monster:
            self.fight(target_monster)
            return

        if self.dungeon.is_walkable(new_x, new_y):
            self.player.tile_x = new_x
            self.player.tile_y = new_y
            self.check_zone_change()
            self.check_monster_reactions()

    def check_zone_change(self):
        zone = self.dungeon.get_zone_at(self.player.tile_x, self.player.tile_y)

        if zone != self.current_zone:
            self.current_zone = zone
            self.set_message(f"Вы вошли в зону: {zone.value}")

    def check_monster_reactions(self):
        for monster in self.dungeon.monsters:
            if not monster.alive:
                continue

            distance = abs(monster.tile_x - self.player.tile_x) + abs(monster.tile_y - self.player.tile_y)

            if distance <= 1:
                self.fight(monster)
                break

            if distance <= 2 and monster.guarding:
                self.set_message(f"{monster.monster_type} уровня {monster.level} охраняет сокровище!")

    def go_to_next_floor(self):
        if not self.dungeon.next_floor():
            self.set_message("Вы прошли все 100 этажей! Подземелье полностью очищено!")
            return

        self.player.tile_x = 1
        self.player.tile_y = 1
        self.player.hp = min(self.player.max_hp, self.player.hp + self.player.max_hp // 2)

        self.renderer.dungeon = self.dungeon
        self.current_zone = self.dungeon.get_zone_at(self.player.tile_x, self.player.tile_y)

        self.set_message(
            f"Вы спустились на этаж {self.dungeon.floor}/{MAX_FLOOR}. "
            f"Монстры стали сильнее, но старое снаряжение осталось с вами."
        )

    def fight(self, monster):
        if not monster.alive:
            return

        if self.player.combat_level >= monster.level:
            monster.alive = False
            self.player.gain_exp(monster.exp_reward)

            if monster.is_boss:
                loot = generate_boss_loot(monster.level)
                self.player.add_item(loot)

                if self.dungeon.floor >= MAX_FLOOR:
                    self.set_message(
                        f"ФИНАЛЬНЫЙ БОСС ПОБЕЖДЁН! Получено: {loot.name}. "
                        f"Вы очистили все 100 этажей!"
                    )
                    return

                self.go_to_next_floor()
                return

            loot = generate_loot(monster.level, from_monster=True)
            self.player.add_item(loot)

            self.set_message(
                f"Победа над {monster.monster_type} ур. {monster.level}! "
                f"Этаж: {self.dungeon.floor}/{MAX_FLOOR}. "
                f"Ваш боевой уровень: {self.player.combat_level}. "
                f"Получено: {loot.name}, опыт: {monster.exp_reward}."
            )
        else:
            damage = max(5, monster.level * 7 - self.player.defense * 2)
            self.player.hp -= damage

            if self.player.hp <= 0:
                self.player.hp = max(1, self.player.max_hp // 3)
                self.player.tile_x = 1
                self.player.tile_y = 1
                self.check_zone_change()

                self.set_message(
                    f"{monster.monster_type} ур. {monster.level} слишком силён. "
                    f"Этаж: {self.dungeon.floor}/{MAX_FLOOR}. "
                    f"Ваш боевой уровень: {self.player.combat_level}. "
                    f"Вы очнулись в начале этажа."
                )
            else:
                self.set_message(
                    f"{monster.monster_type} ур. {monster.level} сильнее вас! "
                    f"Этаж: {self.dungeon.floor}/{MAX_FLOOR}. "
                    f"Ваш боевой уровень: {self.player.combat_level}. "
                    f"Потеряно HP: {damage}."
                )

    def open_nearby_chest(self):
        if self.inventory_open:
            return

        for x, y in self.dungeon.adjacent_positions(self.player.tile_x, self.player.tile_y):
            chest = self.dungeon.chest_at(x, y)

            if chest:
                chest.opened = True

                loot_level = max(
                    self.dungeon.floor,
                    self.player.level + (3 if chest.rare else 0),
                )

                loot = generate_loot(
                    level=loot_level,
                    from_monster=False,
                    rare=chest.rare,
                )

                self.player.add_item(loot)

                chest_type = "редкий сундук" if chest.rare else "сундук"
                self.set_message(f"Открыт {chest_type}. Предмет добавлен в инвентарь: {loot.name}.")
                return

        self.set_message("Рядом нет закрытого сундука.")

    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open
        self.selected_inventory_index = 0

        if self.inventory_open:
            self.set_message("Инвентарь открыт. ↑/↓ выбрать, Enter экипировать/использовать.")
        else:
            self.set_message("Инвентарь закрыт.")

    def move_inventory_selection(self, direction):
        if not self.inventory_open or not self.player.inventory:
            return

        self.selected_inventory_index += direction
        self.selected_inventory_index %= len(self.player.inventory)

    def equip_selected_item(self):
        if not self.inventory_open:
            return

        if not self.player.inventory:
            self.set_message("Инвентарь пуст.")
            return

        item = self.player.inventory[self.selected_inventory_index]
        result = self.player.equip_item(item)
        self.set_message(result)

        if self.selected_inventory_index >= len(self.player.inventory):
            self.selected_inventory_index = max(0, len(self.player.inventory) - 1)

    def save_current_game(self):
        save_game(
            player=self.player,
            dungeon_floor=self.dungeon.floor,
            monsters=self.dungeon.monsters,
            chests=self.dungeon.chests,
        )

        self.set_message("Прогресс сохранён.")

    def load_saved_game(self):
        loaded_data = load_game()

        if loaded_data is None:
            self.set_message("Файл сохранения не найден.")
            return

        self.player, dungeon_floor, monsters, chests = loaded_data
        self.dungeon = Dungeon(floor=dungeon_floor)
        self.dungeon.monsters = monsters
        self.dungeon.chests = chests

        self.renderer.player = self.player
        self.renderer.dungeon = self.dungeon
        self.current_zone = self.dungeon.get_zone_at(self.player.tile_x, self.player.tile_y)

        self.set_message("Прогресс загружен.")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.toggle_inventory()
                elif event.key == pygame.K_RETURN:
                    self.equip_selected_item()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if self.inventory_open:
                        self.move_inventory_selection(-1)
                    else:
                        self.try_move_player(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.inventory_open:
                        self.move_inventory_selection(1)
                    else:
                        self.try_move_player(0, 1)
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    self.try_move_player(-1, 0)
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.try_move_player(1, 0)
                elif event.key == pygame.K_e:
                    self.open_nearby_chest()
                elif event.key == pygame.K_F5:
                    self.save_current_game()
                elif event.key == pygame.K_l:
                    self.load_saved_game()
                elif event.key == pygame.K_ESCAPE:
                    if self.inventory_open:
                        self.toggle_inventory()
                    else:
                        self.running = False

    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        self.renderer.draw(
            self.message,
            self.message_timer,
            self.inventory_open,
            self.selected_inventory_index,
            self.current_zone,
        )

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = DungeonGame()
    game.run()