import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self._game = game
        self._type = e_type
        self._pos = list(pos)
        self._size = size
        self._velocity = [0, 0]
        self._collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self._action = ''
        self._anim_offset = (-3, -3)
        self._flip = False
        self.set_action('idle')

        self._last_movement = [0, 0]

    # Getters e Setters
    def get_game(self):
        return self._game

    def set_game(self, value):
        self._game = value

    def get_type(self):
        return self._type

    def set_type(self, value):
        self._type = value

    def get_pos(self):
        return self._pos

    def set_pos(self, value):
        self._pos = list(value)

    def get_size(self):
        return self._size

    def set_size(self, value):
        self._size = value

    def get_velocity(self):
        return self._velocity

    def set_velocity(self, value):
        self._velocity = value

    def get_collisions(self):
        return self._collisions

    def set_collisions(self, value):
        self._collisions = value

    def get_action(self):
        return self._action

    def set_action(self, action):
        if action != self._action:
            if self._type + '/' + action in self._game.get_assets():
                self._action = action
                self._animation = self._game.get_assets()[self._type + '/' + self._action].copy()
            else:
                print(f"Animação {self._type}/{action} não encontrada, mantendo a ação {self._action}")

    def get_anim_offset(self):
        return self._anim_offset

    def set_anim_offset(self, value):
        self._anim_offset = value

    def get_flip(self):
        return self._flip

    def set_flip(self, value):
        self._flip = value

    def get_last_movement(self):
        return self._last_movement

    def set_last_movement(self, value):
        self._last_movement = value

    def rect(self):
        return pygame.Rect(self._pos[0], self._pos[1], self._size[0], self._size[1])

    def update(self, tilemap, movement=(0, 0)):
        self._collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self._velocity[0], movement[1] + self._velocity[1])

        self._pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self._pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self._collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self._collisions['left'] = True
                self._pos[0] = entity_rect.x

        self._pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self._pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self._collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self._collisions['up'] = True
                self._pos[1] = entity_rect.y

        if movement[0] > 0:
            self._flip = False
        if movement[0] < 0:
            self._flip = True

        self._last_movement = movement

        self._velocity[1] = min(5, self._velocity[1] + 0.1)

        if self._collisions['down'] or self._collisions['up']:
            self._velocity[1] = 0

        self._animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self._animation.img(), self._flip, False),
                  (self._pos[0] - offset[0] + self._anim_offset[0], self._pos[1] - offset[1] + self._anim_offset[1]))
