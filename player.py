"""
Moduł reprezentacji uczestników gry.
Definiuje klasę Player, przechowującą stan majątkowy, pozycję na planszy,
posiadane nieruchomości oraz flagi stanu (np. pobyt w więzieniu, bankructwo).
Obsługuje zarówno graczy ludzkich, jak i instancje sterowane przez AI.
"""

import pygame


class Player:
    def __init__(self, name, color, position=0, is_ai=False, strategy=None):
        self.name = name
        self.color = color
        self._position = position
        self._money = 2000
        self.properties = []
        self.is_in_jail = False
        self.jail_turns = 0
        self.is_ai = is_ai
        self.strategy = strategy

    # --- ENKAPSULACJA PIENIĘDZY ---
    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, value):
        self._money = value

    # --- ENKAPSULACJA POZYCJI ---
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value % 40

    def move(self, steps):
        """Przesuwa gracza o daną liczbę pól i obsługuje przejście przez start"""
        old_position = self.position
        self.position += steps

        if self.position < old_position and steps > 0:
            self.money += 200

    def can_afford(self, property_field):
        return self.money >= property_field.price and property_field.owner is None

    def buy_property(self, property_field):
        self.money -= property_field.price
        property_field.owner = self
        self.properties.append(property_field)

    def draw(self, screen, board, player_index):
        """Rysuje pionek na podstawie współrzędnych z obiektu Board"""
        fx, fy, fw, fh = board.get_field_rect(self.position)

        base_x = fx + board.offset_x + fw // 2
        base_y = fy + board.offset_y + fh // 2

        offsets = [(-12, -12), (12, -12), (-12, 12), (12, 12)]
        off_x, off_y = offsets[player_index % 4]

        pygame.draw.circle(screen, self.color, (base_x + off_x, base_y + off_y), 12)
        pygame.draw.circle(screen, (0, 0, 0), (base_x + off_x, base_y + off_y), 12, 2)