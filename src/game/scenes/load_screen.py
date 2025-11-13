import pygame
import time
import math
import random

class LoadScreen:
    def __init__(self, app, target, message='CARREGANDO...', duration_ms=800, prev_surface=None):
        self.app = app
        self.screen = app.screen
        self.target = target
        self.message = message
        self.duration_ms = int(duration_ms)
        self.prev_surface = prev_surface

        self.start = pygame.time.get_ticks()
        self.done = False

        self.min_visible_ms = 300

        self._bands = 48
        self._rand = [1.0 + (random.uniform(-0.35, 0.35)) for _ in range(self._bands)]
        self._max_offset = None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start
        if elapsed >= max(self.duration_ms, self.min_visible_ms):

            try:

                if callable(self.target) and getattr(self.target, '__name__', '').startswith('<lambda'):

                    new_scene = self.target(self.app)
                    self.app.current_scene = new_scene
                else:
                    self.app.change_scene(self.target)
            except Exception:
                try:
                    self.app.change_scene(self.target)
                except Exception:
                    pass
            self.done = True

    def render(self, screen):
        sw, sh = screen.get_size()

        if self.prev_surface is not None:
            try:
                prev = self.prev_surface
                if prev.get_size() != (sw, sh):
                    prev = pygame.transform.smoothscale(prev, (sw, sh))

                if self._max_offset is None:
                    self._max_offset = int(sh * 0.45)

                now = pygame.time.get_ticks()
                elapsed = now - self.start
                t = min(1.0, float(elapsed) / max(1, self.duration_ms))

                band_h = max(1, sh // self._bands)

                for i in range(self._bands):
                    y = i * band_h
                    h = band_h
                    if y + h > sh:
                        h = sh - y
                    if h <= 0:
                        continue

                    band_start = float(i) / max(1, self._bands) * 0.9
                    local_t = max(0.0, (t - band_start) / (1.0 - band_start)) if t > band_start else 0.0

                    ease = 1.0 - pow(1.0 - local_t, 3)

                    offset = int(ease * self._max_offset * self._rand[i])

                    try:
                        src_rect = pygame.Rect(0, y, sw, h)
                        band_surf = prev.subsurface(src_rect).copy()
                        screen.blit(band_surf, (0, y + offset))
                    except Exception:

                        screen.blit(prev, (0, 0))
                        break

                overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
                overlay.fill((8, 8, 12, int(180 * t)))
                screen.blit(overlay, (0, 0))
            except Exception:
                screen.fill((8, 8, 12))
        else:
            screen.fill((8, 8, 12))

        try:
            font = pygame.font.SysFont(None, 40)
        except Exception:
            font = pygame.font.SysFont(None, 28)

        msg = font.render(self.message, True, (255, 255, 255))
        screen.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 2 - 30))

        now = pygame.time.get_ticks()
        elapsed = now - self.start
        t_bar = min(1.0, float(elapsed) / max(1, self.duration_ms))
        bar_w = sw // 3
        bar_h = 18
        bx = sw // 2 - bar_w // 2
        by = sh // 2 + 8
        pygame.draw.rect(screen, (60, 60, 60), (bx, by, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, (180, 160, 60), (bx + 2, by + 2, int((bar_w - 4) * t_bar), bar_h - 4), border_radius=6)