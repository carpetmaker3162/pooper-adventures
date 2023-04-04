import datetime
import pygame
import copy

with open("logs.txt", "a") as file:
    file.write("\n")
    file.write(f"{datetime.datetime.now()}")

cache = {}

class logs:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def log(content):
        with open("logs.txt", "a") as file:
            file.write("\n")
            file.write(content)
    
    @staticmethod
    def reset_logs():
        file = open("logs.txt", "w")
        file.close()


def decrease(number, by):
    if is_positive(number):
        return number - by
    else:
        return number + by


def increase(number, by):
    return decrease(number, -by)


def is_positive(number):
    return number >= 0


def sign(number):
    if is_positive(number):
        return 1
    else:
        return -1


def get_image(imagepath: str, width=100, height=100):
    image_key = f"{imagepath.strip()} width={width} height={height}"
    if image_key in cache:
        # logs.log(f"using cached '{imagepath}' (width={width} height={height})")
        pass
    else:
        # logs.log(f"loading '{imagepath}' (width={width} height={height})")
        image = pygame.image.load(imagepath).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        cache[image_key] = image
    return cache[image_key]
