import pygame
from ..settings import WHITE, BLACK
from ..entities.player import Player
from ..camera import Camera


class Gameplay:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        # Expanded world/map dimensions (much larger than screen)
        # This allows the player to move around in a larger world
        self.world_width = 2400  # 3x screen width for horizontal exploration
        self.world_height = 2400  # Match width for square-ish world proportions
        
        # Ground Y coordinate (in world space)
        self.ground_y = self.world_height - 150
        
        # Create player in the world (starting position)
        # Player height is 160, so position it appropriately on the ground
        self.player = Player(400, self.ground_y - 160)
        
        # Initialize camera to follow the player
        self.camera = Camera(self.screen_width, self.screen_height, self.world_width, self.world_height)
        
        self.font = pygame.font.Font(None, 28)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to main menu
                self.app.go_to_menu()
            # Attack with Ctrl -> call player's attack animation
            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.player.attack()

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        # Player update uses world dimensions instead of screen dimensions
        self.player.update(self.world_width, self.world_height, self.ground_y)
        # Update camera to follow the player
        self.camera.update(self.player.rect)

    def render(self, screen):
        # Background (fill screen with sky color)
        screen.fill((120, 180, 255))

        # Calculate ground position in screen space
        ground_screen_y = self.ground_y - self.camera.y
        
        # Draw ground (extends across the screen)
        if ground_screen_y < self.screen_height:
            pygame.draw.rect(
                screen,
                (80, 200, 80),
                (0, ground_screen_y, self.screen_width, self.screen_height - ground_screen_y)
            )

        # Draw player (convert to screen coordinates)
        player_screen_rect = self.camera.apply(self.player.rect)
        # Only draw if on screen
        if player_screen_rect.right > 0 and player_screen_rect.left < self.screen_width:
            self.player.draw_at(screen, player_screen_rect.topleft)

        # HUD / instructions (fixed to screen, not affected by camera)
        instr = self.font.render('Esc - Voltar ao Menu', True, BLACK)
        screen.blit(instr, (10, 10))
        
        # Debug: show camera position
        cam_debug = self.font.render(f'Cam: ({int(self.camera.x)}, {int(self.camera.y)})', True, BLACK)
        screen.blit(cam_debug, (10, 40))

    def update_events(self):
        # Not used: we handle single events via handle_event called by app
        pass
