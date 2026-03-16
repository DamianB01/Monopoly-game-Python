"""
Moduł wizualizacji planszy gry.
Definiuje klasę Board, odpowiedzialną za graficzną reprezentację planszy,
rozmieszczenie pól, rysowanie pionków graczy oraz obsługę animacji
kart szansy.
"""

import pygame
import os
import math
from field import Field, Property, TaxField, ChanceField, JailField, UtilityField, StationField, ParkingField, CommunityChestField


class Board:
    def __init__(self):
        self.size = 660
        self.corner_size = 90
        self.offset_x = 50
        self.offset_y = 70
        self.animating_card = False
        self.current_side = "LEFT"
        self.card_angle = 0
        self.current_card = None

        pygame.mixer.init()
        try:
            self.click_sound = pygame.mixer.Sound(os.path.join("sounds", "click.mp3"))
        except:
            self.click_sound = None

        try:
            self.logo_img = self._load_img("logo.png", (350, 180), rotate=45)
            self.card_img = self._load_img("chance1.png", (75, 120))
        except:
            self.logo_img = None
            self.card_img = None

        # 2 pierwsze grafiki załadowałem powyżej, ale później uznałem, że lepiej je wrzucać do słownika, dlatego tak to wygląda
        self.special_icons = {
            "PARKING": self._load_img("parking.png", (300, 300)),
            "JAIL": self._load_img("jail.png", (300, 300)),
            "GO_TO_JAIL": self._load_img("gotojail.png", (300, 300)),
            "TAX": self._load_img("income.png", (120, 160)),
            "LUXURY": self._load_img("luxury.png", (120, 160)),
            "WATER": self._load_img("water.png", (120, 160)),
            "POWER": self._load_img("elec.png", (160, 120)),
            "START": self._load_img("go.png", (300, 300)),
            "CHEST1": self._load_img("commChest1.png",(120,160)),
            "CHEST2": self._load_img("commChest2.png", (120, 160)),
            "CHEST3": self._load_img("commChest3.png", (120, 160)),
            "CHANCE2": self._load_img("chance3.png", (120, 160))
        }

        self.fields = self._setup_fields()
        self.house_icons = self._setup_house_icons()

        self.font = pygame.font.SysFont("Arial", 8, bold=True)
        self.hud_font_bold = pygame.font.SysFont("Arial", 20, bold=True)
        self.hud_font_small = pygame.font.SysFont("Arial", 16)

    def _load_img(self, name, size, rotate=0):
        path = os.path.join("images", name)
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            if rotate: img = pygame.transform.rotate(img, rotate)
            return img
        except:
            return None

    def _setup_house_icons(self):
        icons = {}
        house_files = {
            (255, 50, 50): "house_red.png",
            (50, 50, 255): "house_blue.png",
            (50, 255, 50): "house_green.png",
            (255, 255, 50): "house_yellow.png"
        }
        for color, filename in house_files.items():
            path = os.path.join("images", filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                icons[color] = pygame.transform.scale(img, (15, 15))
            except:
                icons[color] = None
        return icons

    def play_click(self):
        if self.click_sound: self.click_sound.play()

    def draw_center_decorations(self, screen):
        cx, cy = self.offset_x + self.size // 2, self.offset_y + self.size // 2
        if self.logo_img:
            screen.blit(self.logo_img, self.logo_img.get_rect(center=(cx, cy)))
            if self.card_img:
                c_rot = pygame.transform.rotate(self.card_img, 45)

                if not (self.animating_card and self.current_side == "RIGHT"):
                    screen.blit(c_rot, (cx + 95, cy + 55))

                if not (self.animating_card and self.current_side == "LEFT"):
                    screen.blit(c_rot, (cx - 175, cy - 175))

            # ANIMACJA
            if self.animating_card and self.current_card:
                if self.card_angle < 180:
                    self.card_angle += 10

                progress = min(1.0, self.card_angle / 180.0)

                if self.current_side == "RIGHT":
                    start_pos = (cx + 130, cy + 90)
                    start_angle = 45
                else:
                    start_pos = (cx - 130, cy - 130)
                    start_angle = 45

                curr_x = start_pos[0] + (cx - start_pos[0]) * progress
                curr_y = start_pos[1] + (cy - start_pos[1]) * progress

                scale_x = abs(math.cos(math.radians(self.card_angle)))

                lift = 1.0 + (0.5 * math.sin(math.radians(self.card_angle / 2)))

                curr_w = max(1, int(140 * scale_x * lift))
                curr_h = int(200 * lift)

                if self.card_angle < 90:
                    angle_offset = start_angle * (1 - progress)
                    temp_surf = pygame.transform.rotate(self.card_img, angle_offset)
                    card_surf = pygame.transform.scale(temp_surf, (curr_w, curr_h))
                else:
                    base_w, base_h = 200, 300
                    canvas = pygame.Surface((base_w, base_h))
                    canvas.fill((255, 255, 255))
                    pygame.draw.rect(canvas, (0, 0, 0), canvas.get_rect(), 3)

                    owner_name = getattr(self, 'current_player_name', "Gracz")
                    header_txt = self.hud_font_bold.render(owner_name.upper(), True,(0, 0, 0))
                    canvas.blit(header_txt, header_txt.get_rect(centerx=base_w // 2, y=15))

                    pygame.draw.line(canvas, (100, 100, 100), (20, 45), (base_w - 20, 45), 1)

                    display_text = self.current_card.text

                    wrapped_lines = self._wrap_text(display_text, self.hud_font_small, base_w - 20)

                    for idx, line in enumerate(wrapped_lines):
                        txt_surf = self.hud_font_small.render(line, True, (0, 0, 0))
                        txt_rect = txt_surf.get_rect(centerx=base_w // 2, y=65 + idx * 25)
                        canvas.blit(txt_surf, txt_rect)

                    card_surf = pygame.transform.scale(canvas, (max(1, int(curr_w)), max(1, int(curr_h))))

                card_rect = card_surf.get_rect(center=(curr_x, curr_y))

                shadow_off = 10 * progress
                shadow_rect = card_rect.copy()
                shadow_rect.move_ip(shadow_off, shadow_off)
                pygame.draw.rect(screen, (30, 30, 30), shadow_rect, border_radius=5)

                screen.blit(card_surf, card_rect)

    def draw_field_info(self, screen, field, hud_x, message=""):
        info_y = 430
        pygame.draw.rect(screen, (40, 40, 40), (hud_x, info_y, 240, 350))
        pygame.draw.line(screen, (100, 100, 100), (hud_x, info_y - 10), (hud_x + 220, info_y - 10), 2)

        if isinstance(field, Property):
            is_monopoly = False
            if field.owner:
                same_color_fields = [f for f in self.fields if isinstance(f, Property) and f.color == field.color]
                is_monopoly = all(f.owner == field.owner for f in same_color_fields)

            header_txt = f"{field.name.upper()} ({field.houses}/4)"
            name_surf = self.hud_font_bold.render(header_txt, True, (255, 255, 255))

            text_w = name_surf.get_width()
            rect_w = text_w + 20

            header_color = field.color if field.owner is None else field.owner.color
            pygame.draw.rect(screen, header_color, (hud_x, info_y, rect_w, 35), border_radius=5)

            screen.blit(name_surf, (hud_x + 10, info_y + 7))

            current_rent = field.get_current_rent(self.fields)
            multipliers = [1, 5, 15, 40, 80]
            lines = [
                f"Właściciel: {field.owner.name if field.owner else 'Brak'}",
                f"Obecny czynsz: {current_rent} zł",
                "-" * 25,
                "PROGNOZA ROZBUDOWY:"
            ]

            if is_monopoly and field.houses == 0:
                lines.append("(!) Bonus kompletu: x2 czynsz")
            elif field.owner is None:
                lines.append("Zbierz komplet: czynsz x2")

            for h in range(4):
                base_cost = field.rent * 10
                h_price = int(base_cost * (1 + (h * 0.5)))
                h_rent = field.rent * multipliers[h + 1]

                status = "✓" if field.houses > h else ("→" if field.houses == h else " ")
                lines.append(f"{status} Dom {h + 1}: {h_price}zł (Czynsz: {h_rent}zł)")

            for idx, line in enumerate(lines):
                color = (255, 255, 255)
                if "→" in line: color = (255, 255, 0)
                if "✓" in line: color = (150, 150, 150)
                if "(!)" in line: color = (0, 255, 0)

                surf = self.hud_font_small.render(line, True, color)
                screen.blit(surf, (hud_x + 5, info_y + 50 + idx * 22))

        if isinstance(field, TaxField):
            header_surf = self.hud_font_bold.render(field.name.upper(), True, (255, 255, 255))
            pygame.draw.rect(screen, (200, 0, 0), (hud_x, info_y, 220, 35),border_radius=5)
            screen.blit(header_surf, (hud_x + 10, info_y + 7))

            txt = self.hud_font_small.render(f"Opłata skarbowa: {field.amount} zł", True, (255, 255, 255))
            screen.blit(txt, (hud_x + 10, info_y + 50))

        if isinstance(field, UtilityField):
            pygame.draw.rect(screen, (150, 150, 150), (hud_x, info_y, 220, 35), border_radius=5)
            name_surf = self.hud_font_bold.render(field.name.upper(), True, (255, 255, 255))
            screen.blit(name_surf, (hud_x + 10, info_y + 7))

            rate = 50 if field.name == "PRĄD" else 100
            desc = f"Kwota: ilość oczek x {rate} zł"
            txt_surf = self.hud_font_small.render(desc, True, (255, 255, 255))
            screen.blit(txt_surf, (hud_x + 10, info_y + 50))

        pygame.draw.line(screen, (100, 100, 100), (hud_x, 690), (hud_x + 220, 690), 1)

        # Wyświetlanie napisu (game_logic.message)
        if message:
            msg_surf = self.hud_font_small.render(message, True, (255, 255, 0))
            msg_rect = msg_surf.get_rect(center=(self.offset_x + 300, self.offset_y - 25))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(screen, (20, 20, 20), bg_rect, border_radius=5)
            screen.blit(msg_surf, msg_rect)

    def draw(self, screen):
        # Tło planszy
        pygame.draw.rect(screen, (200, 230, 201), (self.offset_x, self.offset_y, self.size, self.size))

        for i in range(40):
            fx, fy, fw, fh = self.get_field_rect(i)
            rect = pygame.Rect(fx + self.offset_x, fy + self.offset_y, fw, fh)
            field = self.fields[i]

            pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)

            # --- LOGIKA GRAFIK ---
            icon_to_draw = None
            is_special = False
            if i == 0:
                icon_to_draw = self.special_icons.get("START")
                is_special = True
            elif isinstance(field, ParkingField):
                icon_to_draw = self.special_icons["PARKING"]
                is_special = True
            elif isinstance(field, JailField):
                icon_to_draw = self.special_icons["GO_TO_JAIL"] if i == 30 else self.special_icons["JAIL"]
                is_special = True
            elif isinstance(field, TaxField):
                icon_to_draw = self.special_icons["TAX"] if field.index == 4 else self.special_icons["LUXURY"]
                is_special = True
            elif isinstance(field, UtilityField):
                icon_to_draw = self.special_icons["WATER"] if "WODOCIĄGI" in field.name.upper() else self.special_icons["POWER"]
                is_special = True
            elif isinstance(field, CommunityChestField):
                icon_to_draw = self.special_icons["CHEST1"] if field.index == 2 else self.special_icons["CHEST2"] if field.index == 33 else self.special_icons["CHEST3"]
                is_special = True
            elif isinstance(field, ChanceField):
                icon_to_draw = self.special_icons["CHANCE2"] if field.index == 36 else self.card_img
                is_special = True
            if icon_to_draw:
                # Automatyczne skalowanie ikony do rozmiaru konkretnego pola, na którym stoi
                scaled_icon = pygame.transform.scale(icon_to_draw, (fw - 2, fh - 2))
                icon_rect = scaled_icon.get_rect(center=rect.center)
                screen.blit(scaled_icon, icon_rect)

            if isinstance(field, Property):
                self._draw_color_bar(screen, rect, i, field.color)

            # RYSOWANIE IKONY WŁAŚCICIELA
            if hasattr(field, 'owner') and field.owner:
                icon = self.house_icons.get(field.owner.color)
                if icon:
                    small_icon = pygame.transform.scale(icon, (20, 20))

                    if 0 <= i <= 10:  # DÓŁ
                        ix = rect.centerx - 10
                        iy = rect.bottom - 22
                    elif 10 < i <= 20:  # LEWO
                        ix = rect.left + 2
                        iy = rect.centery - 10
                    elif 20 < i <= 30:  # GÓRA
                        ix = rect.centerx - 10
                        iy = rect.top + 2
                    else:  # PRAWO
                        ix = rect.right - 22
                        iy = rect.centery - 10

                    screen.blit(small_icon, (ix, iy))

            if not is_special:
                self._draw_centered_text(screen, rect, field.name, i)

    def _draw_color_bar(self, screen, rect, i, color):
        b = 15
        if 0 < i < 10:
            rb = (rect.x, rect.y, rect.width, b)
        elif 10 < i < 20:
            rb = (rect.right - b, rect.y, b, rect.height)
        elif 20 < i < 30:
            rb = (rect.x, rect.bottom - b, rect.width, b)
        else:
            rb = (rect.x, rect.y, b, rect.height)
        pygame.draw.rect(screen, color, rb)

    def get_field_rect(self, i):
        exact_tile_w = (self.size - 2 * self.corner_size) / 9.0
        if 0 <= i <= 10:
            y = self.size - self.corner_size
            if i == 0: return (self.size - self.corner_size, y, self.corner_size, self.corner_size)
            if i == 10: return (0, y, self.corner_size, self.corner_size)
            x = self.size - self.corner_size - int(i * exact_tile_w)
            w = int((i) * exact_tile_w) - int((i - 1) * exact_tile_w)
            return (x, y, w, self.corner_size)
        elif 11 <= i <= 20:
            x = 0
            if i == 20: return (x, 0, self.corner_size, self.corner_size)
            y = self.size - self.corner_size - int((i - 10) * exact_tile_w)
            h = int((i - 10) * exact_tile_w) - int((i - 11) * exact_tile_w)
            return (x, y, self.corner_size, h)
        elif 21 <= i <= 30:
            y = 0
            if i == 30: return (self.size - self.corner_size, y, self.corner_size, self.corner_size)
            x = self.corner_size + int((i - 21) * exact_tile_w)
            w = int((i - 20) * exact_tile_w) - int((i - 21) * exact_tile_w)
            return (x, y, w, self.corner_size)
        else:
            x = self.size - self.corner_size
            y = self.corner_size + int((i - 31) * exact_tile_w)
            h = int((i - 30) * exact_tile_w) - int((i - 31) * exact_tile_w)
            return (x, y, self.corner_size, h)

    def _draw_centered_text(self, screen, rect, name, i):
        words = name.split()
        for idx, word in enumerate(words):
            surf = self.font.render(word, True, (0, 0, 0))
            screen.blit(surf, surf.get_rect(center=(rect.centerx, rect.centery + idx * 10)))

    def _setup_fields(self):
        f = [None] * 40
        f[0] = Field("START", 0, "START")
        f[1] = Property("Ateny", 1, 60, 2, (150, 75, 0))
        f[2] = CommunityChestField("KASA SPOŁ.", 2)
        f[3] = Property("Saloniki", 3, 60, 4, (150, 75, 0))
        f[4] = TaxField("PODATEK", 4, 200)
        f[5] = StationField("DWORZEC", 5)
        f[6] = Property("Neapol", 6, 100, 6, (135, 206, 250))
        f[7] = ChanceField("SZANSA", 7, "CHANCE")
        f[8] = Property("Mediolan", 8, 100, 6, (135, 206, 250))
        f[9] = Property("Rzym", 9, 120, 8, (135, 206, 250))
        f[10] = JailField("WIĘZIENIE", 10)
        f[11] = Property("Barcelona", 11, 140, 10, (255, 0, 255))
        f[12] = UtilityField("PRĄD", 12, 50)
        f[13] = Property("Sewilla", 13, 140, 10, (255, 0, 255))
        f[14] = Property("Madryt", 14, 160, 12, (255, 0, 255))
        f[15] = StationField("DWORZEC", 15)
        f[16] = Property("Bordeaux", 16, 180, 14, (255, 165, 0))
        f[17] = CommunityChestField("KASA SPOŁ.", 17)
        f[18] = Property("Lyon", 18, 180, 14, (255, 165, 0))
        f[19] = Property("Paryż", 19, 200, 16, (255, 165, 0))
        f[20] = ParkingField("PARKING", 20)
        f[21] = Property("Innsbruck", 21, 220, 18, (255, 0, 0))
        f[22] = ChanceField("SZANSA", 22, "CHANCE")
        f[23] = Property("Wiedeń", 23, 220, 18, (255, 0, 0))
        f[24] = Property("Graz", 24, 240, 20, (255, 0, 0))
        f[25] = StationField("DWORZEC", 25)
        f[26] = Property("Zurych", 26, 260, 22, (255, 255, 0))
        f[27] = Property("Bern", 27, 260, 22, (255, 255, 0))
        f[28] = UtilityField("WODOCIĄGI", 28, 100)
        f[29] = Property("Genewa", 29, 280, 24, (255, 255, 0))
        f[30] = JailField("IDŹ DO WIĘZIENIA", 30)
        f[31] = Property("Frankfurt", 31, 300, 26, (0, 128, 0))
        f[32] = Property("Monachium", 32, 300, 26, (0, 128, 0))
        f[33] = CommunityChestField("KASA SPOŁ.", 33)
        f[34] = Property("Berlin", 34, 320, 28, (0, 128, 0))
        f[35] = StationField("DWORZEC", 35)
        f[36] = ChanceField("SZANSA", 36, "CHANCE")
        f[37] = Property("Londyn", 37, 350, 35, (0, 0, 139))
        f[38] = TaxField("PODATEK", 38, 400)
        f[39] = Property("Liverpool", 39, 400, 50, (0, 0, 139))
        return f

    def reset_fields(self):
        """Czyści właścicieli i budynki ze wszystkich pól na planszy."""
        for field in self.fields:
            if hasattr(field, 'owner'):
                field.owner = None
            if hasattr(field, 'houses'):
                field.houses = 0

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines