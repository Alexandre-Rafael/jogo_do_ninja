import random

from scripts.clouds.cloud import Cloud


class MultipleClouds:
    def __init__(self, cloud_images, count=16):
        self._clouds = []

        for i in range(count):
            self._clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images),
                                      random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        self._clouds.sort(key=lambda x: x.get_depth())

    def update(self):
        for cloud in self._clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0)):
        for cloud in self._clouds:
            cloud.render(surf, offset=offset)
