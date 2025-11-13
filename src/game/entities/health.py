import os
import pygame


class Health:
    """Simple health pickup entity.

    - Loads an asset from assets/images/health/_Health.png if present.
    - If missing, generates a small placeholder image and saves it to that path.
    - Has a rect and simple draw/get_hitbox helpers.
    """

    def __init__(self, x, y):
        # visual size of the pickup
        self.width = 48
        self.height = 48
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # small hitbox within the sprite
        self.hitbox_inset = 8

        self.image = None
        self._load_image()

    def _load_image(self):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        assets_dir = os.path.join(base, 'assets', 'images', 'health')
        os.makedirs(assets_dir, exist_ok=True)
        fname = os.path.join(assets_dir, '_Health.png')

        if not os.path.exists(fname):
            # generate a simple placeholder and save it so designers can replace the file later
            try:
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                # draw a simple heart-like shape (two circles + triangle) in red
                c = (220, 30, 60)
                pygame.draw.circle(surf, c, (int(self.width * 0.33), int(self.height * 0.33)), 10)
                pygame.draw.circle(surf, c, (int(self.width * 0.66), int(self.height * 0.33)), 10)
                pts = [
                    (int(self.width * 0.15), int(self.height * 0.45)),
                    (int(self.width * 0.5), int(self.height * 0.9)),
                    (int(self.width * 0.85), int(self.height * 0.45)),
                ]
                pygame.draw.polygon(surf, c, pts)
                # try to save the PNG so a real asset file exists in the repo on first run
                try:
                    pygame.image.save(surf, fname)
                except Exception:
                    # saving may fail in some environments; that's fine — we'll still use surf
                    pass
                self.image = surf
                return
            except Exception:
                # fallback - create a simple surface colored green
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                surf.fill((0, 200, 0))
                self.image = surf
                return

        # try loading existing file
        try:
            if pygame.display.get_init():
                img = pygame.image.load(fname).convert_alpha()
            else:
                img = pygame.image.load(fname)
        except Exception:
            img = None

        if img is None:
            surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            surf.fill((0, 200, 0))
            self.image = surf
            return

        try:
            self.image = pygame.transform.smoothscale(img, (self.width, self.height))
        except Exception:
            self.image = img

    def update(self):
        # stationary pickup — no logic here for now
        return None

    def draw_at(self, surface, pos):
        if self.image:
            surface.blit(self.image, pos)
        else:
            pygame.draw.rect(surface, (0, 200, 0), (*pos, self.width, self.height))

    def get_hitbox(self):
        return pygame.Rect(self.rect.x + self.hitbox_inset, self.rect.y + self.hitbox_inset,
                           max(4, self.width - self.hitbox_inset * 2), max(4, self.height - self.hitbox_inset * 2))
