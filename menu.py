"""
Moduł interfejsu startowego.
Zawiera klasę Menu, która obsługuje ekran powitalny, ekran końcowy, interaktywne pola tekstowe
do wprowadzania imion graczy oraz przyciski wyboru liczby przeciwników.
Wykorzystuje własne mechanizmy walidacji danych wejściowych.
"""

import pygame
import sys


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_main = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_sub = pygame.font.SysFont("Arial", 30)

        # Inicjalizacja dźwięku
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.music_on = True

        # Dźwięk kliknięcia
        try:
            self.click_sound = pygame.mixer.Sound("sounds/click.mp3")
        except:
            self.click_sound = None

        # Tło
        try:
            self.background = pygame.image.load("images/background.jpg")
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
        except:
            self.background = pygame.Surface(screen.get_size())
            self.background.fill((40, 40, 40))

        self.ai_count = 1
        self.difficulty = "Łatwy"

        self.player_name = "Gracz 1"
        self.input_active = False

    def draw_button(self, text, font, x, y, active_color=(0, 255, 0), inactive_color=(255, 255, 255)):
        mouse_pos = pygame.mouse.get_pos()
        img_temp = font.render(text, True, inactive_color)
        rect = img_temp.get_rect(center=(x, y))
        is_hovered = rect.collidepoint(mouse_pos)
        color = active_color if is_hovered else inactive_color
        img = font.render(text, True, color)
        self.screen.blit(img, rect)
        return rect, is_hovered

    def draw_text(self, text, font, color, x, y):
        """Pomocnicza metoda do rysowania statycznego tekstu na środku podanych współrzędnych."""
        img = font.render(text, True, color)
        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)
        return rect

    def show_start_menu(self):
        running = True
        if self.music_on:
            try:
                pygame.mixer.music.load("sounds/music.mp3")
                pygame.mixer.music.set_volume(0.05)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Błąd ładowania muzyki menu: {e}")
        while running:
            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            # --- Nagłówek ---
            self.draw_button("MONOPOLY", self.font_main, 500, 80, (255, 215, 0), (255, 215, 0))

            # --- IMIĘ GRACZA ---
            is_name_valid = len(self.player_name.strip()) > 0
            self.draw_text("Twoje imię:", self.font_sub, (255, 255, 255), 500, 170)
            input_color = (0, 255, 0) if self.input_active else (255, 255, 255)

            display_text = self.player_name if self.player_name else " "
            name_img = self.font_sub.render(display_text, True, input_color)
            name_rect = name_img.get_rect(center=(500, 220))

            field_rect = pygame.Rect(0, 0, 250, 45)
            field_rect.center = (500, 220)

            pygame.draw.rect(self.screen, (20, 20, 20), field_rect, border_radius=8)
            pygame.draw.rect(self.screen, input_color, field_rect, 2, border_radius=8)

            self.screen.blit(name_img, name_rect)
            h_name = field_rect.collidepoint(pygame.mouse.get_pos())

            # --- Liczba AI ---
            img_ai = self.font_sub.render(f"Liczba graczy AI: {self.ai_count}", True, (255, 255, 255))
            self.screen.blit(img_ai, img_ai.get_rect(center=(500, 290)))  # Zmienione z 220 na 290
            btn_minus, h_minus = self.draw_button("[ - ]", self.font_sub, 400, 330, (255, 0, 0))
            btn_plus, h_plus = self.draw_button("[ + ]", self.font_sub, 600, 330, (0, 255, 0))

            # --- Trudność ---
            img_diff = self.font_sub.render(f"Poziom trudności: {self.difficulty}", True, (255, 255, 255))
            self.screen.blit(img_diff, img_diff.get_rect(center=(500, 405)))
            btn_diff, h_diff = self.draw_button("[ Zmień trudność ]", self.font_sub, 500, 450, (100, 100, 255))

            # --- MUZYKA ---
            music_text = "Muzyka: ON" if self.music_on else "Muzyka: OFF"
            music_color = (0, 255, 0) if self.music_on else (255, 0, 0)
            btn_music, h_music = self.draw_button(music_text, self.font_sub, 500, 530, music_color, music_color)

            # --- START ---
            if is_name_valid:
                btn_start, h_start = self.draw_button("ROZPOCZNIJ GRĘ", self.font_main, 500, 680, (255, 255, 0))
            else:
                self.draw_text("WPISZ IMIĘ, ABY ZACZĄĆ", self.font_sub, (255, 100, 100), 500, 680)
                h_start = False

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # OBSŁUGA KLAWIATURY (Wpisywanie imienia)
                if event.type == pygame.KEYDOWN and self.input_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.input_active = False
                    elif len(self.player_name) < 12:  # Limit długości
                        self.player_name += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.click_sound: self.click_sound.play()

                    if h_name:
                        self.input_active = True
                    else:
                        self.input_active = False

                    if h_minus:
                        self.ai_count = max(1, self.ai_count - 1)
                    elif h_plus:
                        self.ai_count = min(3, self.ai_count + 1)
                    elif h_diff:
                        self.difficulty = "Trudny" if self.difficulty == "Łatwy" else "Łatwy"
                    elif h_music:
                        # Przełączanie muzyki
                        self.music_on = not self.music_on
                        if self.music_on:
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    elif h_start:
                        # Płynne wyciszenie przed wyjściem z menu
                        pygame.mixer.music.fadeout(2000)
                        pygame.time.delay(500)
                        return {"ai_count": self.ai_count, "difficulty": self.difficulty, "player_name": self.player_name}

    def show_end_menu(self, winner_name):
        """Wyświetla podsumowanie gry i zwycięzcę."""
        pygame.mixer.music.stop()

        running = True
        while running:
            # Tło
            self.screen.blit(self.background, (0, 0))
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # --- Nagłówek ---
            self.draw_button("KONIEC ROZGRYWKI", self.font_main, 500, 150, (255, 215, 0), (255, 215, 0))

            # Ogłoszenie zwycięzcy
            winner_text = f"ZWYCIĘZCA: {winner_name.upper()}"
            self.draw_button(winner_text, self.font_main, 500, 300, (0, 255, 0), (0, 255, 0))

            # --- TEKST GRATULACJI ---
            if winner_name in ["Zielony", "Niebieski", "Żółty"]:
                sub_text = "Sztuczna inteligencja przejęła rynek! Spróbuj ponownie."
                text_color = (255, 100, 100)
            else:
                sub_text = "Gratulacje! Zostałeś wielkim monopolistą!"
                text_color = (255, 255, 255)

            self.draw_text(sub_text, self.font_sub, text_color, 500, 400)

            # --- Przyciski Interaktywne ---
            btn_restart, h_restart = self.draw_button("ZAGRAJ PONOWNIE", self.font_sub, 500, 550, (255, 255, 0))
            btn_exit, h_exit = self.draw_button("WYJDŹ Z GRY", self.font_sub, 500, 630, (255, 0, 0))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.click_sound: self.click_sound.play()

                    if h_restart:
                        return "RESTART"
                    elif h_exit:
                        pygame.quit()
                        sys.exit()