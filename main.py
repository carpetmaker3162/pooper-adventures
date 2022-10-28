#!/usr/bin/env python3.10

"""
To-do list:
- Implement HP and HP bars
- Add enemies
- Try to add global score system (looking almost impossible right now)
- Add a relative coordinate system
- Add a level encoding/parsing system
- Add music & SFX
"""

import os
import sys
import numpy as np
from utilities import get_image

try:
    import pygame
except ImportError:
    print("Forcibly installing PyGame on your computer wtihout your consent...")
    if os.name == "nt":
        os.system("py3 -m pip install pygame")
        print("🤡 imagine being on windows")
    else:
        os.system("python3 -m pip install pygame")

    import pygame

pygame.init()
pygame.font.init()

NULLIMAGE = pygame.image.load("assets/none.png")
ARIAL = pygame.font.SysFont("ARIAL", 12)
LARGE_TEXT = pygame.font.SysFont("ARIAL", 40)

"""
Team ID
0 = objects
1 = player
2 = enemy
"""

class Entity(pygame.sprite.Sprite):
    def __init__(self, image=NULLIMAGE, x=0, y=0, width=100, height=100, show_hitbox=False, hp=sys.maxsize, hp_bar_size=None, team=0):
        super().__init__()

        self.image = get_image(image, width, height)
        self.rect = self.image.get_rect()
        self.rect.center = [x + width/2, y + height/2]
        self.team = team
        
        if not hp_bar_size:
            self.hp_bar_size = width
        else:
            self.hp_bar_size = hp_bar_size

        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.invulnerable = False
        self.damage_delay = 500
        self.last_hit_by_bullet = -sys.maxsize
        
        self.hp = hp
        self.max_hp = self.hp

        if hp == sys.maxsize: # invulnerable if initialized with hp = sys.maxsize
            self.invulnerable = True
        
        self.width = width
        self.height = height

        self.hitbox = show_hitbox
        
    def draw(self, screen):
        if self.hitbox:
            pygame.draw.rect(screen, pygame.Color(
                255, 0, 0), self.rect, width=5)
        center = np.array(self.rect.center) - (self.width/2, self.height/2)
        screen.blit(self.image, list(center))
    
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
    
    def update(self, collidables, fatal, bullets, screen):
        if self.hp != self.max_hp and not self.invulnerable:
            self.draw_hp_bar(screen)
        if not self.invulnerable:
            for bullet in pygame.sprite.spritecollide(self, bullets, False): # iterating through all the colliding bullets. if this causes lag use a different way
                if bullet.team != self.team:
                    self.hp -= bullet.damage
                    bullet.kill()
        if self.hp < 0 and not self.invulnerable:
            self.kill()
    
    def draw_hp_bar(self, screen: pygame.Surface):
        pos = (self.x - ((self.hp_bar_size - self.width) / 2), self.y - 15)
        size = (self.hp_bar_size, 10)
        pygame.draw.rect(screen, (0, 0, 0), (pos, size), 1)
        bar_pos = (pos[0] + 3, pos[1] + 3)
        bar_size = ((size[0] - 6) * (self.hp / self.max_hp), size[1] - 6)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_pos, *bar_size))


class Player(Entity):
    def __init__(self, x, y, width=100, height=200, hitbox=False, hp=100):
        super().__init__("assets/jin.png", x, y, width, height, hitbox, hp, None, 1)

        # initing stuff
        self.left_image = get_image(
            "assets/jin.png", width, height)
        self.right_image = get_image(
            "assets/jin.png", width, height)
        self.respawn_x = x
        self.respawn_y = y
        self.x_acceleration = 0.5
        self.last_bullet_fired = -sys.maxsize
        self.death_count = 0

        # --- stats you can mess around with ---
        self.max_x_speed = 5                # max x-velocity
        self.terminal_velocity = 20         # max y-velocity
        self.ground_x_acceleration = 0.5    # x-acceleration on the ground
        self.air_x_acceleration = 0.2       # x-acceleration in the air
        self.gravity = 0.98                 # y-acceleration
        self.jump_power = 1.5               # how far up the player jumps initially
        self.firing_cooldown = 330          # gun cooldown in ms
        self.max_hp = hp                    # health points
        # --------------------------------------

        # player states
        self.crouching = False
        self.on_ground = False
        self.facing_right = True
        self.hp = self.max_hp

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

    def update(self, collidables, fatal, bullets, screen):
        super().update(collidables, fatal, bullets, screen)
        
        if (pygame.sprite.spritecollideany(self, fatal) or self.y > 2000 or self.hp <= 0) and not self.invulnerable:
            self.die()

        keys = pygame.key.get_pressed()
        no_keys_pressed = not any(keys)

        self.on_ground = self.is_on_ground(collidables)
        hitting_ceiling = self.hitting_ceiling(collidables)


        if not self.on_ground:
            # when player is in the air
            self.x_acceleration = self.air_x_acceleration
            if self.y_speed < self.terminal_velocity:
                self.y_speed += self.gravity
        else:
            # when player is on the ground
            self.y_speed = 0
            self.x_acceleration = self.ground_x_acceleration


        if hitting_ceiling:
            # when there is an entity directly above the player
            self.y_speed = -self.y_speed * 0.6  # bounce


        if no_keys_pressed and self.facing_right:
            # de-accelerate to the right
            self.x_speed -= self.x_acceleration
            if self.x_speed < 0:
                self.x_speed = 0
        elif no_keys_pressed and not self.facing_right:
            # de-accelerate to the left
            self.x_speed += self.x_acceleration
            if self.x_speed > 0:
                self.x_speed = 0


        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            # moving left
            self.facing_right = False
            self.x_speed -= self.x_acceleration
            if self.x_speed < -self.max_x_speed:
                self.x_speed = -self.max_x_speed  # Reduce speed to max speed


        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            # moving right
            self.facing_right = True
            self.x_speed += self.x_acceleration
            if self.x_speed > self.max_x_speed:
                self.x_speed = self.max_x_speed  # Reduce speed to max speed


        if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.crouching and self.on_ground:
            # jumping
            self.y_speed = -self.jump_power * 10

        self.crouching = False


        if (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.on_ground:
            # crouching
            self.x_speed *= 0.7
            self.crouching = True

        # change player image
        if self.facing_right:
            self.image = self.right_image
        else:
            self.image = self.left_image

        # has to round because floatingpoint imprecision causes issues with pygames coordinate system or something.
        # fix if a better way is found
        self.move(round(self.x_speed), round(self.y_speed), collidables)
    
    def respawn(self, timeout):
        pygame.time.wait(timeout)
        self.x_speed = 0
        self.y_speed = 0
        self.rect.move_ip((self.respawn_x - self.x, self.respawn_y - self.y))
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.hp = self.max_hp
    
    def die(self):
        self.death_count += 1
        self.respawn(1)


class Crate(Entity):
    def __init__(self, x, y, width=200, height=200, hitbox=False):
        super().__init__("assets/crate.png", x, y, width, height, hitbox, sys.maxsize, 0)


class Lava(Entity):
    def __init__(self, x, y, width=960, height=100, hitbox=False):
        super().__init__("assets/lava.png", x, y, width, height, hitbox, sys.maxsize, 0)


class Objective(Entity):
    def __init__(self, x, y, width=100, height=100, hitbox=False):
        super().__init__("assets/burger2.png", x, y, width, height, hitbox, sys.maxsize, 0)


class Bullet(Entity):
    def __init__(self, x, y, team=0, speed=100, direction=0, hitbox=False, lifetime = 8000, damage = 10, screen_width=900, screen_height=600):
        """
        0 = left
        1 = right
        """
        super().__init__("assets/bullet.png", x, y, 15, 5, hitbox)
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


class Enemy(Entity):
    def __init__(self, 
            image="assets/none.png", 
            width=100, 
            height=100, 
            show_hitbox=False, 
            type=0, 
            team=2, 
            hp=50, 
            meleedamage=25, 
            bulletdamage=10, 
            cycle=3000, 
            startx=100, 
            starty=100, 
            endx=200, 
            endy=100, 
            firing_right=False, 
            firing_cooldown=1000):
        """
        Arguments:
        type:           denotes the type of the enemy (see next section)
        team:           usually 2 (Enemy team)
        hp:             health points for entity
        meleedamage:    damage dealt when touching the hitbox of the enemy
        bulletdamage:   damage dealt by its bullets
        cycle:          how long the Enemy takes to complete 1 walk from start coordinates to end coordinates (below) in ms
        startx:         start x (Enemy will always complete cycle )
        starty:         start y
        endx:           end x
        endy:           end y (if Enemy does not move just set all start and end values to the same)
        
        Types (denoted with `type` argument)
        0: just moves around and tries to deal melee damage
        1: shoots in 1 direction
        2: shoots in 2 directions
        """
        
        super().__init__(image, startx, starty, width, height, show_hitbox, hp)
        self.direction = 0 # 0 if going towards end, 1 if going towards start
        self.firing_right = firing_right
        self.firing_cooldown = firing_cooldown
        self.type = type
        self.team = team
        self.hp = hp
        self.meleedamage = meleedamage
        self.bulletdamage = bulletdamage
        self.cycle = cycle
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy
        self.dx, self.dy = (endx - startx, endy - starty)

        self.bullets = pygame.sprite.Group()
        self.last_bullet_fired = -sys.maxsize

        # pygame.time.set_timer(self.toggle_direction, self.cycle)
    
    def toggle_direction(self):
        self.direction = 1 - self.direction

    def update(self, collidables, fatal, bullets, screen, fps):
        super().update(collidables, fatal, bullets, screen)
        try:
            stepx, stepy = self.dx / (fps * self.cycle / 1000), self.dy / (fps * self.cycle / 1000) ## continue this later
        except ZeroDivisionError:
            # In the moments when the game is loading, the FPS is 0 which leads to division by zero. this shouldnt cause any issues
            return
        
        #if self.rect.left == self.endx and self.rect.top == self.endy:
        #    self.direction = 1
        #elif self.rect.left == self.startx and self.rect.top == self.starty:
        #    self.direction = 0

        if self.direction == 0:
            self.rect.move_ip((round(stepx), round(stepy)))
            self.x += round(stepx)
            self.y += round(stepy)
        else:
            self.rect.move_ip((-round(stepx), -round(stepy)))
            self.x += -round(stepx)
            self.y += -round(stepy)
        current_time = pygame.time.get_ticks()
        
        if self.type == 0:
            pass
        elif self.type == 1:
            if current_time - self.last_bullet_fired >= self.firing_cooldown:
                self.bullets.add(Bullet(self.x, self.y, self.team, 15, int(self.firing_right), False, 3000, self.bulletdamage))
                self.last_bullet_fired = current_time
        elif self.type == 2:
            if current_time - self.last_bullet_fired >= self.firing_cooldown:
                self.bullets.add(Bullet(self.x, self.y, self.team, 15, int(self.firing_right), False, 3000, self.bulletdamage))
                self.bullets.add(Bullet(self.x, self.y, self.team, 15, int(not self.firing_right), False, 3000, self.bulletdamage))
                self.last_bullet_fired = current_time
        
        for bullet in self.bullets:
            bullet.move(bullet.x_speed, bullet.y_speed, collidables)
            bullet.update()
        
        self.bullets.draw(screen)


class Game:
    def __init__(self, fps) -> None:
        self.screen_width = 900
        self.screen_height = 600

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Jin's adventures")
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
        self.enemies.add(Enemy("assets/canpooper_left.png", 50, 50, False, 1, 2, 50, 25, 1000, 5000, 850, 50, 850, 50, False, 900))

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

            self.screen.fill((255, 255, 255))
            
            # draw grid
            for i in range(0, 900, 100):
                for j in range(0, 1800, 100):
                    rect = pygame.Rect(i, j, 100, 100)
                    pygame.draw.rect(self.screen, (230, 230, 230), rect, 1)

            if self.player.has_reached_objective(self.objectives):
                message = LARGE_TEXT.render(
                    "congratulations you won", False, (0, 0, 0))
                self.screen.blit(message, (10, 200))
                pygame.display.flip()
                self.player.respawn(1000)
            
            for bullet in self.bullets:
                if (bullet.x > self.screen_width + 100 or bullet.x < -100) or bullet.y > (self.screen_height + 100 or bullet.y < -100):
                    bullet.kill()
                bullet.move(bullet.x_speed, bullet.y_speed, self.collidables)
                bullet.update()
            
            for enemy in self.enemies:
                enemy.update(self.collidables, self.fatal, self.bullets, self.screen, self.clock.get_fps())
                for bullet in enemy.bullets:
                    self.bullets.add(bullet)

            self.player.update(self.collidables, self.fatal, self.bullets, self.screen)

            self.player.draw(self.screen)
            self.collidables.draw(self.screen)
            self.fatal.draw(self.screen)
            self.objectives.draw(self.screen)
            self.bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            
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

            self.screen.blit(coordinates, (10, 10))
            self.screen.blit(onground, (10, 25))
            self.screen.blit(crouching, (10, 40))
            self.screen.blit(direction, (10, 55))
            self.screen.blit(fps, (10, 70))
            self.screen.blit(entitycount, (10, 85))
            self.screen.blit(deaths, (10, 100))

            pygame.display.flip()

            self.clock.tick(self.framecap)


if __name__ == "__main__":
    h = Game(fps=60)
    h.loop()