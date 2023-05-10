import os
import sys

from entities.bullet import Bullet
from utils.misc import decrease, increase, is_positive, get_image, sign
from utils.parser import get_level, display, sprite_types

import pygame

pygame.init()
pygame.font.init()

ARIAL = pygame.font.SysFont("ARIAL", 12)
LARGE_TEXT = pygame.font.SysFont("ARIAL", 40)

levels = []
level_directory = os.listdir("levels")

for filename in level_directory:
    try:
        id = int(filename.removesuffix(".json"))
    except ValueError:
        pass
    levels.append(id)

MAX_LEVEL = max(levels)


class Game:
    def __init__(self, fps, enable_level_skipping=False) -> None:
        self.screen_width = 900
        self.screen_height = 600

        # self.screen is the actual screen. Everything should be drawn on self.g, because that screen will be resized and drawn onto the real screen
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("can pooper's adventures")
        self.g = self.screen.copy()
        self.objects = {}

        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.entitycount = 1
        self.level = 1
        self.draw_level(self.level)
        self.show_info = False
        self.event_ticker = 0

        self.bullets = pygame.sprite.Group()  # may have to change this later

    # to be called when an entire new level has to be loaded
    def draw_level(self, id):
        layout = get_level(id)
        self.g.fill((255, 255, 255))
        data = display(self.g, layout)
        self.objects.update(data)

    # process keyboard events
    def process_events(self):
        keys = pygame.key.get_pressed()

        if self.event_ticker > 0:
            self.event_ticker -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return

        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.objects['player'].last_bullet_fired > self.objects['player'].firing_cooldown:
                self.bullets.add(Bullet(
                    (self.objects['player'].x, self.objects['player'].y), 1, 15, self.objects['player'].direction, 3000, 33))
                self.objects['player'].last_bullet_fired = current_time
            else:
                return

        if keys[pygame.K_o]:
            if self.event_ticker == 0:
                self.event_ticker = 10
                self.show_info = not self.show_info
        if keys[pygame.K_k]:
            if self.event_ticker == 0 and self.enable_level_skipping:
                self.event_ticker = 10
                self.next_level()

    # move to next level and display
    def next_level(self):
        pygame.display.flip()

        for bullet in self.bullets:
            bullet.kill()

        self.g.fill((255, 255, 255))

        if self.level >= MAX_LEVEL:
            self.level = 1
            self.screen.fill((255, 255, 255))
            w = LARGE_TEXT.render(
                "you win lets goooooooooooo", False, (0, 0, 0))
            self.screen.blit(w, (10, 100))
            pygame.display.flip()
            self.objects["player"].respawn(2000)
        else:
            self.level += 1
            self.objects["player"].respawn(250)

        self.draw_level(self.level)

    def display_game_info(self):
        self.entitycount = 2 + \
            len(self.objects['collidable']) + \
            len(self.objects['fatal']) + len(self.bullets)

        # only reason im keeping this is because i will soon be morally obligated to fix the broken physics
        coordinates = ARIAL.render(
            f"({self.objects['player'].x}, {self.objects['player'].y})", False, (0, 0, 0))
        onground = ARIAL.render(
            f"onGround: {self.objects['player'].on_ground}", False, (0, 0, 0))
        crouching = ARIAL.render(
            f"crouching: {self.objects['player'].crouching}", False, (0, 0, 0))
        direction = ARIAL.render(
            f"facing: {self.objects['player'].direction.upper()}", False, (0, 0, 0))
        fps = ARIAL.render(
            f"FPS: {round(self.clock.get_fps(), 1)}", False, (0, 0, 0))
        entitycount = ARIAL.render(
            f"entityCount: {self.entitycount}", False, (0, 0, 0))
        deaths = ARIAL.render(
            f"deathCount: {self.objects['player'].death_count}", False, (0, 0, 0))

        self.g.blit(coordinates, (10, 10))
        self.g.blit(onground, (10, 25))
        self.g.blit(crouching, (10, 40))
        self.g.blit(direction, (10, 55))
        self.g.blit(fps, (10, 70))
        self.g.blit(entitycount, (10, 85))
        self.g.blit(deaths, (10, 100))

    # Renders everything onto the screen.
    # Executed everything frame.
    def render(self):

        self.player.draw(self.g)
        self.collidables.draw(self.g)
        self.fatal.draw(self.g)
        self.objectives.draw(self.g)
        self.bullets.draw(self.g)
        self.enemies.draw(self.g)
        if self.show_info:
            self.display_game_info()

        self.screen.blit(pygame.transform.scale(
            self.g, self.screen.get_rect().size), (0, 0))
        pygame.display.flip()

    # Updates the game state, and processes input.
    # Executed every frame.
    def update(self):
        if (
                (pygame.sprite.spritecollideany(self.player, self.fatal) or
                 self.player.y > 1000 or self.player.hp <= 0)
                and not self.player.invulnerable
        ):
            for bullet in self.bullets:
                bullet.kill()
            self.draw_level(self.level)
            self.player.die()

        if self.player.has_reached_objective(self.objectives):
            self.next_level()
            return

        for bullet in self.bullets:
            if (
                bullet.x > self.screen_width
                or bullet.x < 0
                or bullet.y > self.screen_height or bullet.y < 0
            ):
                bullet.kill()
            bullet.move(bullet.x_speed, bullet.y_speed, self.collidables)
            bullet.update()

        for enemy in self.enemies:
            enemy.update(self.collidables, self.fatal, self.bullets, self.g)
            for bullet in enemy.bullets:
                self.bullets.add(bullet)

        self.player.update(self.collidables, self.fatal, self.bullets, self.g)

    def loop(self):
        while not self.stopped:
            self.process_events()
            pygame.event.pump()

            self.g.fill((255, 255, 255))

            if (pygame.sprite.spritecollideany(self.objects['player'], self.objects['fatal']) or self.objects['player'].y > 1000 or self.objects['player'].hp <= 0) and not self.objects['player'].invulnerable:
                for bullet in self.bullets:
                    bullet.kill()
                self.draw_level(self.level)
                self.objects['player'].die()

            if self.objects['player'].has_reached_objective(self.objects['objective']):
                self.next_level()
                continue

            self.bullets.update(self.objects)

            for enemy in self.objects['enemy']:
                enemy.update(self.objects, self.bullets, self.g)
                for bullet in enemy.bullets:
                    self.bullets.add(bullet)

            self.objects["player"].update(self.objects, self.bullets, self.g)

            x_offset = self.objects["player"].x - \
                self.screen_width // 2  # subtract
            scene_left = self.objects["player"].x - self.screen_width // 2
            scene_right = self.objects["player"].x + self.screen_width
            for component in self.objects.values():
                if isinstance(component, list) or isinstance(component, pygame.sprite.Group):
                    for obj in component:
                        if scene_left <= obj.x or obj.x + obj.width <= scene_right:
                            obj.draw(self.g, x_offset)
                else:
                    if scene_left <= component.x or component.x + component.width <= scene_right:
                        component.draw(self.g, x_offset)
            for bullet in self.bullets:
                if scene_left <= bullet.x <= scene_right:
                    bullet.draw(self.g, x_offset)

            if self.show_info:
                self.display_game_info()

            self.screen.blit(pygame.transform.scale(
                self.g, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(self.framecap)


if __name__ == "__main__":
    enable_level_skipping = False

    for argument in sys.argv:
        if argument == "--enable-level-skipping":
            enable_level_skipping = True

    window = Game(fps=60, enable_level_skipping=enable_level_skipping)
    pygame.display.set_icon(get_image("assets/canpooper_right.png", 200, 200))
    window.loop()
    pygame.quit()
