import pygame
from ..settings import WHITE, BLACK
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..entities.projectile import Projectile


class Gameplay:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        # Ground Y coordinate
        self.ground_y = self.screen_height - 80

        # Create player and enemy
        self.player = Player(100, self.ground_y - 50)
        # Enemy patrol between x=300 and x=700
        self.enemy = Enemy(400, self.ground_y - 40, min_x=300, max_x=700)

        self.font = pygame.font.Font(None, 28)
        # Projectiles list
        self.projectiles = []
        # Cooldown in milliseconds
        self.shoot_cooldown_ms = 2000
        self.last_shot_time = 0

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.app.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to main menu
                self.app.go_to_menu()
            # Shoot projectile with Ctrl (left or right)
            if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                now = pygame.time.get_ticks()
                if now - self.last_shot_time >= self.shoot_cooldown_ms:
                    # create projectile at player's center, going in facing direction
                    p_x = self.player.rect.centerx
                    p_y = self.player.rect.centery
                    proj = Projectile(p_x, p_y, direction=self.player.facing)
                    self.projectiles.append(proj)
                    self.last_shot_time = now

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(self.screen_width, self.screen_height, self.ground_y)
        self.enemy.move()

        # Update projectiles
        for proj in list(self.projectiles):
            proj.update()
            # remove if off-screen
            if proj.rect.right < 0 or proj.rect.left > self.screen_width:
                try:
                    self.projectiles.remove(proj)
                except ValueError:
                    pass
            # collision with enemy
            elif proj.get_rect().colliderect(self.enemy.rect):
                # For demo: go back to menu on hit
                self.app.go_to_menu()

        # Collision: if player collides with enemy, go back to menu (demo behavior)
        if self.player.get_rect().colliderect(self.enemy.rect):
            # For demo, go back to menu on collision
            self.app.go_to_menu()

    def render(self, screen):
        # Background
        screen.fill((120, 180, 255))

        # Ground
        pygame.draw.rect(screen, (80, 200, 80), (0, self.ground_y, self.screen_width, self.screen_height - self.ground_y))

        # Draw entities
        self.player.draw(screen)
        self.enemy.draw(screen)

        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(screen)

        # HUD / instructions
        instr = self.font.render('Esc - Voltar ao Menu', True, BLACK)
        screen.blit(instr, (10, 10))

    def update_events(self):
        # Not used: we handle single events via handle_event called by app
        pass
