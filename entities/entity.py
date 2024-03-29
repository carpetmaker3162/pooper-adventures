from utils.misc import get_image, sign
import pygame

class Entity(pygame.sprite.Sprite):
    """
    Team ID
    0 = objects
    1 = player
    2 = enemy
    """
    singular = False
    name = "entity"

    def __init__(self,
            image="assets/none.png",
            spawn=(0, 0),
            size=(100, 100),
            hp=-1,
            team=0):

        super().__init__()
        self.width, self.height = size
        self.x, self.y = spawn

        self.image = get_image(image, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.team = team

        self.hp_bar_size = self.width

        self.x_speed = 0
        self.y_speed = 0
        self.invulnerable = False
        self.damage_delay = 500
        self.last_hit_by_bullet = -float("inf")

        self.hp = hp
        self.max_hp = self.hp

        if hp < 0:  # invulnerable if negative
            self.invulnerable = True

    def draw(self, screen, x_offset=0):
        # if self.hitbox:
        # pygame.draw.rect(screen, pygame.Color(
        #     255, 0, 0), self.rect, width=5)
        screen.blit(
            self.image, (self.rect.center[0] - self.width/2 - x_offset, self.rect.center[1] - self.height/2))
        if self.hp != self.max_hp and not self.invulnerable:
            self.draw_hp_bar(screen, x_offset)

    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(0, dy, collidables):
            dy -= sign(dy)
        while self.colliding_at(dx, 0, collidables):
            dx -= sign(dx)
        while self.colliding_at(dx, dy, collidables):
            dx -= sign(dx)
            dy -= sign(dy)

        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))

    def colliding_at(self, x, y, entities):
        self.rect.move_ip((x, y))
        colliding = pygame.sprite.spritecollideany(self, entities)
        self.rect.move_ip((-x, -y))
        return colliding

    def update(self, objects: dict, bullets, screen):
        if not self.invulnerable:
            for bullet in pygame.sprite.spritecollide(self, bullets, False):
                if bullet.team != self.team:
                    self.hp -= bullet.damage
                    bullet.kill()

        if self.hp < 0 and not self.invulnerable:
            self.kill()
            if hasattr(self, "bullets"):
                for bullet in self.bullets:
                    bullet.kill()

    def draw_hp_bar(self, screen: pygame.Surface, x_offset=0):
        pos = (self.x - x_offset - ((self.hp_bar_size - self.width)), self.y - 15)
        size = (self.hp_bar_size, 10)
        pygame.draw.rect(screen, (0, 0, 0), (pos, size), 1)
        bar_pos = (pos[0] + 3, pos[1] + 3)
        bar_size = ((size[0] - 6) * (self.hp / self.max_hp), size[1] - 6)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_pos, *bar_size))

    # return whether or not a point lies on the entity
    def lies_on(self, x, y):
        if (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height):
            return True
        else:
            return False
