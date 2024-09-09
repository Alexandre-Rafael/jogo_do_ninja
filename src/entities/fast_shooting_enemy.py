import time
from src.entities.enemy import Enemy


class FastShootingEnemy(Enemy):
    def __init__(self, game, pos, size):
        super().__init__(game, pos, size)
        self.shooting_interval = 1.5 
        self.last_shot_time = time.time()

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        if time.time() - self.last_shot_time > self.shooting_interval:
            self.shoot()
            self.last_shot_time = time.time()

    def shoot(self):
        # Método para atirar
        super().shoot()
