# Copilot Instructions

This document provides guidance for AI coding agents to effectively contribute to the `telegram-game` repository.

## Project Overview

This is a text-based RPG game designed to be played via Telegram. The game logic is written in Python.

### Architecture

The project follows a simple object-oriented architecture:

-   **Game Data (`json/`)**: Game entities like monsters, items, and characters are defined in JSON files. These are loaded at runtime.
-   **Core Classes (`src/class_*.py`)**: These files define the main game objects (e.g., `Hero`, `Monster`, `Room`, `Castle`). They represent the state and basic behaviors of game entities.
-   **Controllers (`src/controllers/controller_*.py`)**: Controllers implement the game logic. They manipulate the core classes based on game events and player actions. For example, `controller_monsters.py` manages monster generation and attributes, and `controller_weapon.py` handles weapon logic.
-   **Main Entrypoint (`main.py`)**: This file initializes the game, loads data, and starts the main game loop. It integrates with the Telegram bot framework.
-   **Tests (`tests/`)**: Unit tests for various components of the game.

### Data Flow

1.  Game data is loaded from the `json/` directory into the respective controller classes upon game initialization.
2.  The `main.py` script orchestrates the game flow, responding to player input from Telegram.
3.  Player actions are processed by the controllers, which update the state of the game objects (e.g., hero's health, inventory, room state).
4.  The game state is presented back to the user through Telegram messages.

## Development Workflow

### Setup

The project uses a `requirements.txt` file for managing Python dependencies. To set up the environment, run:

```bash
pip install -r requirements.txt
```

### Running the Game

The main entry point for the application is `main.py`.

```bash
python main.py
```

### Testing

The project uses `pytest` for testing. Tests are located in the `tests/` directory. To run all tests, execute:

```bash
pytest
```

To run tests for a specific file:

```bash
pytest tests/some_test.py
```

## Key Conventions

-   **Class Naming**: Core data models are in files named `class_*.py` (e.g., `src/class_hero.py`).
-   **Controller Logic**: Business logic is separated into controller files, `controller_*.py` (e.g., `src/controllers/controller_heroes.py`).
-   **JSON for Data**: All static game data is stored in the `json/` directory. When adding new items, monsters, or other game elements, a corresponding JSON entry is required.
-   **Type Hinting**: The codebase is progressively adding type hints. Please add type hints for any new code you write.
-   **State Management**: Game state is managed through instances of the classes defined in `src/`. Controllers should not hold state themselves but operate on the stateful objects passed to them.
