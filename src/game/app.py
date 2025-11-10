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
        self.current_scene = MainMenu(self)

    def run(self):
        while self.running:
            self.handle_events()
            self.current_scene.update()
            self.current_scene.render(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.current_scene.handle_event(event)

    def change_scene(self, scene):
        self.current_scene = scene(self)