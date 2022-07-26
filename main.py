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
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image).convert()
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

class Player(Entity):
    def __init__(self, startx, starty):
        super().__init__("assets/canpooper.png", startx, starty)

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
        while not self.stopped:
            self.process_events()
            self.clock.tick(self.framecap)

if __name__ == "__main__":
    h = Game()
    p = Player(400, 400)
    p.draw(h.screen)
    h.loop()