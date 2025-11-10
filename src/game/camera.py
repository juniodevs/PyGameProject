"""Camera system that follows the player."""
import pygame


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

    def apply(self, rect):
        """Convert world coordinates to screen coordinates.
        
        Args:
            rect: pygame.Rect in world space
            
        Returns:
            pygame.Rect in screen space (relative to camera view)
        """
        return rect.move(-self.x, -self.y)

    def apply_point(self, x, y):
        """Convert a point from world coordinates to screen coordinates.
        
        Args:
            x, y: Position in world space
            
        Returns:
            Tuple (screen_x, screen_y)
        """
        return (x - self.x, y - self.y)

    def get_viewport_rect(self):
        """Get the visible area of the world in world coordinates.
        
        Returns:
            pygame.Rect representing the camera's view in world space
        """
        return pygame.Rect(self.x, self.y, self.screen_width, self.screen_height)
