import pygame


class Projectile:
    def __init__(self, x, y, direction=1, speed=10, color=(255, 40, 40), width=8, height=4):
        # x,y is the center start position
        self.width = width
        self.height = height
        # create rect with center at (x,y)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.direction = 1 if direction >= 0 else -1
        self.speed = speed * self.direction
        self.color = color

    def update(self):
        self.rect.x += int(self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def get_rect(self):
        return self.rect
