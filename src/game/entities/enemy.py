import pygame


class Enemy:
    def __init__(self, x, y, min_x=None, max_x=None):
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 100
        self.speed = 2
        self.direction = 1
        # Patrol bounds
        self.min_x = min_x
        self.max_x = max_x

    def move(self):
        # Simple horizontal patrol between min_x and max_x if provided
        self.rect.x += int(self.speed * self.direction)
        if self.min_x is not None and self.rect.x < self.min_x:
            self.rect.x = self.min_x
            self.direction *= -1
        if self.max_x is not None and self.rect.x > self.max_x:
            self.rect.x = self.max_x
            self.direction *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 0, 0), self.rect)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        # For now just hide off-screen
        self.rect.x = -1000