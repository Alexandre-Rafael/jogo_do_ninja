import math
import random

import pygame
from scripts.entities.physics_entity import PhysicsEntity
from scripts.map.particle import Particle
from scripts.map.spark import Spark


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

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        player = self.get_game().get_player()
        if abs(player.get_dashing()) >= 50:  
            if self.rect().colliderect(player.rect()):  
                self.morrer()  

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
        self.get_game().get_enemies().remove(self)  

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

