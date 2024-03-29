from entities.entity import Entity
import pygame

class Bullet(Entity):
    singular = False
    name = "bullet"

    def __init__(self,
            spawn: tuple,
            team=0,
            speed=100,
            direction="right",
            lifetime=8000,
            damage=10):

        super().__init__("assets/bullet.png", spawn, (15, 5))
        self.team = team
        
        if direction == "right":
            self.x_speed = speed
        else:
            self.x_speed = -speed
        
        self.lifetime = lifetime
        self.life_begin = pygame.time.get_ticks()
        self.damage = damage
    
    def update(self, objects):
        self.move(self.x_speed, self.y_speed, objects['collidable'])
        if pygame.time.get_ticks() - self.life_begin > self.lifetime:
            self.kill()

    def move(self, x, y, collidables):
        dx = x
        dy = y

        if self.colliding_at(dx, dy, collidables):
            self.kill()

        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))
