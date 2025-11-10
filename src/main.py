import pygame
from game.app import GameApp

def main():
    pygame.init()
    game = GameApp()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()