import os
import pygame


class Hitspark:
    """Simple 2-frame hit spark effect.

    Loads `assets/images/effects/hitspark.png` which is expected to contain
    2 horizontal frames (each ~80x39). The effect plays once and then marks
    itself finished. Frames are scaled up by 2x to match requested size.
    """

    _frames = None
    _frame_w = 80
    _frame_h = 39

    def __init__(self, x, y):
        # world coordinates where the center of the hitspark should be drawn
        self.x = int(x)
        self.y = int(y)
        self.started = pygame.time.get_ticks()
        self.frame_index = 0
        self.finished = False

        # ensure frames loaded
        if Hitspark._frames is None:
            Hitspark._load_frames()

        # default durations per frame (ms)
        self.frame_durations = [80, 80]

    @classmethod
    def _load_frames(cls):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        path = os.path.join(base, 'assets', 'images', 'effects', 'hitspark.png')

        cls._frames = []
        try:
            if pygame.display.get_init():
                sheet = pygame.image.load(path).convert_alpha()
            else:
                sheet = pygame.image.load(path)
            sw, sh = sheet.get_size()
            # assume 2 frames horizontally; derive frame width if sizes differ
            frame_w = max(1, sw // 2)
            frame_h = sh
            # scale factor (200% = 2.0)
            scale = 2.0
            for i in range(2):
                rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), rect)
                # scale up frames to be 100% larger (2x)
                try:
                    new_w = int(rect.width * scale)
                    new_h = int(rect.height * scale)
                    surf = pygame.transform.smoothscale(surf, (new_w, new_h))
                except Exception:
                    pass
                cls._frames.append(surf)
            # record actual sizes
            if cls._frames:
                cls._frame_w, cls._frame_h = cls._frames[0].get_size()
        except Exception:
            # fallback: two tiny white ellipses
            for i in range(2):
                surf = pygame.Surface((int(cls._frame_w * 2), int(cls._frame_h * 2)), pygame.SRCALPHA)
                pygame.draw.ellipse(surf, (255, 220, 100), surf.get_rect())
                cls._frames.append(surf)

    def update(self):
        if self.finished:
            return
        now = pygame.time.get_ticks()
        elapsed = now - self.started
        total = 0
        for i, d in enumerate(self.frame_durations):
            total += d
            if elapsed < total:
                self.frame_index = i
                break
        else:
            # animation finished
            self.finished = True

    def draw(self, surface, camera):
        if self.finished:
            return
        if not Hitspark._frames:
            return

        frame = Hitspark._frames[self.frame_index % len(Hitspark._frames)]

        # compute screen position from world coords (centered)
        w, h = frame.get_size()
        rect = pygame.Rect(int(self.x - w // 2), int(self.y - h // 2), w, h)
        try:
            screen_pos = camera.apply(rect).topleft
        except Exception:
            screen_pos = (rect.x, rect.y)

        surface.blit(frame, screen_pos)

    def get_rect(self):
        return pygame.Rect(int(self.x - Hitspark._frame_w // 2), int(self.y - Hitspark._frame_h // 2), Hitspark._frame_w, Hitspark._frame_h)
