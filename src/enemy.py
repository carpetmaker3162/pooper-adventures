from src.entity import Entity
from src.bullet import Bullet
import pygame

class Enemy(Entity):
    def __init__(self,
            image="assets/none.png",
            x=0,
            y=0,
            width=100,
            height=100,
            hp=50,
            bullet_damage=10,
            facing="left",
            firing_cooldown=1000):

        """
        Arguments:
        image:          path of image
        width:          width of sprite in px
        height:         height of sprite in px
        hp:             health points for entity
        bullet_damage:   damage dealt by its bullets
        """
        super().__init__(image, x, y, width, height, hp)
        self.direction = facing
        self.firing_cooldown = firing_cooldown
        self.team = 2
        self.hp = hp
        self.bullet_damage = bullet_damage

        self.bullets = pygame.sprite.Group()
        self.last_bullet_fired = -float("inf")
        self.facing = facing
    
    def update(self, collidables, fatal, bullets, screen):
        super().update(collidables, fatal, bullets, screen)

        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_bullet_fired >= self.firing_cooldown:
            self.bullets.add(Bullet(self.x, self.y, self.team, 15, self.direction, 3000, self.bullet_damage))
            self.last_bullet_fired = current_time
        
        self.bullets.draw(screen)

