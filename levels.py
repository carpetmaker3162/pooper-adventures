# Note: Extend this class to create levels.
class Level:
    def __init__(self) -> None:
        pass
    
    # TODO: Maybe add some more parameters
    # Override this method.
    # Also you know you can return a level from update to change the level.
    def update():
        pass
    
    # TODO: Maybe add some more parameters
    # Override this method as well.
    def render():
        pass

class LevelManager:
    def __init__(self, starting_level) -> None:
        self.current_level = starting_level
    
    # Change the level
    def change_level_to(self, new_level):
        self.current_level = new_level
    
    # Update the current level
    def update(self):
        new_level = self.current_level.update()
        if new_level != None:
            self.current_level = new_level
    
    # Render the current level
    def render(self):
        self.current_level.render()

