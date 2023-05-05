from utils import get_image
from src.entity import Entity
import pygame

class Player(Entity):
    def __init__(self,
            spawn=(0, 0),
            size=(100, 100),
            hp=100):
        
        width, height = size
        x, y = spawn
        super().__init__("assets/canpooper_right.png", spawn, size, hp, None, 1)

        # initing stuff
        self.left_image = get_image(
            "assets/canpooper_left.png", width, height)
        self.right_image = get_image(
            "assets/canpooper_right.png", width, height)
        self.respawn_x = x
        self.respawn_y = y
        self.x_acceleration = 0.5
        self.last_bullet_fired = -float("inf")
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
        self.direction = "right"
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

    def has_reached_objective(self, objective):
        return pygame.sprite.collide_rect(self, objective)

    def update(self, collidables, fatal, bullets, screen):
        super().update(collidables, fatal, bullets, screen)

        keys = pygame.key.get_pressed()
        no_keys_pressed = not (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT])

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
        if no_keys_pressed and self.direction == "right":
            self.x_speed -= self.x_acceleration
            if self.x_speed < 0:
                self.x_speed = 0
        elif no_keys_pressed and self.direction == "left":
            self.x_speed += self.x_acceleration
            if self.x_speed > 0:
                self.x_speed = 0

        # moving left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = "left"
            self.x_speed -= self.x_acceleration
            if self.x_speed < -self.max_x_speed:
                self.x_speed = -self.max_x_speed  # Reduce speed to max speed

        # moving right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = "right"
            self.x_speed += self.x_acceleration
            if self.x_speed > self.max_x_speed:
                self.x_speed = self.max_x_speed  # Reduce speed to max speed

        # jumping
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.crouching and self.on_ground:
            self.y_speed = -self.jump_power * 10

        self.crouching = False

        # crouching
        if (keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.on_ground:
            # crouching
            self.x_speed *= 0.7
            self.crouching = True

        # change player image
        if self.direction == "right":
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

