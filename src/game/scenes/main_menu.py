import pygame
from ..settings import WHITE


class MainMenu:
    def __init__(self, app):
        """app: reference to GameApp instance"""
        self.app = app
        self.screen = app.screen
        self.font_title = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 36)
        self.title = self.font_title.render("Demo Game", True, WHITE)
        self.start_text = self.font.render("Enter - Start", True, WHITE)
        self.controls_lines = [
            "Controles:",
            "← / A  - Mover à esquerda",
            "→ / D  - Mover à direita",
            "Space  - Saltar",
            "Esc    - Voltar / Sair",
        ]
        # Play menu music with crossfade if available
        try:
            # fade_ms chosen small so transition feels snappy
            self.app.audio.crossfade_music('menu', fade_ms=800)
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Change to gameplay scene
                # import dynamically to avoid circular imports at module load time
                try:
                    self.app.audio.play_sound('select')
                except Exception:
                    pass
                import importlib
                mod = importlib.import_module('game.scenes.gameplay')
                Gameplay = getattr(mod, 'Gameplay')
                self.app.change_scene(Gameplay)
            if event.key == pygame.K_ESCAPE:
                self.app.running = False

    def update(self):
        pass

    def render(self, screen):
        screen.fill((20, 20, 40))
        # Title
        screen.blit(self.title, (screen.get_width() // 2 - self.title.get_width() // 2, 80))
        # Start instruction
        screen.blit(self.start_text, (screen.get_width() // 2 - self.start_text.get_width() // 2, 200))

        # Controls
        y = 300
        for line in self.controls_lines:
            text_surf = self.font.render(line, True, WHITE)
            screen.blit(text_surf, (screen.get_width() // 2 - text_surf.get_width() // 2, y))
            y += 36