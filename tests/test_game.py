import unittest
from src.game.app import GameApp

class TestGameApp(unittest.TestCase):
    def setUp(self):
        self.game_app = GameApp()

    def test_initialization(self):
        self.assertIsNotNone(self.game_app)

    def test_game_loop(self):
        # This is a placeholder for testing the game loop
        self.game_app.run()
        self.assertTrue(self.game_app.is_running)

    def tearDown(self):
        self.game_app.quit()

if __name__ == '__main__':
    unittest.main()