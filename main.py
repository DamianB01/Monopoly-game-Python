"""
Moduł główny gry Monopoly.
Odpowiada za inicjalizację silnika Pygame, zarządzanie główną pętlą gry,
obsługę zdarzeń użytkownika oraz koordynację przepływu między menu a rozgrywką.
"""

import pygame
import sys
from menu import Menu
from board import Board
from player import Player
from dice import Dice
from field import Property, StationField
from game import Game
from ai_strategy import EasyStrategy, HardStrategy


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((1000, 800))
    pygame.display.set_caption("Monopoly Project")

    menu = Menu(screen)
    board = Board()
    dice = Dice()
    game_logic = Game()

    program_running = True

    while program_running:
        settings = menu.show_start_menu()
        if settings is None: break
        board.reset_fields()

        # --- PRZEŁĄCZANIE NA MUZYKĘ Z PLANSZY ---
        if menu.music_on:
            try:
                pygame.mixer.music.load("sounds/song.mp3")
                pygame.mixer.music.set_volume(0.03)
                pygame.mixer.music.play(-1)
            except:
                print("Nie znaleziono pliku sounds/song.mp3")

        difficulty_mode = settings["difficulty"]
        if difficulty_mode == "Trudny":
            strat = HardStrategy()
            starting_money_ai = 2500
        else:
            strat = EasyStrategy()
            starting_money_ai = 2000

        human_name = settings.get("player_name", "Gracz 1")
        players = []
        RED = (255, 50, 50)
        BLUE = (50, 50, 255)
        GREEN = (50, 255, 50)
        YELLOW = (255, 255, 50)

        colors = [RED, BLUE, GREEN, YELLOW]

        color_names = {
            RED: "Czerwony",
            BLUE: "Niebieski",
            GREEN: "Zielony",
            YELLOW: "Żółty"
        }

        # Dodaje Gracza (zawsze pierwszy kolor - Czerwony)
        players.append(Player(human_name, colors[0]))
        players[0].is_ai = False

        # Dodaje boty z dynamicznymi nazwami
        for i in range(settings["ai_count"]):
            current_color = colors[i+1]
            bot_name = color_names.get(current_color, f"Bot {i+1}")

            p_bot = Player(bot_name, current_color, is_ai=True, strategy=strat)
            p_bot.money = starting_money_ai
            players.append(p_bot)

        game_active = True
        clock = pygame.time.Clock()
        current_idx = 0
        hud_x = 730
        info_field = board.fields[0]

        while game_active:
            screen.fill((30, 30, 30))
            if not players:
                game_active = False
                break
            current_idx %= len(players)
            curr_p = players[current_idx]
            current_field = board.fields[curr_p.position]

            if len(players) > 0:
                current_idx %= len(players)
                curr_p = players[current_idx]
            else:
                game_active = False
                break

            # --- MECHANIKA WIĘZIENIA (ODSIADKA) ---
            if curr_p.is_in_jail:
                curr_p.jail_turns += 1
                game_logic.history.log(f"{curr_p.name} odsiaduje turę w więzieniu ({curr_p.jail_turns}/2)")
                game_logic.set_message(f"{curr_p.name} w więzieniu ({curr_p.jail_turns}/2)")
                pygame.time.delay(1200)

                # Po 2 turach wychodzi
                if curr_p.jail_turns >= 2:
                    curr_p.is_in_jail = False
                    curr_p.jail_turns = 0
                    game_logic.history.log(f"{curr_p.name} wychodzi z więzienia")
                    game_logic.set_message(f"{curr_p.name} wychodzi z więzienia!")

                current_idx = (current_idx + 1) % len(players)
                continue

            # Sprawdzanie czy gracz jest sam na polu
            players_on_field = [p for p in players if p.position == curr_p.position]
            is_alone = len(players_on_field) == 1

            # --- RYSOWANIE ---
            board.draw(screen)
            board.draw_center_decorations(screen)
            for i, p in enumerate(players): p.draw(screen, board, i)

            # --- HUD ---
            pygame.draw.rect(screen, (40, 40, 40), (hud_x - 10, 0, 1000, 800))
            current_y = 20
            for idx, p in enumerate(players):
                rect_p = pygame.Rect(hud_x - 5, current_y, 240, 35)
                bg_color = (60, 60, 60) if idx == current_idx else (30, 30, 30)
                pygame.draw.rect(screen, bg_color, rect_p, border_radius=5)
                if idx == current_idx:
                    pygame.draw.rect(screen, (0, 255, 0), rect_p, 2, border_radius=5)
                txt = board.hud_font_small.render(f"{p.name}: {p.money} zł", True, (255, 255, 255))
                screen.blit(txt, (hud_x + 5, current_y + 7))
                current_y += 42

            parking_rect = pygame.Rect(hud_x - 5, current_y, 240, 40)
            pygame.draw.rect(screen, (50, 80, 50), parking_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 215, 0), parking_rect, 2, border_radius=5)

            pool_txt = board.hud_font_small.render(f"Pula Parkingu: {game_logic.parking_pool} zł", True, (255, 215, 0))
            screen.blit(pool_txt, (hud_x + 5, current_y + 10))
            current_y += 55

            dice.draw(screen, hud_x + 20, current_y + 10, hud_x + 100, current_y + 10)
            btn_dice = pygame.Rect(hud_x, current_y + 65, 200, 40)
            dice_color = (200, 0, 0) if not curr_p.is_ai else (100, 100, 100)
            pygame.draw.rect(screen, dice_color, btn_dice, border_radius=10)
            screen.blit(board.hud_font_bold.render("RZUT KOŚCIĄ", True, (255, 255, 255)), (hud_x + 35, current_y + 72))

            # Wyświetlanie info o polu
            if not curr_p.is_ai: info_field = current_field
            board.draw_field_info(screen, info_field, hud_x, game_logic.message)

            btn_action = None

            # Sprawdza czy pole jest kupowalne (miasto lub dworzec)
            is_purchasable = isinstance(current_field, (Property, StationField))
            if not curr_p.is_ai and is_purchasable and is_alone:
                if current_field.owner is None and curr_p.money >= current_field.price:
                    btn_action = pygame.Rect(hud_x, 730, 200, 45)
                    pygame.draw.rect(screen, (0, 150, 0), btn_action, border_radius=10)

                    prefix = "DWORZEC" if current_field.type == "STATION" else "POLE"
                    txt_str = f"KUP {prefix}: {current_field.price}zł"
                    txt = board.hud_font_bold.render(txt_str, True, (255, 255, 255))
                    screen.blit(txt, txt.get_rect(center=btn_action.center))

                elif (isinstance(current_field, Property) and current_field.owner == curr_p and current_field.houses < 4):
                    next_house_cost = current_field.get_next_house_price()
                    if curr_p.money >= next_house_cost:
                        btn_action = pygame.Rect(hud_x, 730, 200, 45)
                        pygame.draw.rect(screen, (0, 100, 200), btn_action, border_radius=10)
                        txt = board.hud_font_bold.render(f"KUP DOM: {next_house_cost}zł", True, (255, 255, 255))
                        screen.blit(txt, txt.get_rect(center=btn_action.center))

            pygame.display.flip()

            # --- LOGIKA BOTÓW ---
            if curr_p.is_ai and game_active and current_idx == players.index(curr_p) and not board.animating_card:
                if not game_logic.turn_executed:
                    pygame.time.delay(1000)

                    # 1. ZAKUP DOMU
                    if isinstance(current_field, Property) and current_field.owner == curr_p:
                        while curr_p.strategy.should_build_house(curr_p, current_field, board.fields):
                            success = game_logic.buy_house(curr_p, current_field, players)
                            if success:
                                game_logic.history.log(f"BOT {curr_p.name} ({curr_p.strategy.name()}) kupił dom na {current_field.name}")
                            else:
                                break

                    # 2. KUPNO POLA
                    elif isinstance(current_field, (Property, StationField)) and current_field.owner is None:
                        if curr_p.strategy.should_buy_property(curr_p, current_field, board.fields):
                            curr_p.money -= current_field.price
                            current_field.owner = curr_p
                            curr_p.properties.append(current_field)
                            game_logic.history.log(f"BOT {curr_p.name} ({curr_p.strategy.name()}) kupił: {current_field.name}")
                            game_logic.set_message(f"{curr_p.name} kupuje {current_field.name}")
                        else:
                            game_logic.history.log(f"BOT {curr_p.name} odrzucił zakup: {current_field.name}")

                    roll_val, is_double, to_jail = dice.roll()
                    game_logic.history.log(f"BOT {curr_p.name} rzucił: {roll_val} (Dublet: {is_double})")
                    game_logic.total_turns += 1
                    game_logic.turn_executed = True
                    if to_jail:
                        game_logic.send_to_jail(curr_p)
                        game_logic.turn_executed = False
                        game_logic.history.log(f"BOT {curr_p.name} idzie do więzienia (3 dublety/pole)")
                        game_logic.set_message(f"{curr_p.name} idzie do WIĘZIENIA!")
                        current_idx = (current_idx + 1) % len(players)
                    else:
                        curr_p.move(roll_val)
                        new_field = board.fields[curr_p.position]
                        game_logic.handle_field_landing(curr_p, new_field, board, roll_val)
                        game_logic.history.log(f"BOT {curr_p.name} przeszedł na pole {new_field.name}")

                        game_logic.check_bankruptcy(players)

                        if len(players) <= 1:
                            if len(players) == 1: winner_name = players[0].name
                            game_active = False
                        else:
                            if not is_double and not board.animating_card:
                                game_logic.turn_executed = False
                                current_idx = (current_idx + 1) % len(players)
                            else:
                                game_logic.history.log(f"BOT {curr_p.name} ma dublet - rzuca ponownie...")
                                game_logic.turn_executed = False
                                pygame.display.flip()
                                pygame.time.delay(1000)
                            continue

            is_double = False

            # --- ZDARZENIA ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if board.animating_card and board.card_angle >= 180:
                        board.animating_card = False
                        game_logic.history.log(f"Zamknięto kartę szansy przez {curr_p.name}")
                        if curr_p.is_ai:
                            if not is_double:
                                game_logic.turn_executed = False
                                current_idx = (current_idx + 1) % len(players)
                        else:
                            if not is_double:
                                game_logic.turn_executed = False
                                current_idx = (current_idx + 1) % len(players)
                        continue

                    # Podgląd pól
                    for i in range(40):
                        fx, fy, fw, fh = board.get_field_rect(i)
                        if pygame.Rect(fx + board.offset_x, fy + board.offset_y, fw, fh).collidepoint(event.pos):
                            info_field = board.fields[i]

                    # Kliknięcie w akcję
                    if btn_action and btn_action.collidepoint(event.pos):
                        board.play_click()
                        if current_field.owner is None and curr_p.money >= current_field.price:
                            curr_p.money -= current_field.price
                            current_field.owner = curr_p
                            curr_p.properties.append(current_field)
                            type_name = "Dworzec" if current_field.type == "STATION" else "Pole"
                            game_logic.history.log(f"{curr_p.name} kupił {current_field.name} za {current_field.price}zł")
                            game_logic.set_message(f"Kupiono {type_name.lower()}: {current_field.name}")
                        else:
                            game_logic.buy_house(curr_p, current_field, players)

                    # Rzut kością
                    if btn_dice.collidepoint(event.pos) and not curr_p.is_ai:
                        game_logic.turn_executed = False
                        board.play_click()
                        roll_val, is_double, to_jail = dice.roll()
                        game_logic.history.log(f"Gracz {curr_p.name} rzucił: {roll_val} (Dublet: {is_double})")
                        game_logic.total_turns += 1
                        if to_jail:
                            game_logic.send_to_jail(curr_p)
                            game_logic.history.log(f"ALARM: {curr_p.name} idzie do więzienia (3 dublety/pole)")
                            game_logic.set_message("Idziesz do WIĘZIENIA!")
                            current_idx = (current_idx + 1) % len(players)
                        else:
                            curr_p.move(roll_val)
                            new_field = board.fields[curr_p.position]
                            game_logic.handle_field_landing(curr_p, new_field, board, roll_val)

                        game_logic.check_bankruptcy(players)
                        if len(players) <= 1:
                            if len(players) == 1:
                                winner_name = players[0].name
                            game_active = False
                        else:
                            if not is_double and not board.animating_card:
                                current_idx = (current_idx + 1) % len(players)

            if len(players) == 1:
                winner = players[0]
                winner_name = winner.name
                game_logic.history.log(f"KONIEC GRY. Zwyciężył: {winner_name}")
                game_logic.save_results(winner)
                game_active = False

            if len(players) > 0:
                current_idx %= len(players)
                curr_p = players[current_idx]
            else:
                game_active = False

            clock.tick(60)

        if menu.show_end_menu(winner_name) != "RESTART": program_running = False

    pygame.quit();
    sys.exit()


if __name__ == "__main__":
    main()
