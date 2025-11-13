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

                self._done()

    def _maybe_save(self):

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

        hint_y = h - 110

        center_x = w // 2

        txt_ajustar = self.font.render(' ajustar • ', True, WHITE)
        txt_navegar = self.font.render(' navegar • ', True, WHITE)
        txt_rest = self.font.render(' Enter salvar • Esc sair', True, WHITE)

        icon_w = 20
        gap = 6
        total_w = icon_w + 4 + icon_w + txt_ajustar.get_width() + icon_w + 4 + icon_w + txt_navegar.get_width() + txt_rest.get_width()

        x = center_x - total_w // 2

        self._draw_arrow_icon(screen, x, hint_y, 'left', WHITE)
        x += icon_w + 4

        self._draw_arrow_icon(screen, x, hint_y, 'right', WHITE)
        x += icon_w + gap

        screen.blit(txt_ajustar, (x, hint_y))
        x += txt_ajustar.get_width()

        self._draw_arrow_icon(screen, x, hint_y, 'up', WHITE)
        x += icon_w + 4
        self._draw_arrow_icon(screen, x, hint_y, 'down', WHITE)
        x += icon_w + gap

        screen.blit(txt_navegar, (x, hint_y))
        x += txt_navegar.get_width()
        screen.blit(txt_rest, (x, hint_y))

    def _draw_arrow_icon(self, screen, x, y, direction, color=(240, 220, 160)):
        """Draw a small triangular arrow icon at (x,y). direction in ('left','right','up','down').

        x,y are the top-left of an area approx 20x20 where the icon will be drawn.
        """
        w = 20
        h = 20
        center_y = y + h // 2
        if direction in ('left', 'l'):
            pts = [(x + w - 2, center_y - 6), (x + 2, center_y), (x + w - 2, center_y + 6)]
        elif direction in ('right', 'r'):
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y), (x + 2, center_y + 6)]
        elif direction in ('up', 'u'):
            pts = [(x + w // 2, center_y - 6), (x + 2, center_y + 6), (x + w - 2, center_y + 6)]
        else:
            pts = [(x + 2, center_y - 6), (x + w - 2, center_y - 6), (x + w // 2, center_y + 6)]
        try:
            pygame.draw.polygon(screen, color, pts)
        except Exception:
            pass