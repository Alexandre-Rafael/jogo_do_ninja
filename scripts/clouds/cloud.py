
class Cloud:
    def __init__(self, pos, img, speed, depth):
        self._pos = list(pos)
        self._img = img
        self._speed = speed
        self._depth = depth

    def get_pos(self):
        return self._pos

    def set_pos(self, value):
        self._pos = value

    def get_img(self):
        return self._img

    def set_img(self, value):
        self._img = value

    def get_speed(self):
        return self._speed

    def set_speed(self, value):
        self._speed = value

    def get_depth(self):
        return self._depth

    def set_depth(self, value):
        self._depth = value

    def update(self):
        self._pos[0] += self._speed

    def render(self, surf, offset=(0, 0)):
        render_pos = (self._pos[0] - offset[0] * self._depth, self._pos[1] - offset[1] * self._depth)
        surf.blit(self._img, (render_pos[0] % (surf.get_width() + self._img.get_width()) - self._img.get_width(),
                              render_pos[1] % (surf.get_height() + self._img.get_height()) - self._img.get_height()))
