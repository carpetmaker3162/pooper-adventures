import json
import os
import math
from src.player import Player
from src.enemy import Enemy
from src.props import Crate, Lava, Objective
from utils import get_image

import pygame
pygame.init()

def floor_to_nearest(coordinate: tuple, incr: int):
    x, y = coordinate
    return (incr * math.floor(x / incr),
            incr * math.floor(y / incr))

paths = {
    "player": "assets/canpooper_right.png",
    "enemy": "assets/canpooper_left_angry.png",
    "collidable": "assets/crate.png",
    "objective": "assets/burger.png",
    "fatal": "assets/lava.png"
}

def serialize(component):
    x = component.x
    y = component.y
    w = component.width
    h = component.height
    if isinstance(component, Player):
        return { "spawn": f"{x},{y}", "size": f"{w},{h}", "facing": "right", "hp": 100 }
    elif isinstance(component, Enemy):
        return {
            "spawn": f"{x},{y}", "size": f"{w},{h}",
            "facing": "left",
            "hp": 50,
            "firingDamage": 25,
            "firingRate": 1000
        }
    else:
        return { "spawn": f"{x},{y}", "size": f"{w},{h}" }

class Button(pygame.sprite.Sprite):
    def __init__(self,
            image="assets/none.png",
            x=0,
            y=0,
            width=100,
            height=100,
            text="",
            id=0):
        super().__init__()

        self.image = get_image(image, width, height)
        self.rect = self.image.get_rect()
        self.rect.center = (x + width/2, y + height/2)
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.id = id

    def is_hovering(self, mousex, mousey):
        if (self.x < mousex < self.x + self.width and
            self.y < mousey < self.y + self.height):
            return True
        else:
            return False

class Editor:
    def __init__(self, fps) -> None:
        self.screen_width = 900
        self.screen_height = 700
        self.fps = fps
        
        self.stopped = False
        self.mouse_pos = (0, 0)
        self.active_component_name = "player"
        self.mouse = True # use mouse or keyboard
        
        self.component_w = 100
        self.component_h = 100

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("level editor")
        self.g = self.screen.copy()
        self.clock = pygame.time.Clock()

        self.data = {
            "player": {},
            "enemy": [],
            "collidable": [],
            "objective": {},
            "fatal": []
        }

        # add buttons (i is for button positions)
        self.buttons = pygame.sprite.Group()
        for i, target in enumerate(self.data):
            button = Button(image=paths[target],
                            x = 25 + 100*i, y=625,
                            width=50, height=50,
                            id=target)
            self.buttons.add(button)

        toggle_mode_button = Button(image="assets/mouse.png",
                                    x = 625, y=625,
                                    width=50, height=50,
                                    id="toggle")
        self.buttons.add(toggle_mode_button)

        save_button = Button(image="assets/download.png",
                                    x = 725, y=625,
                                    width=50, height=50,
                                    id="save")
        self.buttons.add(save_button)

        self.player = Player(-1000, -1000)
        self.enemies = pygame.sprite.Group()
        self.collidables = pygame.sprite.Group()
        self.objective = Objective(-1000, -1000)
        self.fatal = pygame.sprite.Group()

    def get_component(self, x, y, w, h):
        match self.active_component_name:
            case "player":
                return Player(x, y, w, h, hp=100)
            case "enemy": # change once enemy types are added
                return Enemy("assets/canpooper_left_angry.png", x, y, w, h, bullet_damage=25)
            case "collidable":
                return Crate(x, y, w, h)
            case "objective":
                return Objective(x, y, w, h)
            case "fatal":
                return Lava(x, y, w, h)
            case _:
                raise ValueError("wtf")

    def set_component(self, component):
        match self.active_component_name:
            case "player":
                self.player = component
            case "enemy":
                self.enemies.add(component)
            case "collidable":
                self.collidables.add(component)
            case "objective":
                self.objective = component
            case "fatal":
                self.fatal.add(component)
            case _:
                raise ValueError("when the bruh")

    def change_component(self, name: str):
        self.active_component_name = name

    def save(self):
        # find an available file name
        i = 1
        while True:
            fp = f"levels/{i}.json"
            if not os.path.exists(fp):
                break
            i += 1

        print(f"Saving level at '{fp}'")
        
        self.data["player"] = serialize(self.player)

        self.data["enemy"] = []
        for enemy in self.enemies:
            self.data["enemy"].append(serialize(enemy))

        self.data["collidable"] = []
        for collidable in self.collidables:
            self.data["collidable"].append(serialize(collidable))

        self.data["objective"] = serialize(self.objective)
        
        self.data["fatal"] = []
        for fatal in self.fatal:
            self.data["fatal"].append(serialize(fatal))
        
        assert not os.path.exists(fp)

        with open(fp, "w") as f:
            f.write(json.dumps(self.data))

        print(f"Saved at '{fp}'")

    def process_events(self):
        keys = pygame.key.get_pressed()
        
        # amount changed by arrow key presses
        if keys[pygame.K_j]:
            self.component_h -= 25
        if keys[pygame.K_k]:
            self.component_h += 25
        if keys[pygame.K_h]:
            self.component_w -= 25
        if keys[pygame.K_l]:
            self.component_w += 25

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = self.mouse_pos
                if y > self.screen_height - 100:
                    for button in self.buttons:
                        if button.is_hovering(x, y):
                            if button.id == "toggle":
                                button.image = get_image(f"assets/mouse.png", 50, 50)
                                self.mouse = not self.mouse
                            elif button.id == "save":
                                self.save()
                            else:
                                self.change_component(button.id)
                else:
                    gx, gy = floor_to_nearest((x, y), 100) # change the 100 after smaller sizes are added
                    component = self.get_component(gx, gy,
                                                   self.component_w,
                                                   self.component_h) # change w and h  
                    self.set_component(component)


    def loop(self):
        while not self.stopped:
            pygame.event.pump()
            self.mouse_pos = pygame.mouse.get_pos()
            self.process_events()

            self.g.fill((255, 255, 255))
            for i in range(0, self.screen_width, 100):
                for j in range(0, self.screen_height - 100, 100):
                    rect = pygame.Rect(i, j, 100, 100)
                    pygame.draw.rect(self.g, (230, 230, 230), rect, 1)

            if self.mouse:
                px, py = self.mouse_pos
                x, y = floor_to_nearest((px, py), 100)

            self.buttons.draw(self.g)

            # draw component image that is previewed on the grid
            if 0 < px < self.screen_width and 0 < py < self.screen_height - 100:
                component = self.get_component(x, y, 
                                               self.component_w, 
                                               self.component_h) # change w/h later
                component.draw(self.g)

            self.player.draw(self.g)
            self.enemies.draw(self.g)
            self.collidables.draw(self.g)
            self.objective.draw(self.g)
            self.fatal.draw(self.g)

            self.screen.blit(pygame.transform.scale(self.g, self.screen.get_rect().size), (0, 0))
            pygame.display.flip()
            self.clock.tick(self.fps)

if __name__ == "__main__":
    editor = Editor(fps=60)
    editor.loop()
    pygame.quit()
