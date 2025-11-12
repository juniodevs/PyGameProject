import pygame
from ..settings import WHITE


class ConfigMenu:
    """Simple configuration overlay to adjust music and SFX volumes.

    Usage: create with ConfigMenu(app, on_done_callback)
    on_done_callback should be callable(returned_to_parent) and will be called when user exits.
    """

    def __init__(self, app, on_done=None):
        self.app = app
        self.screen = app.screen
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 48)
        self.on_done = on_done

        # options: list of tuples (label, getter, setter)
        self.options = [
            ("Música", lambda: int(self.app.audio.music_volume * 100), self._set_music),
            ("SFX", lambda: int(self.app.audio.sfx_volume * 100), self._set_sfx),
        ]
        self.index = 0

    def _set_music(self, pct):
        v = max(0, min(100, pct)) / 100.0
        try:
            self.app.audio.set_music_volume(v)
        except Exception:
            pass

    def _set_sfx(self, pct):
        v = max(0, min(100, pct)) / 100.0
        try:
            self.app.audio.set_sfx_volume(v)
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._done()
            elif event.key in (pygame.K_UP,):
                self.index = (self.index - 1) % len(self.options)
            elif event.key in (pygame.K_DOWN,):
                self.index = (self.index + 1) % len(self.options)
            elif event.key in (pygame.K_LEFT,):
                label, getter, setter = self.options[self.index]
                setter(getter() - 5)
                self._maybe_save()
            elif event.key in (pygame.K_RIGHT,):
                label, getter, setter = self.options[self.index]
                setter(getter() + 5)
                self._maybe_save()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                # pressing enter exits config (apply changes)
                self._done()

    def _maybe_save(self):
        # try to persist current values
        try:
            from ..utils.config import save_config
            cfg = {
                'music_volume': self.app.audio.music_volume,
                'sfx_volume': self.app.audio.sfx_volume,
                'master_volume': getattr(self.app.audio, 'master_volume', 1.0)
            }
            save_config(cfg)
        except Exception:
            pass

    def _done(self):
        # persist when done
        self._maybe_save()
        if callable(self.on_done):
            try:
                self.on_done()
            except Exception:
                pass

    def update(self):
        pass

    def render(self, screen):
        w, h = screen.get_size()
        # semi-transparent overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render('CONFIGURAÇÃO', True, WHITE)
        screen.blit(title, (w // 2 - title.get_width() // 2, 80))

        y = 190
        for i, (label, getter, setter) in enumerate(self.options):
            val = getter()
            text = self.font.render(f'{label}: {val}%', True, WHITE if i != self.index else (255, 220, 100))
            screen.blit(text, (w // 2 - text.get_width() // 2, y))
            y += 48

        hint = self.font.render('←/→ ajustar • ↑/↓ navegar • Enter salvar • Esc sair', True, WHITE)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 110))
