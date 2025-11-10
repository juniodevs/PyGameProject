import pygame


class GameApp:
    def __init__(self):
        import pygame
        from .scenes.main_menu import MainMenu
        from .scenes.gameplay import Gameplay
        from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.FPS = FPS
        # Time scale for slow-motion effects (1.0 = normal speed)
        self.time_scale = 1.0
        self.slow_motion_end = 0
        self.current_scene = MainMenu(self)

    def run(self):
        while self.running:
            self.handle_events()
            self.current_scene.update()
            self.current_scene.render(self.screen)
            pygame.display.flip()
            # If a slow-motion effect is active, adjust target FPS
            now = pygame.time.get_ticks()
            if self.slow_motion_end and now >= self.slow_motion_end:
                self.time_scale = 1.0
                self.slow_motion_end = 0

            target_fps = max(1, int(self.FPS * self.time_scale))
            self.clock.tick(target_fps)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_scene.handle_event(event)

    def change_scene(self, scene):
        # scene should be a class (callable) that accepts the app instance
        self.current_scene = scene(self)

    def go_to_menu(self):
        """Convenience method for scenes to return to main menu without importing it."""
        from .scenes.main_menu import MainMenu
        self.current_scene = MainMenu(self)

    def trigger_slow_motion(self, duration_ms=200, scale=0.3):
        """Activate a brief slow-motion effect.

        Args:
            duration_ms: Duration in milliseconds
            scale: Time scale multiplier (0 < scale <= 1)
        """
        self.time_scale = max(0.01, min(1.0, scale))
        self.slow_motion_end = pygame.time.get_ticks() + int(duration_ms)