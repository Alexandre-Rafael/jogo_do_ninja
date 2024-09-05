import os
import sys
import math
import random
import time

import pygame
from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy, FastShootingEnemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        # Redimensiona a imagem para 16x16 pixels
        self.image = pygame.transform.scale(pygame.image.load(image), (16, 16))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, player):
        # Verifica se o jogador colide com o powerup
        if self.rect.colliderect(player.rect()):
            player.activate_double_jump()  # Ativa o double jump no jogador
            self.kill()  # Remove o powerup após a coleta

    def render(self, surf, offset=(0, 0)):
        # Renderiza o powerup na tela com base no deslocamento
        surf.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('ninja game')
        pygame.mixer.init()  # Inicializa o mixer para carregar sons
        self._screen = pygame.display.set_mode((640, 480))
        self._display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self._display_2 = pygame.Surface((320, 240))
        self._dead = 0

        self._clock = pygame.time.Clock()
        self._movement = [False, False]
        
        self._assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'powerup': load_image('powerup.png')
        }
        
        self._sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        
        self._sfx['ambience'].set_volume(0.2)
        self._sfx['shoot'].set_volume(0.4)
        self._sfx['hit'].set_volume(0.8)
        self._sfx['dash'].set_volume(0.3)
        self._sfx['jump'].set_volume(0.7)
        
        self._clouds = Clouds(self._assets['clouds'], count=16)
        
        self._player = Player(self, (50, 50), (8, 15))
        
        self._tilemap = Tilemap(self, tile_size=16)
        
        self._level = 0
        self.load_level(self._level)
        
        self._screenshake = 0

    def get_screen(self):
        return self._screen

    def get_enemies(self):
        return self._enemies

    def get_display(self):
        return self._display

    def get_display_2(self):
        return self._display_2

    def get_clock(self):
        return self._clock

    def get_movement(self):
        return self._movement

    def set_movement(self, value):
        self._movement = value

    def get_assets(self):
        return self._assets

    def get_sfx(self):
        return self._sfx

    def get_clouds(self):
        return self._clouds

    def get_player(self):
        return self._player

    def get_tilemap(self):
        return self._tilemap

    def get_level(self):
        return self._level

    def set_level(self, value):
        self._level = value

    def get_screenshake(self):
        return self._screenshake

    def set_screenshake(self, value):
        self._screenshake = value

    def get_projectiles(self):
        return self._projectiles

    def get_sparks(self):
        return self._sparks

    def get_particles(self):
        return self._particles

    def get_dead(self):
        return self._dead

    def set_dead(self, value):
        self._dead = value

    def load_level(self, map_id):
        self._tilemap.load('data/maps/' + str(map_id) + '.json')

        self._leaf_spawners = []
        for tree in self._tilemap.extract([('large_decor', 2)], keep=True):
            self._leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self._enemies = []
        for spawner in self._tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self._player.set_pos(spawner['pos'])
                self._player.set_air_time(0)
            else:
                # Condição para spawnar inimigos normais e rápidos juntos
                if random.random() < 0.5:  # 50% de chance de ser inimigo normal
                    self._enemies.append(Enemy(self, spawner['pos'], (8, 15)))
                else:  # 50% de chance de ser inimigo que atira mais rápido
                    self._enemies.append(FastShootingEnemy(self, spawner['pos'], (8, 15)))

        # Configuração de outros elementos do nível (projetéis, powerups, etc.)
        self._powerups = [PowerUp(100, 150, 'data/images/powerup.png')]  # Coloque as coordenadas corretas do powerup
        self._projectiles = []
        self._particles = []
        self._sparks = []

        self._scroll = [0, 0]
        self._dead = 0
        self._transition = -30

    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self._sfx['ambience'].play(-1)

        while True:
            self._display.fill((0, 0, 0, 0))
            self._display_2.blit(self._assets['background'], (0, 0))

            self._screenshake = max(0, self._screenshake - 1)

            if not len(self._enemies):
                self._transition += 1
                if self._transition > 30:
                    self._level = min(self._level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self._level)
            if self._transition < 0:
                self._transition += 1

            if self._dead:
                self._dead += 1
                # Diminua o valor de _dead para 20, para que a fase reinicie mais rápido
                if self._dead == 1:
                    self._sfx['hit'].play()  # Tocar o som de morte assim que o jogador morre
                if self._dead >= 0:  # Reinicia a fase mais rápido
                    self._transition = min(30, self._transition + 1)
                if self._dead > 30:
                    self.load_level(self._level)

            self._scroll[0] += (self._player.rect().centerx - self._display.get_width() / 2 - self._scroll[0]) / 30
            self._scroll[1] += (self._player.rect().centery - self._display.get_height() / 2 - self._scroll[1]) / 30
            render_scroll = (int(self._scroll[0]), int(self._scroll[1]))

            # Atualização do PowerUp
            for powerup in self._powerups.copy():
                powerup.update(self._player)  # Verifica se o player coleta o powerup
                powerup.render(self._display, offset=render_scroll)  # Renderiza o powerup na tela

            # Atualizar e renderizar partículas
            for particle in self._particles.copy():
                if particle.update():
                    self._particles.remove(particle)
                particle.render(self._display, offset=render_scroll)

            for spark in self._sparks.copy():
                if spark.update():
                    self._sparks.remove(spark)
                spark.render(self._display, offset=render_scroll)

            # Atualizar e renderizar os projéteis
            for projectile in self.get_projectiles().copy():
                projectile[0][0] += projectile[1]  # Atualizar a posição do projétil
                img = self.get_assets()['projectile']
                self._display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                # Verificar se o projétil colidiu com o jogador
                if self._player.rect().collidepoint(projectile[0]):
                    self.set_dead(1)  # Marca o jogador como morto
                    self.get_projectiles().remove(projectile)  # Remove o projétil após a colisão
                # Verificar se o projétil colidiu com algo sólido ou está fora do alcance
                elif self.get_tilemap().solid_check(projectile[0]) or projectile[2] > 360:
                    self.get_projectiles().remove(projectile)

            self._clouds.update()
            self._clouds.render(self._display_2, offset=render_scroll)

            self._tilemap.render(self._display, offset=render_scroll)

            for enemy in self._enemies.copy():
                kill = enemy.update(self._tilemap, (0, 0))
                enemy.render(self._display, offset=render_scroll)
                if kill:
                    self._enemies.remove(enemy)

            if not self._dead:
                self._player.update(self._tilemap, (self._movement[1] - self._movement[0], 0))
                self._player.render(self._display, offset=render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self._movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self._movement[1] = True
                    if event.key == pygame.K_UP:
                        if self._player.jump():
                            self._sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self._player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self._movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self._movement[1] = False

            self._display_2.blit(self._display, (0, 0))

            screenshake_offset = (random.random() * self._screenshake - self._screenshake / 2, random.random() * self._screenshake - self._screenshake / 2)
            self._screen.blit(pygame.transform.scale(self._display_2, self._screen.get_size()), screenshake_offset)
            pygame.display.update()
            self._clock.tick(60)


Game().run()
