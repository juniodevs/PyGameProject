import pygame
import time
import math
import random


class LoadScreen:
    """Transition scene that first melts the previous screen (exit) and then
    assembles the next scene (entry) by animating horizontal bands into place.

    Usage: LoadScreen(app, target, prev_surface=prev, duration_ms=800, entry_duration_ms=600)
    """

    def __init__(self, app, target, message='CARREGANDO...', duration_ms=800, prev_surface=None, entry_duration_ms=600):
        self.app = app
        self.screen = app.screen
        self.target = target
        self.message = message
        self.duration_ms = int(duration_ms)
        self.entry_duration_ms = int(entry_duration_ms)
        self.prev_surface = prev_surface

        self.start = pygame.time.get_ticks()
        self.entry_start = None
        self.done = False

        self.min_visible_ms = 300

        self._bands = 48
        self._rand = [1.0 + random.uniform(-0.35, 0.35) for _ in range(self._bands)]
        self._max_offset = None

        # phases: 'exit' (melt prev_surface) -> 'entry' (assemble target)
        self.phase = 'exit'
        self._entry_surface = None
        self._target_scene = None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.phase == 'exit':
            elapsed = now - self.start
            if elapsed >= max(self.duration_ms, self.min_visible_ms):
                # prepare entry: instantiate target scene and render it offscreen
                sw, sh = self.screen.get_size()
                try:
                    if callable(self.target):
                        new_scene = self.target(self.app)
                    else:
                        # if target is not callable, just hand over control
                        self.app.change_scene(self.target)
                        self.done = True
                        return

                    surf = pygame.Surface((sw, sh))
                    try:
                        # ask the scene to render itself into the offscreen surface
                        new_scene.render(surf)
                    except Exception:
                        # rendering may fail if scene expects updates; ignore
                        pass

                    self._entry_surface = surf
                    self._target_scene = new_scene
                    self.phase = 'entry'
                    self.entry_start = pygame.time.get_ticks()
                except Exception:
                    try:
                        self.app.change_scene(self.target)
                    except Exception:
                        pass
                    self.done = True

        elif self.phase == 'entry':
            if self.entry_start is None:
                self.entry_start = pygame.time.get_ticks()
            if now - self.entry_start >= max(self.entry_duration_ms, 100):
                # activate prepared scene
                try:
                    self.app.current_scene = self._target_scene
                except Exception:
                    try:
                        self.app.change_scene(self._target_scene.__class__)
                    except Exception:
                        pass
                self.done = True

    def render(self, screen):
        sw, sh = screen.get_size()

        if self.phase == 'exit':
            # draw melt of previous surface
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

        elif self.phase == 'entry':
            # draw assembly of target surface (bands move from above into place)
            if self._entry_surface is not None:
                prev = self._entry_surface
                if prev.get_size() != (sw, sh):
                    prev = pygame.transform.smoothscale(prev, (sw, sh))

                if self._max_offset is None:
                    self._max_offset = int(sh * 0.45)

                now = pygame.time.get_ticks()
                elapsed = now - (self.entry_start or now)
                t = min(1.0, float(elapsed) / max(1, self.entry_duration_ms))

                band_h = max(1, sh // self._bands)

                for i in range(self._bands):
                    y = i * band_h
                    h = band_h
                    if y + h > sh:
                        h = sh - y
                    if h <= 0:
                        continue

                    # band start stagger so top bands finalize first (reverse of melt)
                    band_start = float(i) / max(1, self._bands) * 0.9
                    local_t = max(0.0, (t - band_start) / (1.0 - band_start)) if t > band_start else 0.0
                    ease = pow(local_t, 0.6)

                    # offset goes from -max_offset*rand -> 0
                    offset = int((1.0 - ease) * (-self._max_offset * self._rand[i]))

                    try:
                        src_rect = pygame.Rect(0, y, sw, h)
                        band_surf = prev.subsurface(src_rect).copy()
                        screen.blit(band_surf, (0, y + offset))
                    except Exception:
                        screen.blit(prev, (0, 0))
                        break

                # overlay fades out as assembly completes
                overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
                overlay.fill((8, 8, 12, int(180 * (1.0 - t))))
                screen.blit(overlay, (0, 0))
            else:
                screen.fill((8, 8, 12))