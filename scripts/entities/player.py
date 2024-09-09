import math
import random
import time

from scripts.entities.physics_entity import PhysicsEntity
from scripts.map.particle import Particle


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self._air_time = 0
        self._jumps = 1
        self._wall_slide = False
        self._dashing = 0
        self.double_jump_active = False
        self.double_jump_timer = 0

    # Getters e Setters
    def get_air_time(self):
        return self._air_time

    def set_air_time(self, value):
        self._air_time = value

    def get_jumps(self):
        return self._jumps

    def set_jumps(self, value):
        self._jumps = value

    def get_wall_slide(self):
        return self._wall_slide

    def set_wall_slide(self, value):
        self._wall_slide = value

    def get_dashing(self):
        return self._dashing

    def set_dashing(self, value):
        self._dashing = value

    def activate_double_jump(self):
        # Ativa o double jump e o temporizador
        self.double_jump_active = True
        self.double_jump_timer = time.time()  # Armazena o tempo atual

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        # Atualizar o timer do double jump e desativar se passar 20 segundos
        if self.double_jump_active and time.time() - self.double_jump_timer > 20:
            self.double_jump_active = False

        self._air_time += 1

        # Verificar se o player está no chão para resetar o contador de pulos
        if self.get_collisions()['down']:
            self._air_time = 0
            self._jumps = 2 if self.double_jump_active else 1  # Permitir double jump se ativo

        if self.get_pos()[1] > tilemap.get_map_height():
            self.get_game().load_level(self.get_game().get_level())  # Reiniciar o nível
            return  # Evitar continuar a lógica de atualização

        self._wall_slide = False
        if (self.get_collisions()['right'] or self.get_collisions()['left']) and self._air_time > 4:
            self._wall_slide = True
            self._velocity[1] = min(self._velocity[1], 0.5)
            self._flip = self.get_collisions()['right'] == False
            self.set_action('wall_slide')

        if not self._wall_slide:
            if self._air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if abs(self._dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.get_game().get_particles().append(
                    Particle(self.get_game(), 'particle', self.rect().center, velocity=pvelocity,
                             frame=random.randint(0, 7)))
        if self._dashing > 0:
            self._dashing = max(0, self._dashing - 1)
        if self._dashing < 0:
            self._dashing = min(0, self._dashing + 1)
        if abs(self._dashing) > 50:
            self._velocity[0] = abs(self._dashing) / self._dashing * 8
            if abs(self._dashing) == 51:
                self._velocity[0] *= 0.1
            pvelocity = [abs(self._dashing) / self._dashing * random.random() * 3, 0]
            self.get_game().get_particles().append(
                Particle(self.get_game(), 'particle', self.rect().center, velocity=pvelocity,
                         frame=random.randint(0, 7)))

        if self._velocity[0] > 0:
            self._velocity[0] = max(self._velocity[0] - 0.1, 0)
        else:
            self._velocity[0] = min(self._velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        if abs(self._dashing) <= 50:
            super().render(surf, offset=offset)

    def dash(self):
        if not self.get_dashing():
            self.get_game().get_sfx()['dash'].play()
            if self.get_flip():
                self.set_dashing(-60)
            else:
                self.set_dashing(60)
            # Adicionando partículas ao fazer o dash
            for i in range(10):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.get_game().get_particles().append(
                    Particle(self.get_game(), 'particle', self.rect().center, velocity))

    def jump(self):
        if self._wall_slide:
            if self._flip and self.get_last_movement()[0] < 0:
                self._velocity[0] = 3.5
                self._velocity[1] = -2.5
                self._air_time = 5
                self._jumps = max(0, self._jumps - 1)
                return True
            elif not self._flip and self.get_last_movement()[0] > 0:
                self._velocity[0] = -3.5
                self._velocity[1] = -2.5
                self._air_time = 5
                self._jumps = max(0, self._jumps - 1)
                return True
        elif self._jumps:
            self._velocity[1] = -3
            self._jumps -= 1
            self._air_time = 5
            return True
