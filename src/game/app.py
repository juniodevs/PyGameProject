import pygame
from .utils.audio import AudioManager

class GameApp:
    def __init__(self):
        import pygame
        from .scenes.main_menu import MainMenu
        from .scenes.gameplay import Gameplay
        from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

        pygame.init()

        try:
            self.audio = AudioManager()
        except Exception:

            class _NullAudio:
                def play_sound(self, *a, **k):
                    return None
                def play_music(self, *a, **k):
                    return False
                def stop_music(self, *a, **k):
                    return None
                def set_master_volume(self, *a, **k):
                    return None
                def set_sfx_volume(self, *a, **k):
                    return None
                def set_music_volume(self, *a, **k):
                    return None
                def preload_folder(self, *a, **k):
                    return 0
            self.audio = _NullAudio()

        try:
            from .utils.config import load_config
            cfg = load_config()
            try:
                self.audio.set_music_volume(cfg.get('music_volume', 0.6))
                self.audio.set_sfx_volume(cfg.get('sfx_volume', 1.0))
                self.audio.set_master_volume(cfg.get('master_volume', 1.0))
            except Exception:
                pass
        except Exception:
            pass

        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Game")

        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.FPS = FPS

        self.time_scale = 1.0
        self.slow_motion_end = 0

        self._zoom_start = 0
        self._zoom_duration = 0
        self._zoom_mag = 1.0
        self.current_scene = MainMenu(self)

    def run(self):
        while self.running:
            self.handle_events()
            self.current_scene.update()

            self.current_scene.render(self.screen)

            now = pygame.time.get_ticks()
            if self.slow_motion_end and now >= self.slow_motion_end:
                self.time_scale = 1.0
                self.slow_motion_end = 0

            zoom = 1.0
            if self._zoom_start and now < self._zoom_start + self._zoom_duration:
                t = now - self._zoom_start
                half = self._zoom_duration / 2.0
                mag = self._zoom_mag
                if t <= half:
                    zoom = 1.0 + (mag - 1.0) * (t / half)
                else:
                    zoom = mag - (mag - 1.0) * ((t - half) / half)
            else:
                if self._zoom_start and now >= self._zoom_start + self._zoom_duration:
                    self._zoom_start = 0
                    self._zoom_duration = 0
                    self._zoom_mag = 1.0

            sw, sh = self.screen.get_size()
            if abs(zoom - 1.0) > 0.0001:
                scaled_w = max(1, int(sw * zoom))
                scaled_h = max(1, int(sh * zoom))
                scaled = pygame.transform.smoothscale(self.screen, (scaled_w, scaled_h))
                dx = (sw - scaled_w) // 2
                dy = (sh - scaled_h) // 2
                self.display.fill((0, 0, 0))
                self.display.blit(scaled, (dx, dy))
            else:
                self.display.blit(self.screen, (0, 0))

            pygame.display.flip()

            target_fps = max(1, int(self.FPS * self.time_scale))
            self.clock.tick(target_fps)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_scene.handle_event(event)

    def change_scene(self, scene):

        self.current_scene = scene(self)

    def go_to_menu(self):
        """Convenience method for scenes to return to main menu without importing it."""
        try:
            from .scenes.main_menu import MainMenu
            from .scenes.load_screen import LoadScreen
            prev = None
            try:
                prev = self.screen.copy()
            except Exception:
                prev = None
            # pass previous screen so LoadScreen can animate a melt/datamosh
            self.change_scene(lambda app, p=prev: LoadScreen(app, target=MainMenu, message='VOLTANDO AO MENU...', duration_ms=600, prev_surface=p))
        except Exception:
            try:
                from .scenes.main_menu import MainMenu
                self.current_scene = MainMenu(self)
            except Exception:
                pass

    def trigger_slow_motion(self, duration_ms=200, scale=0.3):
        """Activate a brief slow-motion effect.

        Args:
            duration_ms: Duration in milliseconds
            scale: Time scale multiplier (0 < scale <= 1)
        """
        self.time_scale = max(0.01, min(1.0, scale))
        self.slow_motion_end = pygame.time.get_ticks() + int(duration_ms)

    def trigger_zoom(self, duration_ms=220, magnitude=1.08):
        """Trigger a brief zoom-in then back effect.

        Args:
            duration_ms: Duration in milliseconds
            magnitude: Zoom magnitude (>= 1.0)
        """
        self._zoom_start = pygame.time.get_ticks()
        self._zoom_duration = int(duration_ms)
        self._zoom_mag = max(1.0, float(magnitude))