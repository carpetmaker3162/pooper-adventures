import os
import json

from entities.player import Player
from entities.entity import Entity
from entities.enemy import Enemy
from entities.props import Crate, Objective, Lava

import pygame

sprite_attrs = {
    "firingDamage": "bullet_damage",
    "firingRate": "firing_cooldown"
}

sprites = {
    "player": Player,
    "enemy": Enemy,
    "collidable": Crate,
    "objective": Objective,
    "fatal": Lava,
}

def serialize(component):
    x = component.x
    y = component.y
    w = component.width
    h = component.height

    if isinstance(component, Player):
        return {
            "spawn": f"{x},{y}",
            "size": f"{w},{h}",
            "facing": "right",
            "hp": 100
        }
    elif isinstance(component, Enemy):
        return {
            "spawn": f"{x},{y}", "size": f"{w},{h}",
            "facing": component.facing,
            "hp": 50,
            "firingDamage": 25,
            "firingRate": 1000
        }
    else:
        return {
            "spawn": f"{x},{y}",
            "size": f"{w},{h}"
        }


def get_level(lvl: int):
    fp = f"levels/{lvl}.json"
    if not os.path.exists(fp):
        raise FileNotFoundError(f"Level {lvl} does not exist")

    with open(fp, "r") as f:
        raw = f.read()

    data = json.loads(raw)
    return data


def unwrap(d, key):
    if isinstance(d[key], int):
        return d[key]
    if "," in d[key]:
        return list(map(int, d[key].split(",")))
    else:
        return d[key]

def display(g: pygame.surface.Surface, data):
    new = {}
    for key, section in data.items():
        if isinstance(section, list): # draw a group of items
            group = pygame.sprite.Group()

            # iterate through the group of items
            for item in section:
                arguments = {}

                # add all of the object's attributes that have been specified
                for attr in item.keys():
                    arguments[sprite_attrs.get(attr, attr)] = unwrap(item, attr)

                # handle objects that need to be initialized with additional arguments
                if key == "enemy":
                    obj = sprites[key](
                        f"assets/canpooper_{arguments.get('facing', 'right')}_angry.png",
                        **arguments)
                else:
                    obj = sprites[key](**arguments)

                group.add(obj)

            group.draw(g)
            new[key] = group
        if isinstance(section, dict):
            arguments = {}

            for attr in section.keys():
                arguments[sprite_attrs.get(attr, attr)] = unwrap(section, attr)

            obj = sprites[key](**arguments)

            obj.draw(g)
            new[key] = obj
    
    # add in empty groups where needed
    for sprite_type in sprites:
        if sprite_type not in new:
            new[sprite_type] = []

    return new
