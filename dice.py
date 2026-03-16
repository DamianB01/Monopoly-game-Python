"""
Moduł mechaniki losowości.
Odpowiada za symulację rzutu dwiema kośćmi, wykrywanie dubletów
oraz odpowiadania za wczytanie grafik kości.
"""

import pygame
import random
import os

class Dice:
    def __init__(self):
        self.double_count = 0
        self.roll_sum = 2
        self.d1 = 1
        self.d2 = 1
        self.images = self._load_images()

    def _load_images(self):
        """Ładuje 6 grafik kostek z folderu images"""
        imgs = []
        try:
            for i in range(1, 7):
                path = os.path.join("images", f"dice{i}.png")
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (50, 50))
                imgs.append(img)
            return imgs
        except pygame.error:
            print("Uwaga: Nie znaleziono grafik kostek w folderze 'images'.")
            return None

    def roll(self):
        self.d1 = random.randint(1,6)
        self.d2 = random.randint(1,6)
        self.roll_sum = self.d1 + self.d2
        is_double = (self.d1 == self.d2)

        if is_double:
            self.double_count += 1
        else:
            self.double_count = 0

        sent_to_jail = self.double_count >= 3
        if sent_to_jail:
            self.double_count = 0

        return self.roll_sum, is_double, sent_to_jail

    def draw(self, screen, x1, y1, x2, y2):
        """Rysuje obie kostki na podanych współrzędnych"""
        if self.images:
            screen.blit(self.images[self.d1 - 1], (x1, y1))
            screen.blit(self.images[self.d2 - 1], (x2, y2))
        else:
            # Jeśli brak grafik, rysujemy białe kwadraty z liczbami
            font = pygame.font.SysFont("Arial", 30, bold=True)
            for i, val in enumerate([self.d1, self.d2]):
                pos_x = x1 if i == 0 else x2
                pos_y = y1 if i == 0 else y2
                rect = pygame.Rect(pos_x, pos_y, 50, 50)
                pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=5)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=5)
                txt = font.render(str(val), True, (0, 0, 0))
                screen.blit(txt, txt.get_rect(center=rect.center))

    def reset(self):
        self.double_count = 0