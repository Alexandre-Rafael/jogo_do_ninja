import math
import pygame

class Spark:
    def __init__(self, pos, angle, speed):
        self._pos = list(pos)
        self._angle = angle
        self._speed = speed
        
   
    def get_pos(self):
        return self._pos

    def set_pos(self, pos):
        self._pos = pos

    def get_angle(self):
        return self._angle

    def set_angle(self, angle):
        self._angle = angle

    def get_speed(self):
        return self._speed

    def set_speed(self, speed):
        self._speed = speed
        
    def update(self):
        self._pos[0] += math.cos(self._angle) * self._speed
        self._pos[1] += math.sin(self._angle) * self._speed
        
        self._speed = max(0, self._speed - 0.1)
        return not self._speed
    
    def render(self, surf, offset=(0, 0)):
        render_points = [
            (self._pos[0] + math.cos(self._angle) * self._speed * 3 - offset[0], self._pos[1] + math.sin(self._angle) * self._speed * 3 - offset[1]),
            (self._pos[0] + math.cos(self._angle + math.pi * 0.5) * self._speed * 0.5 - offset[0], self._pos[1] + math.sin(self._angle + math.pi * 0.5) * self._speed * 0.5 - offset[1]),
            (self._pos[0] + math.cos(self._angle + math.pi) * self._speed * 3 - offset[0], self._pos[1] + math.sin(self._angle + math.pi) * self._speed * 3 - offset[1]),
            (self._pos[0] + math.cos(self._angle - math.pi * 0.5) * self._speed * 0.5 - offset[0], self._pos[1] + math.sin(self._angle - math.pi * 0.5) * self._speed * 0.5 - offset[1]),
        ]
        
        pygame.draw.polygon(surf, (255, 255, 255), render_points)
