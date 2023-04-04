from src.entity import Entity
from src.bullet import Bullet
import pygame

class Enemy(Entity):
    def __init__(
            self,
            image="assets/none.png",
            width=100,
            height=100,
            show_hitbox=False,
            type=0,
            team=2,
            hp=50,
            meleedamage=25,
            bulletdamage=10,
            startx=0,
            starty=0,
            firing_right=False,
            firing_cooldown=1000):

        """
        Arguments:
        image:          path of image
        width:          width of sprite in px
        height:         height of sprite in px
        show_hitbox:    show hitbox or no
        type:           denotes the type of the enemy (see next section)
        team:           usually 2 (Enemy team)
        hp:             health points for entity
        meleedamage:    damage dealt when touching the hitbox of the enemy
        bulletdamage:   damage dealt by its bullets
        """
        
        super().__init__(image, startx, starty, width, height, show_hitbox, hp)
        self.direction = 0 # 0 if going towards end, 1 if going towards start
        self.firing_right = firing_right
        self.firing_cooldown = firing_cooldown
        self.team = team
        self.hp = hp
        self.meleedamage = meleedamage
        self.bulletdamage = bulletdamage

        self.bullets = pygame.sprite.Group()
        self.last_bullet_fired = -float("inf")
        
    
    def update(self, collidables, fatal, bullets, screen):
        super().update(collidables, fatal, bullets, screen)

        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_bullet_fired >= self.firing_cooldown:
            self.bullets.add(Bullet(self.x, self.y, self.team, 15, int(self.firing_right), False, 3000, 10))
            self.last_bullet_fired = current_time
        
        for bullet in self.bullets:
            bullet.move(bullet.x_speed, bullet.y_speed, collidables)
            bullet.update()
        
        self.bullets.draw(screen)
