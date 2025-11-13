import os
import pygame
from ..settings import WHITE
from ..entities.player import Player
from .config_menu import ConfigMenu

class MainMenu:
    def __init__(self, app):
        """app: reference to GameApp instance"""
        self.app = app
        self.screen = app.screen

        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            fonts_dir = os.path.join(base, 'assets', 'fonts')

            title_path = os.path.join(fonts_dir, 'The Knight.ttf')
            if os.path.isfile(title_path):
                self.font_title = pygame.font.Font(title_path, 72)
                self.font = pygame.font.Font(title_path, 32)
            else:
                self.font_title = pygame.font.SysFont(None, 72)
                self.font = pygame.font.SysFont(None, 32)
        except Exception:
            self.font_title = pygame.font.SysFont(None, 72)
            self.font = pygame.font.SysFont(None, 32)

        try:
            self.font_controls = pygame.font.SysFont(None, 22)
        except Exception:
            self.font_controls = self.font
        self.title_text = 'KNIGHT DEMO GAME'

        self.options = ['INICIAR GAME', 'CONFIGURAÇÃO', 'SAIR']
        self.selected = 0

        sw, sh = self.screen.get_size()
        px = sw // 2 - 152
        py = sh - 220
        self.menu_player = Player(px, py)

        self.menu_player._set_state('idle')
        self._auto_dir = -1
        self._dir_change_time = pygame.time.get_ticks() + 1200
        self._next_jump_time = pygame.time.get_ticks() + 2000

        try:
            self.app.audio.stop_battle_music()
        except Exception:
            pass
        try:
            self.app.audio.play_menu_music('menumusic', ramp_ms=5000, fade_ms=200)
        except Exception:
            pass

        self.config_overlay = None
        # confirmation dialog state for exiting
        self.confirm_exit = False
        # 0 -> NÃO (default), 1 -> SIM
        self.confirm_choice = 0
        # fade/animation for confirmation dialog
        self._confirm_alpha = 0
        self._confirm_fade_ms = 220
        self._confirm_fade_start = None
        self._confirm_closing = False

        self.controls = [
            ("Mover Esquerda", "← / A"),
            ("Mover Direita", "→ / D"),
            ("Pular", "Space"),
            ("Atacar", "Ctrl"),
            ("Castar Bola de Fogo", "SHIFT"),
            ("Pausar", "Esc"),
        ]

    def _start_game(self):
        try:
            self.app.audio.play_sound('select')
        except Exception:
            pass

        try:
            import importlib
            mod = importlib.import_module('game.scenes.gameplay')
            Gameplay = getattr(mod, 'Gameplay')

            try:
                from .load_screen import LoadScreen
                prev = None
                try:
                    prev = self.screen.copy()
                except Exception:
                    prev = None
                self.app.change_scene(lambda app, p=prev: LoadScreen(app, target=Gameplay, message='CARREGANDO JOGO...', duration_ms=700, prev_surface=p))
                return
            except Exception:
                self.app.change_scene(Gameplay)
                return
        except Exception:
            try:
                self.app.change_scene('game.scenes.gameplay')
            except Exception:
                pass

    def handle_event(self, event):
        if self.config_overlay:
            self.config_overlay.handle_event(event)
            return
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            # If confirm dialog is open, only handle dialog keys (block up/down menu navigation)
            if self.confirm_exit:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.confirm_choice = max(0, self.confirm_choice - 1)
                    try:
                        self.app.audio.play_sound('select')
                    except Exception:
                        pass
                    return
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.confirm_choice = min(1, self.confirm_choice + 1)
                    try:
                        self.app.audio.play_sound('select')
                    except Exception:
                        pass
                    return
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.confirm_choice == 1:
                        try:
                            self.app.audio.play_sound('select')
                        except Exception:
                            pass
                        self.app.running = False
                        return
                    else:
                        try:
                            self.app.audio.play_sound('select')
                        except Exception:
                            pass
                        # start fade-out/close
                        self._confirm_closing = True
                        self._confirm_fade_start = pygame.time.get_ticks()
                        return
                elif event.key == pygame.K_ESCAPE:
                    # start fade-out/close
                    self._confirm_closing = True
                    self._confirm_fade_start = pygame.time.get_ticks()
                    try:
                        self.app.audio.play_sound('select')
                    except Exception:
                        pass
                    return
                # swallow any other keys while confirm dialog is open
                return

            # normal menu navigation (only active when confirm dialog is not open)
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                choice = self.options[self.selected]
                if choice == 'INICIAR GAME':
                    self._start_game()
                elif choice == 'CONFIGURAÇÃO':
                    self.config_overlay = ConfigMenu(self.app, on_done=self._close_config)
                elif choice == 'SAIR':
                    try:
                        self.app.audio.play_sound('select')
                    except Exception:
                        pass
                    # open confirmation dialog (start fade-in)
                    self.confirm_exit = True
                    self._confirm_closing = False
                    self._confirm_fade_start = pygame.time.get_ticks()
                    self._confirm_alpha = 0
                    self.confirm_choice = 0
            elif event.key == pygame.K_ESCAPE:
                # open confirmation dialog instead of immediate exit
                try:
                    self.app.audio.play_sound('select')
                except Exception:
                    pass
                self.confirm_exit = True
                self._confirm_closing = False
                self._confirm_fade_start = pygame.time.get_ticks()
                self._confirm_alpha = 0
                self.confirm_choice = 0

    def _close_config(self):
        self.config_overlay = None

    def update(self):
        now = pygame.time.get_ticks()
        # update confirmation dialog fade
        if self.confirm_exit or self._confirm_closing:
            if self._confirm_fade_start is None:
                self._confirm_fade_start = now
            elapsed_f = now - self._confirm_fade_start
            t = min(1.0, float(elapsed_f) / max(1, self._confirm_fade_ms))
            if not self._confirm_closing:
                self._confirm_alpha = int(255 * t)
            else:
                self._confirm_alpha = int(255 * (1.0 - t))
                if t >= 1.0:
                    # finish closing
                    self.confirm_exit = False
                    self._confirm_closing = False
                    self._confirm_fade_start = None

        if now >= self._dir_change_time:
            self._auto_dir *= -1
            self._dir_change_time = now + 1200 + (now % 400)

        self.menu_player.vel_x = self._auto_dir * (self.menu_player.speed * 0.5)

        if now >= self._next_jump_time and self.menu_player.on_ground:
            self.menu_player.vel_y = self.menu_player.jump_power
            self.menu_player.on_ground = False
            self._next_jump_time = now + 1800 + (now % 1200)

        sw, sh = self.screen.get_size()
        ground_y = sh - 40
        self.menu_player.update(sw, sh, ground_y)

        if self.config_overlay:
            self.config_overlay.update()

    def render(self, screen):
        screen.fill((20, 20, 40))
        sw, sh = screen.get_size()

        title = self.font_title.render(self.title_text, True, WHITE)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 60))

        menu_x = 80
        menu_w = 360
        y = 180
        for i, opt in enumerate(self.options):
            box_w = menu_w
            box_h = 56
            box_x = menu_x
            box_y = y

            if i == self.selected:
                pygame.draw.rect(screen, (60, 50, 30), (box_x - 8, box_y - 6, box_w + 16, box_h + 12), border_radius=8)
                color = (255, 220, 100)
            else:
                color = WHITE

            txt = self.font.render(opt, True, color)
            screen.blit(txt, (box_x + 24, y + 10))

            if i == self.selected:
                arrow = self.font.render('►', True, (255, 200, 120))
                screen.blit(arrow, (box_x + 8, y + 12))

            y += box_h + 12

        instr_text_prefix = 'Use '
        instr_text_suffix = ' para navegar • Enter selecionar'
        prefix_surf = self.font_controls.render(instr_text_prefix, True, WHITE)
        suffix_surf = self.font_controls.render(instr_text_suffix, True, WHITE)

        arrow_w = 18
        gap = 6
        total_w = prefix_surf.get_width() + arrow_w + gap + arrow_w + suffix_surf.get_width()
        instr_x = menu_x + (menu_w // 2) - (total_w // 2)
        instr_y = y + 12
        screen.blit(prefix_surf, (instr_x, instr_y))
        x = instr_x + prefix_surf.get_width()

        self._draw_arrow_icon(screen, x, instr_y + 2, 'up', (240, 220, 160))
        x += arrow_w + gap

        self._draw_arrow_icon(screen, x, instr_y + 2, 'down', (240, 220, 160))
        x += arrow_w + gap
        screen.blit(suffix_surf, (x, instr_y))

        panel_w = 300
        panel_h = 260
        panel_x = menu_x + menu_w + 32
        panel_y = 160

        pygame.draw.rect(screen, (30, 30, 40), (panel_x, panel_y, panel_w, panel_h), border_radius=6)

        hdr = self.font.render('CONTROLES', True, (220, 220, 200))
        screen.blit(hdr, (panel_x + panel_w // 2 - hdr.get_width() // 2, panel_y + 12))

        row_y = panel_y + 52
        for label, key in self.controls:
            lbl = self.font_controls.render(label, True, (200, 200, 200))
            screen.blit(lbl, (panel_x + 18, row_y))

            parts = [p.strip() for p in key.split('/')]

            items = []
            gap = 8
            total_w = 0
            for p in parts:

                if any(ch in p for ch in ('←', '→', '↑', '↓')):
                    w = 20
                    items.append((p, None, w))
                else:
                    surf = self.font_controls.render(p, True, (240, 220, 160))
                    w = surf.get_width()
                    items.append((p, surf, w))
                total_w += w + gap
            if total_w > 0:
                total_w -= gap

            x = panel_x + panel_w - total_w - 16
            for p, surf, w in items:
                if surf is None:

                    center_y = row_y + self.font_controls.get_height() // 2
                    if '←' in p:
                        pts = [(x + w - 2, center_y - 6), (x + 2, center_y), (x + w - 2, center_y + 6)]
                    elif '→' in p:
                        pts = [(x + 2, center_y - 6), (x + w - 2, center_y), (x + 2, center_y + 6)]
                    elif '↑' in p:
                        pts = [(x + w // 2, center_y - 6), (x + 2, center_y + 6), (x + w - 2, center_y + 6)]
                    else:  
                        pts = [(x + 2, center_y - 6), (x + w - 2, center_y - 6), (x + w // 2, center_y + 6)]
                    pygame.draw.polygon(screen, (240, 220, 160), pts)
                else:
                    screen.blit(surf, (x, row_y))
                x += w + gap

            row_y += 34

        player_pos = (sw // 2 - self.menu_player.width // 2, sh - 220)
        self.menu_player.draw_at(screen, player_pos)

        if self.config_overlay:
            self.config_overlay.render(screen)

        # confirmation dialog for exiting (with fade)
        if self._confirm_alpha > 0:
            box_w = 420
            box_h = 140
            bx = sw // 2 - box_w // 2
            by = sh // 2 - box_h // 2

            # dim the background with a semi-transparent overlay
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((8, 8, 12, int(150 * (self._confirm_alpha / 255.0))))
            screen.blit(overlay, (0, 0))

            # dialog surface with alpha
            dialog = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            dialog.fill((18, 18, 22, self._confirm_alpha))
            # border
            pygame.draw.rect(dialog, (120, 110, 80, self._confirm_alpha), (2, 2, box_w - 4, box_h - 4), width=2, border_radius=6)
            screen.blit(dialog, (bx, by))

            # message
            msg = self.font.render('Deseja sair do jogo?', True, (240, 240, 240))
            msg.set_alpha(self._confirm_alpha)
            screen.blit(msg, (sw // 2 - msg.get_width() // 2, by + 18))

            # options
            col_no = (220, 220, 220) if self.confirm_choice == 0 else (150, 150, 150)
            col_yes = (220, 220, 220) if self.confirm_choice == 1 else (150, 150, 150)
            opt_no = self.font.render('NÃO', True, col_no)
            opt_yes = self.font.render('SIM', True, col_yes)
            opt_no.set_alpha(self._confirm_alpha)
            opt_yes.set_alpha(self._confirm_alpha)

            opts_y = by + 70
            gap = 80
            total_w = opt_no.get_width() + gap + opt_yes.get_width()
            ox = sw // 2 - total_w // 2

            screen.blit(opt_no, (ox, opts_y))
            screen.blit(opt_yes, (ox + opt_no.get_width() + gap, opts_y))

            # highlight selected (draw on main surface so alpha applies to stroke too)
            sel_x = ox if self.confirm_choice == 0 else (ox + opt_no.get_width() + gap)
            sel_w = opt_no.get_width() if self.confirm_choice == 0 else opt_yes.get_width()
            hl_surf = pygame.Surface((sel_w + 16, opt_no.get_height() + 12), pygame.SRCALPHA)
            pygame.draw.rect(hl_surf, (255, 200, 120, self._confirm_alpha), (0, 0, sel_w + 16, opt_no.get_height() + 12), width=2, border_radius=6)
            screen.blit(hl_surf, (sel_x - 8, opts_y - 6))

    def _draw_arrow_icon(self, screen, x, y, direction, color=(240, 220, 160)):
        w = 18
        h = 18
        center_y = y + h // 2
        if direction in ('left', 'l'):
            pts = [(x + w - 2, center_y - 6), (x + 2, center_y), (x + w - 2, center_y + 6)]
        elif direction in ('right', 'r'):
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y), (x + 2, center_y + 6)]
        elif direction in ('up', 'u'):
            pts = [(x + w // 2, center_y - 6), (x + 2, center_y + 6), (x + w - 2, center_y + 6)]
        else:
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y - 6), (x + w // 2, center_y + 6)]
        pygame.draw.polygon(screen, color, pts)