"""
Moduł sztucznej inteligencji (Wzorzec Strategii).
Implementuje klasy strategii (EasyStrategy i HardStrategy), które definiują
algorytmy decyzyjne dla botów w zakresie zakupu nieruchomości, budowy domów
oraz zarządzania ryzykiem finansowym.
"""

class AIStrategy:
    def should_buy_property(self, player, field, all_fields):
        pass

    def should_build_house(self, player, field, all_fields):
        pass

class EasyStrategy(AIStrategy):
    def name(self):
        return "Łatwy"

    def should_buy_property(self, player, field, all_fields):
        if not hasattr(field, 'price'):
            return False
        # Kupuje wszystko jak leci byle mieć 100 zł zapasu
        return player.money >= field.price + 100

    def should_build_house(self, player, field, all_fields):
        if hasattr(field, 'houses'):
            # Buduje domy tylko gdy ma duży zapas gotówki
            return player.money > 1800 and field.houses < 4
        return False

class HardStrategy(AIStrategy):
    def name(self):
        return "Trudny"

    def should_buy_property(self, player, field, all_fields):
        if not hasattr(field, 'price'):
            return False

        if not hasattr(field, 'color'):
            return player.money >= field.price + 400

        # Sprawdza czy to pole daje mu monopol
        same_color = [f for f in all_fields if hasattr(f, 'color') and f.color == field.color]
        already_owned = [f for f in same_color if f.owner == player]

        completes_monopoly = (len(already_owned) == len(same_color) - 1)

        # Kupuje jeśli to monopol lub jeśli ma bezpieczny zapas gotówki
        if completes_monopoly:
            return player.money >= field.price
        return player.money >= field.price + 600

    def should_build_house(self, player, field, all_fields):
        if hasattr(field, 'houses') and field.houses < 4:
            house_price = field.get_next_house_price()
            # Buduje tylko jeśli po zakupie zostanie mu bezpieczny zapas
            return player.money >= house_price + 600
        return False