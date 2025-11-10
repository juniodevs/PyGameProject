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
        
        # Death state tracking
        self.is_dead = False
        self.death_time = 0  # Timestamp when player died
        self.death_countdown = 5  # Seconds before returning to menu

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
            # Test damage with 'H' key (for testing HP system)
            if event.key == pygame.K_h:
                self.player.take_damage(1)

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        # Player update uses world dimensions instead of screen dimensions
        self.player.update(self.world_width, self.world_height, self.ground_y)
        
        # Check if player just died
        if self.player.current_hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.death_time = pygame.time.get_ticks()
        
        # If player is dead, manage countdown and return to menu
        if self.is_dead:
            now = pygame.time.get_ticks()
            elapsed_ms = now - self.death_time
            elapsed_s = elapsed_ms / 1000.0
            
            if elapsed_s >= self.death_countdown:
                # Countdown finished, return to menu
                self.app.go_to_menu()
        
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
        
        # Draw HP overlay (5 hearts/hearts)
        self._draw_hp_overlay(screen)
        
        # If player is dead, show death countdown
        if self.is_dead:
            self._draw_death_countdown(screen)
        
        # Debug: show camera position
        cam_debug = self.font.render(f'Cam: ({int(self.camera.x)}, {int(self.camera.y)})', True, BLACK)
        screen.blit(cam_debug, (10, 40))

    def _draw_hp_overlay(self, screen):
        """Draw HP overlay showing current HP / max HP as visual hearts/bars."""
        # HP display at top right
        hp_x = self.screen_width - 200
        hp_y = 20
        
        # Draw label
        hp_label = self.font.render(f'HP: {self.player.current_hp} / {self.player.max_hp}', True, (0, 0, 0))
        screen.blit(hp_label, (hp_x, hp_y))
        
        # Draw HP bars visually (5 bars)
        bar_width = 25
        bar_height = 20
        bar_gap = 5
        bar_x = hp_x
        bar_y = hp_y + 35
        
        for i in range(self.player.max_hp):
            # Draw background (gray)
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw current HP (green for alive, red if low)
            if i < self.player.current_hp:
                # Full bar - green
                color = (0, 200, 0)
            else:
                # Empty bar - dark gray
                color = (50, 50, 50)
            
            pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)  # Border
            
            bar_x += bar_width + bar_gap

    def _draw_death_countdown(self, screen):
        """Draw death screen with countdown to return to menu."""
        # Semi-transparent overlay (dark)
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Calculate remaining time
        now = pygame.time.get_ticks()
        elapsed_ms = now - self.death_time
        remaining_s = max(0, self.death_countdown - (elapsed_ms / 1000.0))
        
        # Death message
        large_font = pygame.font.Font(None, 72)
        death_text = large_font.render('VOCÊ MORREU', True, (255, 0, 0))
        text_rect = death_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
        screen.blit(death_text, text_rect)
        
        # Countdown
        countdown_font = pygame.font.Font(None, 48)
        countdown_text = countdown_font.render(f'Retornando em: {int(remaining_s) + 1}s', True, (255, 255, 255))
        countdown_rect = countdown_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        screen.blit(countdown_text, countdown_rect)

    def update_events(self):
        # Not used: we handle single events via handle_event called by app
        pass
