"""Camera system that follows the player.

Adds simple screen shake support via start_shake(duration_ms, magnitude).
"""
import pygame
import random


class Camera:
    """Camera follows the player and renders only visible portion of world.
    
    The camera is centered on the player (or slightly offset for better visibility).
    It respects map boundaries to prevent showing black void outside the playable area.
    """

    def __init__(self, screen_width, screen_height, world_width, world_height):
        """Initialize camera.
        
        Args:
            screen_width: Display width in pixels
            screen_height: Display height in pixels
            world_width: Total world/map width in pixels
            world_height: Total world/map height in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (top-left corner of visible area in world coordinates)
        self.x = 0
        self.y = 0

        # Screen shake state
        self.shake_magnitude = 0
        self.shake_end = 0
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_rect):
        """Update camera to follow target (usually the player).
        
        Args:
            target_rect: pygame.Rect of the entity to follow (player)
        """
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
        """Start a screen shake effect.

        Args:
            duration_ms: How long the shake lasts in milliseconds
            magnitude: Max pixel offset for shake
        """
        self.shake_magnitude = magnitude
        self.shake_end = pygame.time.get_ticks() + duration_ms

    def apply(self, rect):
        """Convert world coordinates to screen coordinates.
        
        Args:
            rect: pygame.Rect in world space
            
        Returns:
            pygame.Rect in screen space (relative to camera view)
        """
        return rect.move(-self.x - self.offset_x, -self.y - self.offset_y)

    def apply_point(self, x, y):
        """Convert a point from world coordinates to screen coordinates.
        
        Args:
            x, y: Position in world space
            
        Returns:
            Tuple (screen_x, screen_y)
        """
        return (x - self.x - self.offset_x, y - self.y - self.offset_y)

    def get_viewport_rect(self):
        """Get the visible area of the world in world coordinates.
        
        Returns:
            pygame.Rect representing the camera's view in world space
        """
        return pygame.Rect(self.x, self.y, self.screen_width, self.screen_height)
