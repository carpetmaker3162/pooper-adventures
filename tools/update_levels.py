import os
import json
from warnings import warn

folder = "levels/"

def get_levels():
    levels = {}

    for file in os.listdir(folder):
        fp = folder + file

        with open(fp) as f:
            content = f.read()

        levels[fp] = json.loads(content)

    return levels

def save_levels(levels: dict):
    for fp, level in levels.items():
        with open(fp, "w") as f:
            f.write(json.dumps(level))

def add_sprite(name: str, default_values: dict):
    levels = get_levels()

    for fp in levels:
        if name in levels[fp]:
            raise ValueError(f"sprite '{name}' already exists in {fp}")

    for fp in levels:
        levels[fp][name] = default_values

    save_levels(levels)

def add_sprite_group(name: str):
    levels = get_levels()

    for fp in levels:
        if name in levels[fp]:
            raise ValueError(f"group '{name}' already exists in {fp}")

    for fp in levels:
        levels[fp][name] = []

    save_levels(levels)

def remove_sprite(name: str):
    levels = get_levels()

    for fp in levels:
        if name not in levels[fp]:
            warn(f"sprite '{name}' does not exist in {fp}")
        else:
            del levels[fp][name]

    save_levels(levels)
