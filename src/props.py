from src.entity import Entity

class Crate(Entity):
    def __init__(self, x, y, width=200, height=200, hitbox=False):
        super().__init__("assets/crate.png", x, y, width, height, hitbox, -1, 0)


class Lava(Entity):
    def __init__(self, x, y, width=960, height=100, hitbox=False):
        super().__init__("assets/lava.png", x, y, width, height, hitbox, -1, 0)


class Objective(Entity):
    def __init__(self, x, y, width=100, height=100, hitbox=False):
        super().__init__("assets/burger.png", x, y, width, height, hitbox, -1, 0)
