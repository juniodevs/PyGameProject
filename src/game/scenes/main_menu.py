class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.title = self.font.render("Main Menu", True, (255, 255, 255))
        self.start_text = self.font.render("Press Enter to Start", True, (255, 255, 255))
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_game()

    def start_game(self):
        # Logic to transition to the gameplay scene
        pass

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title, (self.screen.get_width() // 2 - self.title.get_width() // 2, 100))
        self.screen.blit(self.start_text, (self.screen.get_width() // 2 - self.start_text.get_width() // 2, 300))
        pygame.display.flip()