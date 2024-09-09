import pygame
from src.check_devices.device_disconnected_error import DeviceDisconnectedError

class CheckDevice:
    @staticmethod
    def check_devices(self):
        if not pygame.key.get_focused() or not pygame.mouse.get_focused():
            raise DeviceDisconnectedError("Teclado ou mouse desconectado!")

