from executables.rooms.obstacles.Obstacle import Obstacle


class Fridge(Obstacle):
    def __init__(self, r, pos=(0, 0), *sprite_groups):
        self.image = r.drawable("fridge")
        super().__init__(r, pos, *sprite_groups)
