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
    
    objectives = pygame.sprite.Group()
    x, y = unwrap(o, "spawn")
    w, h = unwrap(o, "size")
    objective = Objective(x, y, w, h, False)
    objectives.add(objective)
    
    player.draw(g)
    enemies.draw(g)
    collidables.draw(g)
    fatalobjs.draw(g)
    objectives.draw(g)
    
    new = {
        "player": player,
        "enemies": enemies,
        "collidables": collidables,
        "fatal": fatalobjs,
        "objectives": objectives
    }

    return new
