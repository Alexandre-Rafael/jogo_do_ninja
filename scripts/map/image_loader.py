import os
import pygame

BASE_IMG_PATH = 'data/images/'

class ImageLoader:
    def __init__(self, base_path=BASE_IMG_PATH):
        self.base_path = base_path

    def load_image(self, path):
        """Carrega uma imagem e define a colorkey para remover o fundo preto."""
        img = pygame.image.load(self.base_path + path).convert()
        img.set_colorkey((0, 0, 0))  
        return img

    def load_images(self, path):
        """Carrega várias imagens de um diretório, em ordem alfabética."""
        images = []
        full_path = self.base_path + path
        for img_name in sorted(os.listdir(full_path)):
            if img_name.endswith(('.png', '.jpg', '.jpeg')): 
                images.append(self.load_image(path + '/' + img_name))
        return images
