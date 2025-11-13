import os
import pygame


class FireInBody:
    """Looping fire-in-body effect attached to an enemy.

    Loads `assets/images/effects/fireInBody.png` (4 frames horizontally).
    The effect is positioned relative to the enemy's rect center and will
    mark itself finished when the enemy's death animation has finished
    (same condition used when gameplay removes enemies).
    """

    _frames = None

    def __init__(self, enemy, impact_offset_y=0):
        self.enemy = enemy
        self.frame_index = 0
        self.started = pygame.time.get_ticks()
        self.finished = False
        # per-frame duration
        self.frame_durations = [120, 120, 120, 120]
        # offset relative to enemy center (pixels). Positive moves effect down
        self.offset_y = int(impact_offset_y)

        if FireInBody._frames is None:
            FireInBody._load_frames()

    @classmethod
    def _load_frames(cls):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        path = os.path.join(base, 'assets', 'images', 'effects', 'fireInBody.png')
        cls._frames = []
        try:
            if pygame.display.get_init():
                sheet = pygame.image.load(path).convert_alpha()
            else:
                sheet = pygame.image.load(path)
            sw, sh = sheet.get_size()
            frame_count = 4
            frame_w = max(1, sw // frame_count)
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, sh)
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), rect)
                # scale up for visibility
                try:
                    surf = pygame.transform.smoothscale(surf, (int(rect.width * 3.0), int(rect.height * 3.0)))
                except Exception:
                    pass
                cls._frames.append(surf)
        except Exception:
            # fallback: small orange rectangle
            for i in range(4):
                surf = pygame.Surface((32, 16), pygame.SRCALPHA)
                surf.fill((255, 140, 40))
                cls._frames.append(surf)

    def update(self):
        if self.finished:
            return
        now = pygame.time.get_ticks()
        # if the enemy is in death state and its death_time passed the removal threshold, finish
        try:
            if getattr(self.enemy, 'current_hp', 0) <= 0 and getattr(self.enemy, 'death_time', 0) > 0 and now - self.enemy.death_time > 1000:
                self.finished = True
                return
        except Exception:
            pass

        # advance frame based on durations looping
        total = 0
        elapsed = now - self.started
        dur_sum = sum(self.frame_durations)
        t = elapsed % dur_sum
        s = 0
        for i, d in enumerate(self.frame_durations):
            s += d
            if t < s:
                self.frame_index = i
                break

    def draw(self, surface, camera):
        if self.finished:
            return
        if not FireInBody._frames:
            return

        frame = FireInBody._frames[self.frame_index % len(FireInBody._frames)]
        # position at enemy center plus dynamic offset (impact-based)
        try:
            er = self.enemy.rect
            cx = er.centerx
            cy = er.centery
            fw, fh = frame.get_size()
            rect = pygame.Rect(int(cx - fw // 2), int(cy - fh // 2) + self.offset_y, fw, fh)
            try:
                screen_pos = camera.apply(rect).topleft
            except Exception:
                screen_pos = (rect.x, rect.y)
            surface.blit(frame, screen_pos)
        except Exception:
            pass

    def get_rect(self):
        if not FireInBody._frames:
            return pygame.Rect(0, 0, 0, 0)
        frame = FireInBody._frames[0]
        er = getattr(self.enemy, 'rect', pygame.Rect(0, 0, 0, 0))
        fw, fh = frame.get_size()
        return pygame.Rect(int(er.centerx - fw // 2), int(er.centery - fh // 2) + self.offset_y, fw, fh)
