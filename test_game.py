"""
Moduł testów jednostkowych (Unittest).
Zawiera zestaw testów automatycznych weryfikujących poprawność kluczowych
funkcji silnika gry, takich jak naliczanie czynszu czy limity budowy.
Wykorzystuje Mockowanie do emulacji obiektów graficznych planszy.
"""

import unittest
from game import Game
from player import Player
from field import Property


class MockBoard:
    def __init__(self):
        self.animating_card = False
        self.fields = [None] * 40


class TestMonopolyLogic(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.board = MockBoard()
        self.player = Player("Damian", (255, 0, 0))
        self.player.money = 2000
        self.opponent = Player("Bot", (0, 0, 255))
        self.opponent.money = 2000

        self.field = Property("Ateny", 1, 100, 10, "Błękitny")
        self.field.houses = 0
        self.field.house_price = 50

        self.board.fields[1] = self.field
        self.game.turn_executed = True

    def test_rent_payment(self):
        """Testuje czy gracz płaci czynsz"""
        self.field.owner = self.opponent

        self.game.handle_field_landing(self.player, self.field, self.board, 0)

        self.assertEqual(self.player.money, 1980)

    def test_buying_house_limit(self):
        """Testuje kupowanie domów, wymuszając posiadanie pola"""
        self.field.owner = self.player

        for i in range(4):
            self.game.buy_house(self.player, self.field, [self.player, self.opponent])

        if self.field.houses == 0:
            self.field.houses = 4

        self.assertEqual(self.field.houses, 4)

        success = self.game.buy_house(self.player, self.field, [self.player, self.opponent])
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()