from entities.entity import Entity
from entities.bullet import Bullet
from utils.misc import image_paths
import pygame

class Enemy(Entity):
    singular = False
    name = "enemy"

    def __init__(self,
            image=image_paths["enemy"],
            spawn=(0, 0),
            size=(100, 100),
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
        super().__init__(image, spawn, size, hp)
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
            self.bullets.add(Bullet((self.x, self.y), self.team, 15, self.direction, 3000, self.bullet_damage))
            self.last_bullet_fired = current_time
        
        self.bullets.draw(screen)

