import pygame
from src.entity import Entity

class Bullet(Entity):
    def __init__(
            self, 
            x,
            y,
            team=0,
            speed=100,
            direction=0,
            lifetime=8000,
            damage=10,
            screen_width=900,
            screen_height=600):

        """
        Arguments:
        x:              start x
        y:              start y
        Directions:
        0 = left
        1 = right
        """
        super().__init__("assets/bullet.png", x, y, 15, 5)
        self.team = team
        
        if direction:
            self.x_speed = speed
        else:
            self.x_speed = -speed
        
        self.lifetime = lifetime
        self.life_begin = pygame.time.get_ticks()
        self.damage = damage
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def update(self):
        if pygame.time.get_ticks() - self.life_begin > self.lifetime \
            or (self.x > self.screen_width + 100 or self.x < -100) or self.y > (self.screen_height + 100 or self.y < -100):
            self.kill()
