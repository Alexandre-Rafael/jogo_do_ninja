import os
import pygame

BASE_IMG_PATH = 'data/images/'


def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images


class DeviceDisconnectedError(Exception):
    pass


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self._images = images
        self._loop = loop
        self._img_duration = img_dur
        self._done = False
        self._frame = 0

    # Getters and Setters
    def get_images(self):
        return self._images

    def set_images(self, images):
        self._images = images

    def get_loop(self):
        return self._loop

    def set_loop(self, loop):
        self._loop = loop

    def get_img_duration(self):
        return self._img_duration

    def set_img_duration(self, img_dur):
        self._img_duration = img_dur

    def get_done(self):
        return self._done

    def set_done(self, done):
        self._done = done

    def get_frame(self):
        return self._frame

    def set_frame(self, frame):
        self._frame = frame

    def copy(self):
        return Animation(self._images, self._img_duration, self._loop)

    def update(self):
        if self._loop:
            self._frame = (self._frame + 1) % (self._img_duration * len(self._images))
        else:
            self._frame = min(self._frame + 1, self._img_duration * len(self._images) - 1)
            if self._frame >= self._img_duration * len(self._images) - 1:
                self._done = True

    def img(self):
        return self._images[int(self._frame / self._img_duration)]
