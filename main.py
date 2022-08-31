#!/usr/bin/env python3.10

import os
import time
import numpy as np
try:
    import pygame
except ImportError:
    print("Forcibly installing PyGame on your computer wtihout your consent...")
    if os.name == "nt":
        os.system("py3 -m pip install pygame")
        os.system("echo 🤡 imagine being on windows")
    else:
        os.system("python3 -m pip install pygame")

pygame.init()
pygame.font.init()

class Entity(pygame.sprite.Sprite):
    def __init__(self, image = "assets/none.png", x = 0, y = 0, width = 100, height = 100, show_hitbox = False):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = [x + width/2, y + height/2]

        self.x = x
        self.y = y

        self.width = width
        self.height = height
        
        self.hitbox = show_hitbox

    def draw(self, screen):
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color(255, 0, 0), self.rect, width = 5)
        center = np.array(self.rect.center) - (self.width/2, self.height/2)
        screen.blit(self.image, list(center))

class Player(Entity):
    def __init__(self, x, y, width = 100, height = 200, hitbox = False):
        super().__init__("assets/canpooper.png", x, y, width, height, hitbox)
        self.x_speed = 0
        self.y_speed = 0
        self.max_x_speed = 5
        self.gravity = 1

        self.respawn_x = x
        self.respawn_y = y

        self.jump_power = 1.5

        self.crouching = False
        self.on_ground = False
    
    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(0, dy, collidables):
            dy -= np.sign(dy)
        while self.colliding_at(dx, dy, collidables):
            dx -= np.sign(dx)
        
        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))
    
    def colliding_at(self, x, y, entities):
        # returns group of entities
        self.rect.move_ip((x, y))
        colliding = pygame.sprite.spritecollideany(self, entities)
        self.rect.move_ip((-x, -y))
        return colliding
    
    def is_on_ground(self, entities):
        for entity in entities:
            if (entity.rect.top == self.rect.bottom) and (entity.rect.left <= self.rect.left <= entity.rect.right or entity.rect.left <= self.rect.right <= entity.rect.right or (self.rect.left <= entity.rect.left and self.rect.right >= entity.rect.right)):
                return True
        return False
    
    def hitting_ceiling(self, entities):
        for entity in entities:
            if (entity.rect.bottom == self.rect.top) and (entity.rect.left <= self.rect.left <= entity.rect.right or entity.rect.left <= self.rect.right <= entity.rect.right or (self.rect.left <= entity.rect.left and self.rect.right >= entity.rect.right)):
                return True
        return False
    
    def has_reached_objective(self, objectives):
        return pygame.sprite.spritecollideany(self, objectives) is not None
    
    def update(self, collidables, fatal):
        if pygame.sprite.spritecollideany(self, fatal):
            self.die(0)

        keys = pygame.key.get_pressed()
        self.on_ground = self.is_on_ground(collidables)
        hitting_ceiling = self.hitting_ceiling(collidables)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x_speed = -self.max_x_speed
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x_speed = self.max_x_speed
        
        if not self.on_ground:
            if self.y_speed < 15:
                self.y_speed += self.gravity
        else:
            self.y_speed = 0

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.crouching and self.on_ground:
            self.y_speed = -self.jump_power * 10
        
        self.crouching = False

        if (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.on_ground:
            self.x_speed *= 0.6
            self.crouching = True
        
        self.move(self.x_speed, self.y_speed, collidables)
        self.x_speed = 0
    
    def die(self, timeout):
        pygame.time.wait(timeout)
        self.x_speed = 0
        self.y_speed = 0
        self.rect.move_ip((self.respawn_x - self.x, self.respawn_y - self.y))
        self.x = self.respawn_x
        self.y = self.respawn_y

class Crate(Entity):
    def __init__(self, x, y, width=200, height=200, hitbox=False):
        super().__init__("assets/crate.png", x, y, width, height, hitbox)

class Lava(Entity):
    def __init__(self, x, y, width=960, height=100, hitbox=False):
        super().__init__("assets/lava.png", x, y, width, height, hitbox)

class Objective(Entity):
    def __init__(self, x, y, width=100, height=100, hitbox=False):
        super().__init__("assets/burger.png", x, y, width, height, hitbox)

class Game:
    def __init__(self, fps) -> None:
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("can pooper's adventures")
        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.player = Player(100, 50, 100, 100)

        self.collidables = pygame.sprite.Group()
        self.collidables.add(Crate(100, 200, 100, 100))
        self.collidables.add(Crate(400, 200, 100, 100))
        self.collidables.add(Crate(700, 200, 100, 100))

        self.fatal = pygame.sprite.Group()
        self.fatal.add(Lava(0, 540, 960, 100))

        self.objectives = pygame.sprite.Group()
        self.objectives.add(Objective(800, 100, 100, 100))
    
    def process_events(self):
        # process keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
    
    def loop(self):
        while not self.stopped:
            self.process_events()

            pygame.event.pump()
            
            self.screen.fill((255, 255, 255))
            
            if self.player.has_reached_objective(self.objectives):
                message = large_text.render("congratulations you won", False, (0, 0, 0))
                self.screen.blit(message, (10, 200))
                pygame.display.flip()
                self.player.die(1000)
            
            self.player.update(self.collidables, self.fatal)
            
            self.player.draw(self.screen)
            self.collidables.draw(self.screen)
            self.fatal.draw(self.screen)
            self.objectives.draw(self.screen)
            
            coordinates = arial.render(f"({self.player.x}, {self.player.y})", False, (0, 0, 0))
            onground = arial.render(f"onGround: {self.player.on_ground}", False, (0, 0, 0))
            crouching = arial.render(f"crouching: {self.player.crouching}", False, (0, 0, 0))
            
            self.screen.blit(coordinates, (10, 10))
            self.screen.blit(onground, (10, 25))
            self.screen.blit(crouching, (10, 40))

            pygame.display.flip()
            
            self.clock.tick(self.framecap)

if __name__ == "__main__":
    h = Game(fps=56)
    arial = pygame.font.SysFont("Arial", 12)
    large_text = pygame.font.SysFont("Arial", 40)
    h.loop()

"""
50
69.1831
89.8968
111.7841
135.0282
158.7998
183.9250
210.4039
"""