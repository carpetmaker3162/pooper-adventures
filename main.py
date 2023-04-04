import os
import sys
from utils import logs, decrease, increase, is_positive, get_image, sign
import pygame

pygame.init()
pygame.font.init()

NULLIMAGE = pygame.image.load("assets/none.png")
ARIAL = pygame.font.SysFont("ARIAL", 12)
LARGE_TEXT = pygame.font.SysFont("ARIAL", 40)

class Entity(pygame.sprite.Sprite):
    """
    Team ID
    0 = objects
    1 = player
    2 = enemy
    """
    def __init__(
            self, 
            image=NULLIMAGE,
            x=0,
            y=0,
            width=100,
            height=100,
            show_hitbox=False,
            hp=sys.maxsize,
            hp_bar_size=None,
            team=0):

        super().__init__()

        self.image = get_image(image, width, height)
        self.rect = self.image.get_rect()
        self.rect.center = (x + width/2, y + height/2)
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
        screen.blit(self.image, (self.rect.center[0] - self.width/2, self.rect.center[1] - self.height/2))
    
    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(0, dy, collidables):
            dy -= sign(dy)
        while self.colliding_at(dx, dy, collidables):
            dx -= sign(dx)

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
            for bullet in pygame.sprite.spritecollide(self, bullets, False):
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
    def __init__(
            self,
            x,
            y,
            width=100,
            height=200,
            hitbox=False,
            hp=100):

        super().__init__("assets/canpooper_left.png", x, y, width, height, hitbox, hp, None, 1)

        # initing stuff
        self.left_image = get_image(
            "assets/canpooper_left.png", width, height)
        self.right_image = get_image(
            "assets/canpooper_right.png", width, height)
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
        p = self.rect
        for entity in entities:
            e = entity.rect
            if (e.top == p.bottom and 
                    (e.left <= p.left <= e.right or 
                    e.left <= p.right <= e.right or 
                    p.left <= e.left and 
                    p.right >= e.right)):
                return True
        return False

    def hitting_ceiling(self, entities):
        p = self.rect
        for entity in entities:
            e = entity.rect
            if (e.bottom == p.top and 
                    (e.left <= p.left <= e.right or 
                    e.left <= p.right <= e.right or 
                    p.left <= e.left and 
                    p.right >= e.right)):
                return True
        return False

    def has_reached_objective(self, objectives):
        return pygame.sprite.spritecollideany(self, objectives) is not None

    def update(self, collidables, fatal, bullets, screen):
        super().update(collidables, fatal, bullets, screen)
        
        if (pygame.sprite.spritecollideany(self, fatal) or self.y > 2000 or self.hp <= 0) and not self.invulnerable:
            self.die()

        keys = pygame.key.get_pressed()
        no_keys_pressed = not (keys[pygame.K_a] or keys[pygame.K_d])

        self.on_ground = self.is_on_ground(collidables)
        hitting_ceiling = self.hitting_ceiling(collidables)

        # change or apply acceleration depending on whether player is on the ground
        if not self.on_ground:
            self.x_acceleration = self.air_x_acceleration
            if self.y_speed < self.terminal_velocity:
                self.y_speed += self.gravity
        else:
            # when player is on the ground
            self.y_speed = 0
            self.x_acceleration = self.ground_x_acceleration

        # bounce back if player hits the ceilint
        if hitting_ceiling:
            self.y_speed = -self.y_speed * 0.6  # bounce

        
        # de-acceleration
        if no_keys_pressed and self.facing_right:
            self.x_speed -= self.x_acceleration
            if self.x_speed < 0:
                self.x_speed = 0
        elif no_keys_pressed and not self.facing_right:
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
        super().__init__("assets/burger.png", x, y, width, height, hitbox, sys.maxsize, 0)


class Bullet(Entity):
    def __init__(
            self, 
            x,
            y,
            team=0,
            speed=100,
            direction=0,
            hitbox=False,
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
        self.last_bullet_fired = -sys.maxsize
        
    
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


class Game:
    def __init__(self, fps) -> None:
        self.screen_width = 900
        self.screen_height = 600

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("can pooper's adventures")
        self.g = self.screen.copy() # for rescaling

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
