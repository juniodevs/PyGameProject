import os
import pygame


class ParallaxBackground:
    """Parallax background manager.

    Loads layers 1..8 from assets/images/background and draws them with
    different parallax factors and opacities. Layer 7 is treated as the ground
    and aligned to the world's ground Y.
    """

    def __init__(self, screen_width, screen_height, world_width, ground_y):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.ground_y = ground_y

        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assets_dir = os.path.join(base, 'assets', 'images', 'background')

        # Load images 1..8 if present
        self.layers = []
        for i in range(1, 9):
            path = os.path.join(assets_dir, f'{i}.png')
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
            else:
                # fallback: a transparent surface so game won't crash
                img = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            self.layers.append(img)

        # Per-layer configuration: (parallax_factor, alpha, vertical_type)
        # vertical_type: 'top' = pinned to top, 'bottom' = align bottom to ground,
        # 'above_ground' = slightly above ground (distant trees)
        self.config = {
            1: (0.0, 255, 'top'),    # full white base
            2: (0.15, 190, 'top'),   # sky with moon, slightly translucent
            3: (0.35, 120, 'above_ground'),
            4: (0.34, 110, 'above_ground'),
            5: (0.32, 115, 'above_ground'),
            6: (0.05, 60, 'top'),    # thin fog overlay
            7: (0.9, 255, 'ground'), # ground (near player), moves almost with player
            8: (0.75, 220, 'ground'),# closer trees near ground
        }

        # Prepare alpha-applied copies so we don't modify originals each frame.
        # We will NOT scale the images here — the user indicated the images already
        # have the correct sizes. We'll blit them at their natural sizes and just
        # apply per-layer alpha.
        self.layer_surfaces = {}
        for idx, img in enumerate(self.layers, start=1):
            factor, alpha, vtype = self.config.get(idx, (0.5, 255, 'top'))
            surf = img.copy()
            # Apply configured alpha (if any)
            try:
                surf.set_alpha(alpha)
            except Exception:
                pass
            self.layer_surfaces[idx] = surf

    def draw(self, screen, camera):
        """Draw all layers to the screen using the provided camera."""
        # ground_screen_y (in screen space)
        ground_screen_y = self.ground_y - camera.y

        for idx in range(1, 9):
            img = self.layer_surfaces.get(idx)
            if img is None:
                continue

            factor, alpha, vtype = self.config.get(idx, (0.5, 255, 'top'))
            img_w, img_h = img.get_size()

            # Horizontal parallax offset based on camera.x
            # More distant layers (small factor) move less.
            # Use positive offset = int(camera.x * factor) % img_w so layers move
            # in the same direction as world movement (camera.x increasing -> layers shift left).
            offset_x = int(camera.x * factor) % img_w if img_w > 0 else 0

            # Determine vertical position in screen space
            if vtype == 'top':
                y = 0
            elif vtype == 'ground':
                # Align the bottom of the image to the ground line
                y = int(ground_screen_y - img_h)
            elif vtype == 'above_ground':
                # Place slightly higher than ground to look distant
                y = int(ground_screen_y - img_h - 120)
            else:
                y = 0

            # Draw the layer at its natural size. We position its left edge at
            # -offset_x so it scrolls with parallax. To be safe we draw three
            # tiles (left/current/right) to avoid gaps when images are not
            # perfectly screen-sized.
            start_x = -offset_x
            screen.blit(img, (start_x, y))
            # right tile
            screen.blit(img, (start_x + img_w, y))
            # left tile
            screen.blit(img, (start_x - img_w, y))
