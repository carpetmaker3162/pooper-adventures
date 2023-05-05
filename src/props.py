from src.entity import Entity

class Crate(Entity):
    def __init__(self, spawn=(0, 0), size=(200, 200)):
        super().__init__("assets/crate.png", spawn, size, -1, 0)


class Lava(Entity):
    def __init__(self, spawn=(0, 0), size=(960, 100)):
        super().__init__("assets/lava.png", spawn, size, -1, 0)


class Objective(Entity):
    def __init__(self, spawn=(0, 0), size=(100, 100)):
        super().__init__("assets/burger.png", spawn, size, -1, 0)


class Vial(Entity):
    def __init__(self, spawn=(0, 0), size=(50, 50)):
        super().__init__("assets/none.png", spawn, size, -1, 0)
