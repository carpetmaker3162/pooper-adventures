import json
import os
import sys
import math
from src.player import Player
from src.enemy import Enemy
from src.props import Crate, Lava, Objective
from utils import get_image
from parser import display

import pygame
pygame.init()


def floor_to_nearest(coordinate: tuple, incr: tuple):
    x, y = coordinate
    incrx, incry = incr
    return (incrx * math.floor(x / incrx),
            incry * math.floor(y / incry))


image_paths = {
    "player": "assets/canpooper_right.png",
    "enemy": "assets/canpooper_right_angry.png",
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
        return {"spawn": f"{x},{y}", "size": f"{w},{h}", "facing": "right", "hp": 100}
    elif isinstance(component, Enemy):
        return {
            "spawn": f"{x},{y}", "size": f"{w},{h}",
            "facing": component.facing,
            "hp": 50,
            "firingDamage": 25,
            "firingRate": 1000
        }
    else:
        return {"spawn": f"{x},{y}", "size": f"{w},{h}"}


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
    def __init__(self, fps, imported_level=None) -> None:
        self.screen_width = 900
        self.screen_height = 700
        self.fps = fps

        self.stopped = False
        self.mouse_pos = (0, 0)
        self.active_component_name = "player"
        self.event_ticker = 10
        self.delete_mode = False
        self.orientation = "left"

        self.component_w = 100
        self.component_h = 100

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE)
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

        # display imported level
        if imported_level is not None:
            if not os.path.exists(imported_level):
                raise FileNotFoundError("lmao idiot")
            with open(imported_level) as f:
                raw = f.read()
                data = json.loads(raw)
                data = display(self.g, data)
            self.player = data["player"]
            self.enemies = data["enemies"]
            self.collidables = data["collidables"]
            self.fatal = data["fatal"]
            self.objective = data["objectives"].sprites()[0]
        else:
            self.player = Player(-1000, -1000)
            self.enemies = pygame.sprite.Group()
            self.collidables = pygame.sprite.Group()
            self.objective = Objective(-1000, -1000)
            self.fatal = pygame.sprite.Group()

        # add buttons (i is for button positions)
        self.buttons = pygame.sprite.Group()
        for i, target in enumerate(self.data):
            button = Button(image=image_paths[target],
                            x=25 + 100*i, y=625,
                            width=50, height=50,
                            id=target)
            self.buttons.add(button)

        reflect_button = Button(image="assets/reflection.png",
                                x=625, y=625,
                                width=50, height=50,
                                id="reflect")
        self.buttons.add(reflect_button)

        delete_button = Button(image="assets/trash.png",
                               x=725, y=625,
                               width=50, height=50,
                               id="delete")
        self.buttons.add(delete_button)

        save_button = Button(image="assets/download.png",
                             x=825, y=625,
                             width=50, height=50,
                             id="save")
        self.buttons.add(save_button)

    def get_component(self, x, y, w, h, **kwargs):
        match self.active_component_name:
            case "player":
                return Player(x, y, w, h, hp=100)
            case "enemy":  # change once enemy types are added
                direction = kwargs.get("orient", "left")
                return Enemy(f"assets/canpooper_{direction}_angry.png",
                             x, y, w, h, bullet_damage=25,
                             facing=direction)
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

    def process_key_events(self):
        keys = pygame.key.get_pressed()

        # amount changed by arrow key presses
        if self.event_ticker > 0:
            self.event_ticker -= 1
        elif self.event_ticker == 0:
            self.event_ticker = 5
            if keys[pygame.K_j]:
                self.component_h -= 25
            elif keys[pygame.K_k]:
                self.component_h += 25
            elif keys[pygame.K_h]:
                self.component_w -= 25
            elif keys[pygame.K_l]:
                self.component_w += 25
            elif keys[pygame.K_UP]:
                self.component_w *= 2
                self.component_h *= 2
            elif keys[pygame.K_DOWN]:
                self.component_w /= 2
                self.component_h /= 2
                self.component_w = int(self.component_w)
                self.component_h = int(self.component_h)

        self.component_w = max(25, self.component_w)
        self.component_h = max(25, self.component_h)

    def process_mouse_events(self):
        x, y = self.mouse_pos
        # Checks whether the mouse clicked within the toolbar
        # or not.
        if y > self.screen_height - 100:
            for button in self.buttons:
                if button.is_hovering(x, y):
                    if button.id == "delete":
                        self.delete_mode = True
                    elif button.id == "save":
                        self.save()
                    elif button.id == "reflect":
                        self.orientation = ("left" if
                                            self.orientation == "right" else
                                            "right")
                    else:
                        self.delete_mode = False
                        self.change_component(button.id)
        else:
            gx, gy = floor_to_nearest(
                (x, y), (self.component_w, self.component_h))
            if self.delete_mode:
                for e in self.enemies:
                    if e.lies_on(x, y):
                        e.kill()
                for c in self.collidables:
                    if c.lies_on(x, y):
                        c.kill()
                for f in self.fatal:
                    if f.lies_on(x, y):
                        f.kill()
            else:
                component = self.get_component(gx, gy,
                                               self.component_w,
                                               self.component_h,
                                               orient=self.orientation)
                self.set_component(component)

    def process_events(self):
        pygame.event.pump()
        self.mouse_pos = pygame.mouse.get_pos()

        self.process_key_events()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_events()

    def draw_grid(self):
        for i in range(0, self.screen_width, 100):
            for j in range(0, self.screen_height - 100, 100):
                rect = pygame.Rect(i, j, 100, 100)
                pygame.draw.rect(self.g, (230, 230, 230), rect, 1)

    def render(self, mouse_x, mouse_y, mouse_px, mouse_py):
        # draw component image that is previewed on the grid
        if (
            0 < mouse_px < self.screen_width and
            0 < mouse_py < self.screen_height - 100 and
            not self.delete_mode
        ):
            component = self.get_component(
                mouse_x, mouse_y,
                self.component_w,
                self.component_h,
                orient=self.orientation
            )  # change w/h later

            component.draw(self.g)

        self.draw_grid()

        pygame.draw.rect(
            self.g,
            (255, 255, 255),
            pygame.Rect(0, 600, 900, 100)
        )

        self.player.draw(self.g)
        self.enemies.draw(self.g)
        self.collidables.draw(self.g)
        self.objective.draw(self.g)
        self.fatal.draw(self.g)
        self.buttons.draw(self.g)

        self.screen.blit(
            pygame.transform.scale(
                self.g, self.screen.get_rect().size
            ),
            (0, 0)
        )

    def loop(self):
        while not self.stopped:
            self.process_events()

            self.g.fill((255, 255, 255))

            px, py = self.mouse_pos
            mouse_x, mouse_y = floor_to_nearest(
                (px, py), (self.component_w, self.component_h)
            )

            self.render(mouse_x, mouse_y, px, py)

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    imported_level = None
    if len(sys.argv) > 1:
        imported_level = sys.argv[1]

    editor = Editor(60, imported_level)
    pygame.display.set_icon(
        get_image("assets/canpooper_right_angry.png", 200, 200))
    editor.loop()
    pygame.quit()
