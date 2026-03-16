"""
Moduł definicji pól planszy.
Zawiera hierarchię klas pól (m.in. Property, Station, SpecialField).
Implementuje logikę przynależności pól, obliczanie czynszów,
zarządzanie poziomem rozbudowy (domy/hotele) oraz atrybuty ekonomiczne nieruchomości.
"""

import random

class Field:
    """Klasa bazowa dla wszystkich pól na planszy."""
    def __init__(self, name, index, type="SPECIAL"):
        self.name = name
        self.index = index
        self.type = type

class Property(Field):
    """Klasa dla nieruchomości"""
    def __init__(self, name, index, price, rent, color):
        super().__init__(name, index, type="PROPERTY")
        self.price = price
        self.rent = rent
        self.color = color
        self.owner = None
        self._houses = 0

    @property
    def houses(self):
        return self._houses

    @houses.setter
    def houses(self, value):
        if 0 <= value <= 5:
            self._houses = value
        else:
            print("BŁĄD: Nieprawidłowa liczba domów!")

    def get_next_house_price(self):
        """
        Cena domu zależy od potencjału pola (rent).
        Bazowa cena domu to rent * 10 (np. czynsz 10 -> dom 100).
        Każdy kolejny dom jest o 50% droższy od bazowej ceny.
        """
        base_cost = self.rent * 10
        multiplier = 1 + (self.houses * 0.5)
        return int(base_cost * multiplier)

    def get_current_rent(self, all_fields):
        """Oblicza czynsz, uwzględniając domy oraz bonus za posiadanie kompletu kolorów"""
        multipliers = [1, 5, 15, 40, 80]
        base_rent = self.rent * multipliers[self.houses]
        # Mechanizm Monopolu:
        # Jeśli gracz ma wszystkie pola tego koloru to czynsz x2
        if self.houses == 0 and self.owner is not None:
            color_group = [f for f in all_fields if isinstance(f, Property) and f.color == self.color]
            owns_all = all(f.owner == self.owner for f in color_group)
            if owns_all:
                return base_rent * 2

        return base_rent

class TaxField(Field):
    def __init__(self, name, index, amount):
        super().__init__(name, index, type="TAX")
        self.amount = amount

class ChanceField(Field):
    """To pole dziedziczy po Field i wyzwala losowanie karty"""
    def __init__(self, name, index, card_type="CHANCE"):
        super().__init__(name, index, type=card_type)

class UtilityField(Field):
    def __init__(self, name, index, multiplier):
        super().__init__(name, index, type="UTILITY")
        self.multiplier = multiplier
        self.owner = None

class StationField(Field):
    def __init__(self, name, index):
        super().__init__(name, index, type="STATION")
        self.price = 500
        self.owner = None

    def get_rent(self):
        """Oblicza czynsz na podstawie liczby posiadanych dworców przez właściciela"""
        if not self.owner:
            return 0

        count = 0
        for p in self.owner.properties:
            if isinstance(p, StationField):
                count += 1
        if count == 1: return 100
        if count == 2: return 200
        if count == 3: return 400
        if count == 4: return 800
        return 0

class ParkingField(Field):
    def __init__(self, name, index):
        super().__init__(name, index, type="PARKING")

class JailField(Field):
    def __init__(self, name, index):
        super().__init__(name, index, type="JAIL")

class CommunityChestField(Field):
    """U mnie community chest to nie karta, a stała premia"""
    def __init__(self, name, index):
        super().__init__(name, index, "CHEST")
        self.amount = 200


class ChanceCard:
    """Klasa reprezentująca pojedynczą kartę"""
    def __init__(self, text, action_type, value=0):
        self.text = text
        self.action_type = action_type
        self.value = value

class ChanceDeck:
    """Klasa zarządzająca talią, z której korzystają pola szansy"""
    def __init__(self):
        self.cards = [
            ChanceCard("BANK PŁACI CI DYWIDENDĘ: +150 zł", "MONEY", 150),
            ChanceCard("MANDAT ZA SZYBKĄ JAZDĘ: -50 zł", "MONEY", -50),
            ChanceCard("WYGRAŁEŚ W KONKURSIE PIĘKNOŚCI: +100 zł", "MONEY", 100),
            ChanceCard("OPŁATA ZA SZKOŁĘ: -250 zł", "MONEY", -250),
            ChanceCard("IDŹ DO STARTU (POBIERZ 200 zł)", "MOVE", 0),
            ChanceCard("COFNIJ SIĘ O 3 POLA", "MOVE_RELATIVE", -3),
            ChanceCard("IDŹ BEZPOŚREDNIO DO WIĘZIENIA", "JAIL", 10)
        ]
        random.shuffle(self.cards)

    def draw(self):
        card = self.cards.pop(0)
        self.cards.append(card)
        return card