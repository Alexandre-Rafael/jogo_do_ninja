import math
import random
import time
import pygame

from scripts.particle import Particle
from scripts.spark import Spark


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
        self._pos = value

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
            self._action = action
            self._animation = self._game.get_assets()[self._type + '/' + self._action].copy()

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


# Classe de inimigos
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        self._walking = 0

    # Getters e Setters
    def get_walking(self):
        return self._walking

    def set_walking(self, value):
        self._walking = value

    def update(self, tilemap, movement=(0, 0)):
        # Lógica de movimento do inimigo
        if self.get_walking():
            if tilemap.solid_check((self.rect().centerx + (-7 if self.get_flip() else 7), self.get_pos()[1] + 23)):
                if self.get_collisions()['right'] or self.get_collisions()['left']:
                    self.set_flip(not self.get_flip())  # Muda a direção
                else:
                    movement = (movement[0] - 0.5 if self.get_flip() else 0.5, movement[1])
            else:
                self.set_flip(not self.get_flip())  # Inverte a direção se atingir uma borda
            self.set_walking(max(0, self.get_walking() - 1))

            # Decidir quando atirar
            if not self.get_walking():
                dis = (self.get_game().get_player().get_pos()[0] - self.get_pos()[0],
                       self.get_game().get_player().get_pos()[1] - self.get_pos()[1])
                if abs(dis[1]) < 16:
                    self.shoot()  # Atira no jogador
        elif random.random() < 0.01:
            self.set_walking(random.randint(30, 120))

        # Atualizar física
        PhysicsEntity.update(self, tilemap, movement=movement)

        # Definir a ação (andar ou ficar parado)
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Verificar se foi atingido por um dash
        player = self.get_game().get_player()
        if abs(player.get_dashing()) >= 50:  # Verifica se o jogador está realizando um dash
            if self.rect().colliderect(player.rect()):  # Verifica a colisão com o jogador
                self.morrer()  # Inimigo morre ao ser atingido pelo dash

    def morrer(self):
        """Função que trata a morte do inimigo"""
        self.get_game().set_screenshake(max(16, self.get_game().get_screenshake()))
        self.get_game().get_sfx()['hit'].play()
        for i in range(30):
            angle = random.random() * math.pi * 2
            speed = random.random() * 5
            self.get_game().get_sparks().append(Spark(self.rect().center, angle, 2 + random.random()))
            self.get_game().get_particles().append(Particle(self.get_game(), 'particle', self.rect().center,
                                                            velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                      math.sin(angle + math.pi) * speed * 0.5],
                                                            frame=random.randint(0, 7)))
        self.get_game().get_enemies().remove(self)  # Remove o inimigo da lista de inimigos do jogo

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        # Desenhar a arma
        if self.get_flip():
            surf.blit(pygame.transform.flip(self.get_game().get_assets()['gun'], True, False),
                      (self.rect().centerx - 4 - self.get_game().get_assets()['gun'].get_width() - offset[0],
                       self.rect().centery - offset[1]))
        else:
            surf.blit(self.get_game().get_assets()['gun'],
                      (self.rect().centerx + 4 - offset[0],
                       self.rect().centery - offset[1]))

    def shoot(self):
        """Atira no jogador"""
        self.get_game().get_sfx()['shoot'].play()
        if self.get_flip():
            projectile_pos = [self.rect().centerx - 7, self.rect().centery]
            direction = -1.5
        else:
            projectile_pos = [self.rect().centerx + 7, self.rect().centery]
            direction = 1.5
        self.get_game().get_projectiles().append([projectile_pos, direction, 0])

        # Efeito de faíscas no tiro
        for i in range(4):
            angle = random.random() - 0.5
            speed = 2 + random.random()
            self.get_game().get_sparks().append(Spark(projectile_pos, angle, speed))


class FastShootingEnemy(Enemy):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size)
        self.shooting_interval = 3  # Intervalo de 0.1 segundo entre cada tiro
        self.last_shot_time = time.time()  # Armazena o tempo do último tiro

    def update(self, tilemap, movement=(0, 0)):
        # Lógica do movimento e outras funcionalidades
        super().update(tilemap, movement=movement)

        # Lógica de tiro contínuo (metralhadora)
        if time.time() - self.last_shot_time > self.shooting_interval:
            self.shoot()
            self.last_shot_time = time.time()

    def shoot(self):
        # Método para atirar
        super().shoot()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.collected = False
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (16, 16))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, player):
        if self.rect.colliderect(player.rect()):
            player.activate_double_jump()
            self.kill()  # Remove o powerup do jogo
            self.collected = True

    # Método render para desenhar o powerup na tela
    def render(self, surf, offset=(0, 0)):
        if not self.collected:
            surf.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self._air_time = 0
        self._jumps = 1
        self._wall_slide = False
        self._dashing = 0
        self.double_jump_active = False  # Variável para controlar o double jump
        self.double_jump_timer = 0  # Timer para controlar duração do powerup

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
