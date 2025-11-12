# Pygame Game Project

## Overview
This project is a simple game developed using Pygame. It serves as a foundation for building a more complex game, featuring a main menu and a gameplay scene.

## Project Structure
```
pygame-game
├── src
│   ├── main.py
│   ├── game
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── settings.py
│   │   ├── scenes
│   │   │   ├── __init__.py
│   │   │   ├── main_menu.py
│   │   │   └── gameplay.py
│   │   ├── entities
│   │   │   ├── __init__.py
│   │   │   ├── player.py
│   │   │   └── enemy.py
│   │   └── utils
│   │       └── __init__.py
│   └── assets
│       ├── sounds
│       ├── music
│       └── fonts
├── tests
│   └── test_game.py
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd pygame-game
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Game
To start the game, run the following command:
```
python src/main.py
```

## Audio assets (how to add)
The game includes an AudioManager that looks for audio files under `src/assets`.

- Sound effects: place short SFX files in `src/assets/sounds/` (recommended formats: .wav, .ogg, .mp3).
   Example names: `attack.wav`, `hit.wav`, `player_hurt.wav`, `enemy_die.wav`, `select.wav`.
- Music: place background tracks in `src/assets/music/` (recommended: .ogg, .mp3).
   Example names: `menu.ogg`, `gameplay.ogg`, `game_over.ogg`.

The code will try to load by name (e.g. `self.app.audio.play_sound('attack')`) and will try common extensions automatically.
You can also preload all sounds by calling `app.audio.preload_folder()` from your code if desired.

## Game Features
- Main Menu: Navigate through the main menu to start the game.
- Gameplay: Experience basic gameplay mechanics.

## Contributing
Feel free to fork the repository and submit pull requests for any improvements or features you would like to add.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.