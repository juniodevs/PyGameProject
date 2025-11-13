import os
import pygame


class Fireball:
    """Projectile fireball that uses a 3-frame horizontal sprite-sheet

    Expects assets/images/effects/fireBall.png with 3 frames. Each frame is
    roughly 48x12 (as provided by the user). Frames are doubled in size for
    visibility.
    """

    _frames = None

    def __init__(self, x, y, direction, speed=12, lifetime_ms=3000):
        # x,y is the spawn center position
        self.speed = speed
        self.vx = speed * (1 if direction >= 0 else -1)
        self.vy = 0
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime_ms = lifetime_ms
        self.finished = False

        # animation state
        self.frame_index = 0
        self.frame_started = pygame.time.get_ticks()
        self.frame_durations = [80, 80, 80]

        if Fireball._frames is None:
            Fireball._load_frames()

        # default rect from first frame if available
        if Fireball._frames and len(Fireball._frames) > 0:
            fw, fh = Fireball._frames[0].get_size()
            self.rect = pygame.Rect(int(self.x - fw // 2), int(self.y - fh // 2), fw, fh)
        else:
            self.radius = 14
            self.rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    @classmethod
    def _load_frames(cls):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        path = os.path.join(base, 'assets', 'images', 'effects', 'fireBall.png')
        cls._frames = []
        try:
            if pygame.display.get_init():
                sheet = pygame.image.load(path).convert_alpha()
            else:
                sheet = pygame.image.load(path)
            sw, sh = sheet.get_size()
            frame_count = 3
            frame_w = max(1, sw // frame_count)
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_w, 0, frame_w, sh)
                surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), rect)
                try:
                    surf = pygame.transform.smoothscale(surf, (int(rect.width * 2.0), int(rect.height * 2.0)))
                except Exception:
                    pass
                cls._frames.append(surf)
        except Exception:
            # fallback visuals
            for i in range(3):
                surf = pygame.Surface((28, 28), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 180, 60), (14, 14), 12)
                cls._frames.append(surf)

    def update(self, world_width=None, world_height=None):
        if self.finished:
            return
        self.x += self.vx
        self.y += self.vy

        # animation frame update
        now = pygame.time.get_ticks()
        elapsed = now - self.frame_started
        dur_sum = sum(self.frame_durations)
        t = elapsed % dur_sum
        s = 0
        for i, d in enumerate(self.frame_durations):
            s += d
            if t < s:
                self.frame_index = i
                break

        # update rect
        if Fireball._frames and len(Fireball._frames) > 0:
            fw, fh = Fireball._frames[self.frame_index].get_size()
            self.rect.x = int(self.x - fw // 2)
            self.rect.y = int(self.y - fh // 2)
        else:
            try:
                self.rect.x = int(self.x - self.rect.width // 2)
                self.rect.y = int(self.y - self.rect.height // 2)
            except Exception:
                pass

        if now - self.spawn_time > self.lifetime_ms:
            self.finished = True
            return

        if world_width is not None:
            if self.rect.right < 0 or self.rect.left > world_width:
                self.finished = True

    def draw(self, surface, camera=None):
        if self.finished:
            return
        draw_rect = self.rect.copy()
        if camera is not None:
            try:
                draw_rect = camera.apply(draw_rect)
            except Exception:
                pass

        if Fireball._frames and len(Fireball._frames) > 0:
            frame = Fireball._frames[self.frame_index % len(Fireball._frames)]
            try:
                surface.blit(frame, draw_rect.topleft)
            except Exception:
                pass
        else:
            # fallback: draw circle
            try:
                core = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.circle(core, (255, 180, 60, 220), (self.rect.width // 2, self.rect.height // 2), min(self.rect.width, self.rect.height) // 2 - 2)
                surface.blit(core, draw_rect.topleft)
            except Exception:
                try:
                    pygame.draw.circle(surface, (255, 120, 40), (draw_rect.centerx, draw_rect.centery), 8)
                except Exception:
                    pass

    def get_hitbox(self):
        return self.rect
