import pygame


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
            self.collected = True
            self.kill()
            

    def render(self, surf, offset=(0, 0)):
        if not self.collected:
            surf.blit(self.image, (self.rect.x - offset[0], self.rect.y - offset[1]))
