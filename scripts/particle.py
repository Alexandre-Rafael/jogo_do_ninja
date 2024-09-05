class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self._game = game
        self._type = p_type
        self._pos = list(pos)
        self._velocity = velocity
        self._animation = self._game.get_assets()['particle/' + p_type].copy()
        self._animation.frame = frame

    # Getters e Setters
    def get_type(self):
        return self._type

    def set_type(self, value):
        self._type = value

    def get_pos(self):
        return self._pos

    def set_pos(self, value):
        self._pos = value

    def get_velocity(self):
        return self._velocity

    def set_velocity(self, value):
        self._velocity = value

    def get_animation(self):
        return self._animation

    def set_animation(self, value):
        self._animation = value

    def update(self):
        self._pos[0] += self._velocity[0]
        self._pos[1] += self._velocity[1]
        return self._animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(self._animation.img(), (self._pos[0] - offset[0], self._pos[1] - offset[1]))
