import os
import sys
from utils import logs, decrease, increase, is_positive, get_image, sign
import pygame
from src.player import Player
from src.entity import Entity
from src.bullet import Bullet
from src.enemy import Enemy
from src.props import Crate, Objective, Lava

pygame.init()
pygame.font.init()

ARIAL = pygame.font.SysFont("ARIAL", 12)
LARGE_TEXT = pygame.font.SysFont("ARIAL", 40)

class Game:
    def __init__(self, fps) -> None:
        self.screen_width = 900
        self.screen_height = 600
        
        # self.screen is the actual screen. Everything should be drawn on self.g, because that screen will be resized and drawn onto the real screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("can pooper's adventures")
        self.g = self.screen.copy()

        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.player = Player(100, 50, 50, 50, False, 100)
        self.entitycount = 1

        self.collidables = pygame.sprite.Group()
        self.collidables.add(Crate(100, 250, 100, 100, False))
        self.collidables.add(Crate(300, 150, 50, 50, False))
        self.collidables.add(Crate(350, 150, 50, 50, False))
        self.collidables.add(Crate(400, 200, 100, 100, False))
        self.collidables.add(Crate(600, 100, 50, 50, False))
        self.collidables.add(Crate(650, 100, 50, 50, False))
        self.collidables.add(Crate(700, 300, 100, 100, False))

        self.fatal = pygame.sprite.Group()
        self.fatal.add(Lava(0, 540, 960, 100))

        self.bullets = pygame.sprite.Group()

        self.objectives = pygame.sprite.Group()
        self.objectives.add(Objective(800, 450, 100, 100))
       
        self.enemies = pygame.sprite.Group()
        self.enemies.add(Enemy("assets/canpooper_left.png", 50, 50, False, 1, 2, 50, 25, 30, 850, 250, False, 100))

    def process_events(self):
        # process keyboard events
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
        
        if keys[pygame.K_SPACE]:
            current_time = pygame.time.get_ticks()
            if current_time - self.player.last_bullet_fired > self.player.firing_cooldown:
                self.bullets.add(Bullet(self.player.x, self.player.y, 1, 15, self.player.facing_right, False, 3000, 33))
                self.player.last_bullet_fired = current_time
            else:
                return

    def loop(self):
        while not self.stopped:
            self.process_events()
            pygame.event.pump()

            self.enemy_bullets = pygame.sprite.Group()

            self.g.fill((255, 255, 255))
            
            # draw grid
            for i in range(0, 900, 100):
                for j in range(0, 1800, 100):
                    rect = pygame.Rect(i, j, 100, 100)
                    pygame.draw.rect(self.g, (230, 230, 230), rect, 1)

            if self.player.has_reached_objective(self.objectives):
                pygame.display.flip()
                self.player.respawn(250)
            
            for bullet in self.bullets:
                if (bullet.x > self.screen_width + 100 or bullet.x < -100) or bullet.y > (self.screen_height + 100 or bullet.y < -100):
                    bullet.kill()
                bullet.move(bullet.x_speed, bullet.y_speed, self.collidables)
                bullet.update()
            
            for enemy in self.enemies:
                enemy.update(self.collidables, self.fatal, self.bullets, self.g)
                for bullet in enemy.bullets:
                    self.bullets.add(bullet)

            self.player.update(self.collidables, self.fatal, self.bullets, self.g)

            self.player.draw(self.g)
            self.collidables.draw(self.g)
            self.fatal.draw(self.g)
            self.objectives.draw(self.g)
            self.bullets.draw(self.g)
            self.enemies.draw(self.g)
            
            self.entitycount = 1 + len(self.collidables) + len(self.fatal) + len(self.objectives) + len(self.bullets)
            coordinates = ARIAL.render(
                f"({self.player.x}, {self.player.y})", False, (0, 0, 0))
            onground = ARIAL.render(
                f"onGround: {self.player.on_ground}", False, (0, 0, 0))
            crouching = ARIAL.render(
                f"crouching: {self.player.crouching}", False, (0, 0, 0))
            direction = ARIAL.render(
                f"facing: {'RIGHT' if self.player.facing_right else 'LEFT'}", False, (0, 0, 0))
            fps = ARIAL.render(
                f"FPS: {round(self.clock.get_fps(), 1)}", False, (0, 0, 0))
            entitycount = ARIAL.render(
                f"entityCount: {self.entitycount}", False, (0, 0, 0))
            deaths = ARIAL.render(
                f"deathCount: {self.player.death_count}", False, (0, 0, 0))

            self.g.blit(coordinates, (10, 10))
            self.g.blit(onground, (10, 25))
            self.g.blit(crouching, (10, 40))
            self.g.blit(direction, (10, 55))
            self.g.blit(fps, (10, 70))
            self.g.blit(entitycount, (10, 85))
            self.g.blit(deaths, (10, 100))
            
            self.screen.blit(pygame.transform.scale(self.g, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(self.framecap)


if __name__ == "__main__":
    h = Game(fps=60)
    h.loop()
