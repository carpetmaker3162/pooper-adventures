#!/usr/bin/env python3.10

import os
import time
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

sign = lambda a: -1 if (abs(a) != a) else 1

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width = 100, height = 100):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

class Player(Entity):
    def __init__(self, x, y, width = 100, height = 200):
        super().__init__("assets/Sports-Ball-Transparent.png", x, y, width, height)
        self.x_speed = 0
        self.y_speed = 0
        self.max_x_speed = 1
        self.gravity = 9.807

        self.jump_power = 1
        
        self.width = width
        self.height = height

        print(self.rect.bottom)
        print(self.rect.top)
    
    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(0, dy, collidables):
            dy -= sign(dy)

        while self.colliding_at(dx, dy, collidables):
            dx -= sign(dx)

        self.rect.move_ip((dx, dy))
    
    def colliding_at(self, x, y, collidables):
        # returns group of entities
        self.rect.move_ip((x, y))
        colliding = pygame.sprite.spritecollideany(self, collidables)
        self.rect.move_ip((-x, -y))
        return colliding
    
    def on_ground(self, collidables):
        for entity in collidables:
            if (entity.rect.top <= (self.rect.bottom + self.height / 2)) and (entity.rect.left >= self.rect.right or entity.rect.right <= self.rect.left):
                return True
        return False
    
    def hitting_ceiling(self, collidables):
        for entity in collidables:
            if (entity.rect.bottom >= self.rect.top) and (entity.rect.left >= self.rect.right or entity.rect.right <= self.rect.left):
                return True
        return False
    
    def update(self, collidables):
        keys = pygame.key.get_pressed()
        # if self.on_ground(collidables) or self.hitting_ceiling(collidables):
        #     self.y_speed = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            pass
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            pass
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y_speed = -self.jump_power * 10
        
        if not self.on_ground(collidables) and self.y_speed < 20:
            self.y_speed += self.gravity * 0.06
        
        self.move(self.x_speed, self.y_speed, collidables)

class Crate(Entity):
    def __init__(self, x, y):
        super().__init__("assets/crate.png", x, y)
        print(self.rect.bottom)
        print(self.rect.top)

class Game:
    def __init__(self, fps) -> None:
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("can pooper's adventures in Poopland")
        self.clock = pygame.time.Clock()
        self.stopped = False
        self.framecap = fps
        self.player = Player(100, 100, 100, 100)

        self.collidables = pygame.sprite.Group()
        self.collidables.add(Crate(100, 400))
    
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
            self.player.update(self.collidables)
            self.player.draw(self.screen)
            self.collidables.draw(self.screen)
            
            pygame.display.flip()
            
            self.clock.tick(self.framecap)

if __name__ == "__main__":
    h = Game(60)
    h.loop()