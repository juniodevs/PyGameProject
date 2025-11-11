import pygame
import random


class Camera:

    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (top-left corner of visible area in world coordinates)
        self.x = 0
        self.y = 0

        # Screen shake state
        self.shake_magnitude = 5
        self.shake_end = 0
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_rect):
        # Center camera on the target (player's center)
        self.x = target_rect.centerx - self.screen_width // 2
        self.y = target_rect.centery - self.screen_height // 2
        
        # Clamp camera to world boundaries
        self.x = max(0, min(self.x, self.world_width - self.screen_width))
        self.y = max(0, min(self.y, self.world_height - self.screen_height))

        # Apply screen shake if active
        now = pygame.time.get_ticks()
        if self.shake_end and now < self.shake_end:
            self.offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
        else:
            self.offset_x = 0
            self.offset_y = 0

    def start_shake(self, duration_ms=300, magnitude=8):
        self.shake_magnitude = magnitude
        self.shake_end = pygame.time.get_ticks() + duration_ms

    def apply(self, rect):
        return rect.move(-self.x - self.offset_x, -self.y - self.offset_y)

    def apply_point(self, x, y):
        return (x - self.x - self.offset_x, y - self.y - self.offset_y)

    def get_viewport_rect(self):
        return pygame.Rect(self.x, self.y, self.screen_width, self.screen_height)
