import pygame


class Player:
    def __init__(self, x, y):
        self.width = 50
        self.height = 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = 5
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.6
        self.on_ground = False

    def handle_input(self, keys):
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def update(self, screen_width, screen_height, ground_y):
        # Apply gravity
        self.vel_y += self.gravity
        # Move
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Floor collision
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.on_ground = True

        # Keep inside horizontal bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 200, 0), self.rect)

    def get_rect(self):
        return self.rect