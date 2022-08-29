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

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty, width = 100, height = 100):
        super().__init__()

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        
        self.rect.center = [startx, starty]

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)
    
    def move(self, x, y):
        self.rect.move_ip((x, y))

class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((960, 640))
        pygame.display.set_caption("can pooper's adventures in Poopland")
        self.clock = pygame.time.Clock()
        self.screen.fill((255, 255, 255))
        self.stopped = False
        self.framecap = 60
    
    def process_events(self):
        # process keyboard events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # change later
                exit()
    
    def loop(self):
        pygame.display.flip()
        while not self.stopped:
            self.process_events()
            self.clock.tick(self.framecap)

class Player(Entity):
    def __init__(self, startx, starty, width = 100, height = 200):
        super().__init__("assets/Sports-Ball-Transparent.png", startx, starty, width, height)
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_w]:
            self.move()

if __name__ == "__main__":
    h = Game()
    p = Player(100, 100, 100, 100)
    p.draw(h.screen)
    h.loop()