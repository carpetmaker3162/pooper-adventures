import os
import json

from src.player import Player
from src.entity import Entity
from src.bullet import Bullet
from src.enemy import Enemy
from src.props import Crate, Objective, Lava

import pygame

def get_level(lvl: int):
    fp = f"levels/{lvl}.json"
    if not os.path.exists(fp):
        raise FileNotFoundError
    
    with open(fp, "r") as f:
        raw = f.read()

    data = json.loads(raw)
    return data

def unwrap(d, key):
    if "," in d[key]:
        return d[key].split(,)
    else:
        if d[key].isnumeric():
            return int(d[key])
        else:
            return d[key]

def display(g: pygame.surface.Surface, data):
    p = data["player"]
    e = data["enemy"]
    c = data["collidable"]
    o = data["objective"]
    f = data["fatal"]
    
    x, y = unwrap(p, "spawn")
    w, h = unwrap(p, "size")
    hp = unwrap(p, "hp")
    player = Player(x, y, w, h, False, hp)
    
    enemies = pygame.sprite.Group()
    for enemy in e:
        x, y = unwrap(enemy, "spawn")
        w, h = unwrap(enemy, "size")
        hp = unwrap(enemy, "hp")
        dir = unwrap(enemy, "facing")
        firingdamage = unwrap(enemy, "firingDamage")
        firingrate = unwrap(enemy, "firingRate")

        enemy = Enemy(f"assets/canpooper_{dir}_angry.png",
            x, y, w, h, False, 2, hp, firingdamage, (dir == "right"), firingrate)
        enemies.add(enemy)

    collidables = pygame.sprite.Group()
    for collidable in c:
        x, y = unwrap(collidable, "spawn")
        w, h = unwrap(collidable, "size")

        collidable = Crate(x, y, w, h, False)
        collidables.add(collidable)
    
    fatalobjs = pygame.sprite.Group()
    for fatal in f:
        x, y = unwrap(fatal, "spawn")
        w, h = unwrap(fatal, "size")

        lava = Lava(x, y, w, h, False)
        fatalobjs.add(lava)
    
    x, y = unwrap(o, "spawn")
    w, h = unwrap(o, "size")
    objective = Objective(x, y, w, h, False)
    
    player.draw(g)
    enemies.draw(g)
    collidables.draw(g)
    fatalobjs.draw(g)
    objective.draw(g)
    
    new = {
        "player": player,
        "enemies": enemy,
        "collidables": collidables,
        "fatal": fatalobjs,
        "objective": objective
    }

    return new
