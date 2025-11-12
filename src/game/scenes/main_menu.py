import pygame
from ..settings import WHITE
from ..entities.player import Player
from .config_menu import ConfigMenu


class MainMenu:
    def __init__(self, app):
        """app: reference to GameApp instance"""
        self.app = app
        self.screen = app.screen
        self.font_title = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 32)
        self.title_text = 'KNIGHT DEMO GAME'

        # Menu options
        self.options = ['START GAME', 'CONFIGURAÇÃO']
        self.selected = 0

        # Simple menu player shown at bottom doing an idle loop
        sw, sh = self.screen.get_size()
        px = sw // 2 - 152
        py = sh - 220
        self.menu_player = Player(px, py)
        # Force idle start
        self.menu_player._set_state('idle')
        self._auto_dir = -1
        self._dir_change_time = pygame.time.get_ticks() + 1200
        self._next_jump_time = pygame.time.get_ticks() + 2000

        # Play menu music with crossfade if available
        try:
            self.app.audio.crossfade_music('menu', fade_ms=800)
        except Exception:
            pass

        self.config_overlay = None

    def _start_game(self):
        try:
            self.app.audio.play_sound('select')
        except Exception:
            pass
        import importlib
        mod = importlib.import_module('game.scenes.gameplay')
        Gameplay = getattr(mod, 'Gameplay')
        self.app.change_scene(Gameplay)

    def handle_event(self, event):
        if self.config_overlay:
            self.config_overlay.handle_event(event)
            return
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.options[self.selected] == 'START GAME':
                    self._start_game()
                else:
                    # open configuration overlay
                    self.config_overlay = ConfigMenu(self.app, on_done=self._close_config)
            elif event.key == pygame.K_ESCAPE:
                self.app.running = False

    def _close_config(self):
        self.config_overlay = None

    def update(self):
        # update auto-walk for menu player
        now = pygame.time.get_ticks()
        if now >= self._dir_change_time:
            self._auto_dir *= -1
            self._dir_change_time = now + 1200 + (now % 400)

        # set velocity according to auto dir
        self.menu_player.vel_x = self._auto_dir * (self.menu_player.speed * 0.5)
        # random-ish jump schedule
        if now >= self._next_jump_time and self.menu_player.on_ground:
            self.menu_player.vel_y = self.menu_player.jump_power
            self.menu_player.on_ground = False
            self._next_jump_time = now + 1800 + (now % 1200)

        # update animations / physics with screen bounds
        sw, sh = self.screen.get_size()
        ground_y = sh - 40
        self.menu_player.update(sw, sh, ground_y)

        if self.config_overlay:
            self.config_overlay.update()

    def render(self, screen):
        screen.fill((20, 20, 40))
        sw, sh = screen.get_size()

        # Title
        title = self.font_title.render(self.title_text, True, WHITE)
        screen.blit(title, (sw // 2 - title.get_width() // 2, 60))

        # Menu options
        y = 220
        for i, opt in enumerate(self.options):
            color = WHITE if i != self.selected else (255, 220, 100)
            txt = self.font.render(opt, True, color)
            screen.blit(txt, (sw // 2 - txt.get_width() // 2, y))
            y += 56

        # Draw small instructions
        instr = self.font.render('Use ↑/↓ para navegar • Enter selecionar', True, WHITE)
        screen.blit(instr, (sw // 2 - instr.get_width() // 2, y + 10))

        # Draw the menu player near bottom center
        player_pos = (sw // 2 - self.menu_player.width // 2, sh - 220)
        self.menu_player.draw_at(screen, player_pos)

        if self.config_overlay:
            self.config_overlay.render(screen)