import json
import os
import sys
import math

from entities.player import Player
from entities.enemy import Enemy
from entities.props import Crate, Lava, Objective
from utils.misc import get_image, image_paths
from utils.parser import display, serialize, sprite_types, sprite_attrs

import pygame

pygame.init()


def floor_to_nearest(coordinate: tuple, incr: tuple):
    x, y = coordinate
    incrx, incry = incr
    return (incrx * math.floor(x / incrx),
            incry * math.floor(y / incry))


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
        self.id = id

    def is_hovering(self, mousex, mousey):
        if (self.x < mousex < self.x + self.width and
                self.y < mousey < self.y + self.height):
            return True
        else:
            return False


class Editor:
    def __init__(self, fps, imported_level=None, edit=False) -> None:
        self.screen_width = 900
        self.screen_height = 800
        self.fps = fps

        self.stopped = False
        self.mouse_pos = (0, 0)
        self.active_component_name = "player"
        self.event_ticker = 10
        self.delete_mode = False
        self.orientation = "left"
        self.scene_x = 0 # top left corner x-value of page that is being scrolled

        self.component_w = 100
        self.component_h = 100

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("level editor")
        self.g = self.screen.copy()
        self.clock = pygame.time.Clock()

        self.export_data = {} # dictionary of serialized data that will be exported to files
        self.written_objects = {} # dictionary of sprite objects that will be drawn. replaces the variables that are created for each type of object

        for type_name, sprite_class in sprite_types.items():
            # whether or not an object will potentially appear in groups
            if sprite_class.singular:
                self.export_data[type_name] = {}
            else:
                self.export_data[type_name] = []

        # display imported level
        if imported_level is not None:
            if not os.path.exists(imported_level):
                raise FileNotFoundError("lmao idiot")

            with open(imported_level) as f:
                raw = f.read()
                data = json.loads(raw)
                data = display(self.g, data)

            self.written_objects.update(data)
        else:
            for type_name, sprite_class in sprite_types.items():
                if sprite_class.singular:
                    self.written_objects[type_name] = sprite_types[type_name]((-1000, -1000))
                else:
                    self.written_objects[type_name] = []

        # add buttons cooresponding to each type of sprite, in a row along the top row of the editor toolbar
        self.buttons = pygame.sprite.Group()
        for i, target in enumerate(self.written_objects.keys()):
            self.buttons.add(Button(image=image_paths[target],
                            x=25 + 100*i, y=625, width=50, height=50,
                            id=target))

        self.buttons.add(Button(image="assets/reflection.png",
                                x=625, y=625, width=50, height=50,
                                id="reflect"))

        self.buttons.add(Button(image="assets/trash.png",
                                x=725, y=625, width=50, height=50,
                                id="delete"))

        self.buttons.add(Button(image="assets/download.png",
                                x=825, y=625, width=50, height=50,
                                id="save"))

        self.buttons.add(Button(image="assets/arrow_left.png",
                                x=725, y=725, width=50, height=50,
                                id="left"))

        self.buttons.add(Button(image="assets/arrow_right.png",
                                x=825, y=725, width=50, height=50,
                                id="right"))
        
        self.imported_level = imported_level
        self.edit = edit

    def get_component(self, x, y, w, h, **kwargs):
        x = x + self.scene_x
        match self.active_component_name:
            case "player":
                return Player((x, y), (w, h), hp=100)
            case "enemy":  # change once enemy types are added
                direction = kwargs.get("orient", "left")
                return Enemy(f"assets/canpooper_{direction}_angry.png",
                             (x, y), (w, h), bullet_damage=25,
                             facing=direction)
            case _:
                sprite_type = sprite_types[self.active_component_name]
                return sprite_type((x, y), (w, h))

    def set_component(self, component):
        if type(component).singular:
            self.written_objects[component.name] = component
        else:
            self.written_objects[component.name].append(component)

    def change_component(self, name: str):
        # change this later but fine for now
        self.active_component_name = name

    def save(self):
        # find an available file name
        if not self.edit:
            i = 1
            while True:
                fp = f"levels/{i}.json"
                if not os.path.exists(fp):
                    break
                i += 1
        elif self.edit and self.imported_level is not None:
            fp = self.imported_level

        print(f"Saving level at '{fp}'")

        for key, component in self.written_objects.items():
            self.export_data[key] = serialize(component)

        if not self.edit:
            assert not os.path.exists(fp)

        with open(fp, "w") as f:
            f.write(json.dumps(self.export_data))

        print(f"Saved at '{fp}'")

    def process_key_events(self):
        keys = pygame.key.get_pressed()

        # amount changed by arrow key presses
        if self.event_ticker > 0:
            self.event_ticker -= 1
        elif self.event_ticker == 0:
            self.event_ticker = 10
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
                self.component_w = round(self.component_w / 2)
                self.component_h = round(self.component_h / 2)

        self.component_w = max(25, self.component_w)
        self.component_h = max(25, self.component_h)

    def process_mouse_events(self):
        x, y = self.mouse_pos
        # Checks whether the mouse clicked within the toolbar
        # or not.
        if y > 600:
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
                    elif button.id == "right":
                        self.scene_x += self.screen_width
                    elif button.id == "left":
                        self.scene_x -= self.screen_width
#                        self.scene_x = max(self.scene_x, 0)
                    else:
                        self.delete_mode = False
                        self.change_component(button.id)
        else:
            if self.delete_mode:
                for key, component in self.written_objects.items():
                    if type(component) != list and type(component) != pygame.sprite.Group:
                        continue
                    for obj in component:
                        if obj.lies_on(x, y):
                            self.written_objects[key].remove(obj)
            else:
                gx, gy = floor_to_nearest(
                    (x, y), (self.component_w, self.component_h))
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

    def render(self):
        mouse_px, mouse_py = self.mouse_pos
        mouse_x, mouse_y = floor_to_nearest(
            (mouse_px, mouse_py), (self.component_w, self.component_h)
        )

        # Clear the screen
        self.g.fill((255, 255, 255))

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
            )
            component.move(-self.scene_x, 0, pygame.sprite.Group()) # move to relative position on screen (we do a little trolling part 2)
            component.draw(self.g)

        self.draw_grid()

        pygame.draw.rect(
            self.g,
            (255, 255, 255),
            pygame.Rect(0, 600, 900, 100)
        )
        
        for component in self.written_objects.values():
            if isinstance(component, list) or isinstance(component, pygame.sprite.Group):
                for obj in component:
                    if self.scene_x <= obj.x <= self.scene_x + self.screen_width:
                        # we do a little trolling (move the obj to desired location on screen so its blitted to its relative position on the screen)
                        obj.move(-self.scene_x, 0, pygame.sprite.Group())
                        obj.draw(self.g)
                        obj.move(self.scene_x, 0, pygame.sprite.Group())
            else:
                if self.scene_x <= component.x <= self.scene_x + self.screen_width:
                    component.move(-self.scene_x, 0, pygame.sprite.Group())
                    component.draw(self.g)
                    component.move(self.scene_x, 0, pygame.sprite.Group())

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

            self.render()

            pygame.display.flip()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    imported_level = None
    edit = False
    
    for argument in sys.argv:
        if argument.endswith(".json") and os.path.exists(argument):
            imported_level = argument
        if argument in ["-e", "--edit"]:
            edit = True

    if imported_level is None and edit:
        raise ValueError("please pass a level file path to edit the level directly")
        pygame.quit()
        exit()
    
    editor = Editor(60, imported_level, edit=edit)
    pygame.display.set_icon(
        get_image("assets/canpooper_right_angry.png", 200, 200))
    editor.loop()
    pygame.quit()
