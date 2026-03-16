"""
Moduł silnika logiki gry.
Klasa Game zarządza zasadami gry: transferami gotówki, systemem tur,
obsługą lądowania na polach, zapisywaniem logów w konsoli oraz weryfikacją warunków zwycięstwa.
Jest niezależna od warstwy graficznej, co umożliwia jej testowanie jednostkowe.
"""

from field import Property, TaxField, UtilityField, StationField, ParkingField, JailField, ChanceDeck, ChanceField, CommunityChestField
import random
import datetime
from collections import UserList

class Game:
    def __init__(self):
        self.message = "Witaj w Monopoly!"
        self.parking_pool = 0
        self.total_turns = 0
        self.deck = ChanceDeck()
        self.history = GameLogger()
        self.history.log("Gra zainicjalizowana.")
        self.turn_executed = False

    def set_message(self, text):
        self.message = text

    def handle_field_landing(self, player, field, board, dice_roll=0):
        """Logika po wejściu gracza na pole (czynsz, podatki, własność)"""

        if board.animating_card:
            return

        if isinstance(field, Property):
            if field.owner and field.owner != player:
                rent_to_pay = field.get_current_rent(board.fields)
                player.money -= rent_to_pay
                field.owner.money += rent_to_pay
                self.set_message(f"{player.name} płaci {rent_to_pay}zł czynszu dla {field.owner.name}")

                if player.money < 0:
                    self.set_message(f"GRACZ {player.name} ZBANKRUTOWAŁ!")

            elif field.owner == player:
                if player.is_ai and player.strategy:
                    if player.strategy.should_build_house(player, field, board.fields):
                        success = self.buy_house(player, field, [])
                        if success:
                            self.set_message(f"{player.name} buduje dom na {field.name}!")

                if field.houses < 4:
                    self.set_message(f"To Twoje pole ({field.name}). Możesz dokupić dom!")
                else:
                    self.set_message(f"Odwiedzasz swój hotel na {field.name}")

            elif field.owner is None:
                if player.is_ai and player.strategy:
                    if player.strategy.should_buy_property(player, field, board.fields):
                        player.buy_property(field)
                        self.set_message(f"{player.name} kupuje {field.name} za {field.price}zł")
                    else:
                        self.set_message(f"{player.name} oszczędza i nie kupuje {field.name}")
                else:
                    self.set_message(f"{player.name} stanął na wolnym polu: {field.name}")

        elif isinstance(field, TaxField):
            player.money -= field.amount
            self.parking_pool += field.amount
            self.set_message(f"{player.name} płaci podatek: {field.amount} zł. Pula parkingu: {self.parking_pool} zł")
            if player.money < 0:
                self.set_message(f"BANKRUCTWO! {player.name} nie udźwignął podatków!")

        elif isinstance(field, UtilityField):
            if field.name == "PRĄD":
                amount = dice_roll * 50
                player.money -= amount
                self.set_message(f"Opłata za prąd: {amount}zł")
            elif field.name == "WODOCIĄGI":
                amount = dice_roll * 100
                player.money -= amount
                self.set_message(f"Opłata za wodociągi: {amount}zł")

        elif isinstance(field, StationField):
            if field.owner and field.owner != player:
                rent = field.get_rent()
                player.money -= rent
                field.owner.money += rent
                self.set_message(f"{player.name} płaci {rent}zł czynszu za {field.name}")
            elif field.owner is None:
                self.set_message(f"{field.name} jest wolny! Cena: 500zł")

        elif isinstance(field, ParkingField):
            if self.parking_pool > 0:
                player.money += self.parking_pool
                self.set_message(f"DARMOWY PARKING! {player.name} zgarnia pulę {self.parking_pool} zł!")
                self.parking_pool = 0
            else:
                self.set_message(f"{player.name} odpoczywa na parkingu. Pula jest pusta.")

        elif isinstance(field, JailField):
            if field.index == 30:
                self.send_to_jail(player)
            else:
                self.set_message(f"{player.name} odwiedza znajomych w więzieniu.")

        elif isinstance(field, ChanceField):
            # 1. Losujemy kartę i stronę wylotu
            card = self.deck.draw()
            # 2. Animację odpalamy tylko, jeśli gracz nie jest botem
            if not getattr(player, 'is_ai', False):  # Sprawdza flagę is_ai
                board.current_player_name = player.name
                board.current_side = random.choice(["LEFT", "RIGHT"])
                board.current_card = card
                board.animating_card = True
                board.card_angle = 0
                self.set_message(f"{player.name} dobiera kartę...")
            else:
                self.set_message(f"Bot {player.name} wylosował: {card.text}")
            self.apply_card_effect(player, card, board)

        elif isinstance(field, CommunityChestField):
            player.money += field.amount
            self.set_message(f"{player.name} otrzymuje {field.amount}zł z Kasy Społecznej!")

    def buy_house(self, player, prop, all_players):
        """Kupno domu"""
        if not isinstance(prop, Property) or prop.owner != player:
            self.set_message("To nie jest Twoje pole!")
            return False

        if player.position != prop.index:
            self.set_message("Musisz stać na swoim polu!")
            return False

        if prop.houses >= 4:
            self.set_message("Maksymalnie 4 domy!")
            return False

        if player.money < 100:
            self.set_message("Brak pieniędzy!")
            return False

        current_cost = prop.get_next_house_price()
        if player.money < current_cost:
            self.set_message(f"Brak pieniędzy! Potrzebujesz {current_cost}zł")
            return False
        player.money -= current_cost
        prop.houses += 1
        self.set_message(f"Wybudowano dom! Następny kosztuje {prop.get_next_house_price()}zł")
        return True

    def send_to_jail(self, player):
        player.position = 10
        player.is_in_jail = True
        player.jail_turns = 0
        self.history.log(f"{player.name} trafia do WIĘZIENIA")
        self.set_message(f"{player.name} trafia do WIĘZIENIA!")

    def check_bankruptcy(self, players):
        """Usuwa graczy z ujemnym stanem konta"""
        for p in players[:]:
            if p.money < 0:
                self.history.log(f"--- BANKRUCTWO: {p.name} posiada {p.money}zł i odpada z gry! ---")
                self.set_message(f"GRACZ {p.name} ZBANKRUTOWAŁ!")
                for prop in p.properties:
                    prop.owner = None
                    if hasattr(prop, 'houses'):
                        prop.houses = 0
                self.history.log(f"Zwolniono nieruchomości należące do {p.name}")
                players.remove(p)

    def apply_card_effect(self, player, card, board):
        """Wykonuje akcję zapisaną na karcie szansy"""
        if card.action_type == "MONEY":
            player.money += card.value
            if card.value > 0:
                self.set_message(f"Zysk: {card.text}")
            else:
                self.set_message(f"Strata: {card.text}")

        elif card.action_type == "MOVE":
            old_pos = player.position
            player.position = card.value

            if player.position < old_pos and card.value != 10:
                player.money += 200
                self.set_message(f"Przechodzisz przez start! +200zł")

        elif card.action_type == "MOVE_RELATIVE":
            player.position = (player.position + card.value) % 40
            new_field = board.fields[player.position]
            self.handle_field_landing(player, new_field, board)

        elif card.action_type == "JAIL":
            self.send_to_jail(player)
            if not player.is_ai:
                board.animating_card = True

        self.check_bankruptcy([player])

    def save_results(self, winner):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            name = winner.name
            money = winner.money
            turns = self.total_turns
            with open("results.txt", "a", encoding="utf-8") as f:
                line = f"[{timestamp}] Zwycięzca: {name} | Pieniądze: {money} zł | Wszystkie rzuty kostką w trakcie rozgrywki: {turns}\n"
                f.write(line)
            print(f"Statystyki zapisane: {line}")
        except Exception as e:
            print(f"Błąd zapisu wyników: {e}")

class GameLogger(UserList):
    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.append(entry)
        print(entry)