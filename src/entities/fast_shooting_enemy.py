import random
import time
from src.entities.enemy import Enemy


class FastShootingEnemy(Enemy):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size)
        self.shooting_interval = 1.5 
        self.last_shot_time = time.time()
        self.jump_power = -6 
        self.gravity = 1  
        self.velocity_y = 0  
        self.on_ground = False 

    def update(self, tilemap, movement=(0, 0)):
        # Atualizar o movimento horizontal e flip
        if self.get_walking():
            if tilemap.solid_check((self.rect().centerx + (-7 if self.get_flip() else 7), self.get_pos()[1] + 23)):
                if self.get_collisions()['right'] or self.get_collisions()['left']:
                    self.set_flip(not self.get_flip()) 
                else:
                    movement = (movement[0] - 0.5 if self.get_flip() else 0.5, movement[1])
            else:
                self.set_flip(not self.get_flip()) 
            self.set_walking(max(0, self.get_walking() - 1))

        elif random.random() < 0.01:
            self.set_walking(random.randint(30, 120))

        self.velocity_y += self.gravity
        self.set_pos((self.get_pos()[0], self.get_pos()[1] + self.velocity_y))

        ground_rects = tilemap.physics_rects_around(self.get_pos())
        if any(self.rect().colliderect(rect) for rect in ground_rects):
            self.velocity_y = 0
            self.on_ground = True 
            self.set_pos((self.get_pos()[0], ground_rects[0].top - self.rect().height))
        else:
            self.on_ground = False  

        
        if self.on_ground and random.random() < 0.02:  # 2% de chance de pular a cada frame
            self.velocity_y = self.jump_power

        super().update(tilemap, movement=movement)

        if time.time() - self.last_shot_time > self.shooting_interval:
            self.shoot()
            self.last_shot_time = time.time()

        if movement[0] != 0:
            self.set_action('run')
        elif not self.on_ground:
            self.set_action('jump')
        else:
            self.set_action('idle')

    def shoot(self):
        # Método para atirar
        super().shoot()
