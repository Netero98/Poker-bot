# Poker-bot Project Documentation

This document provides a comprehensive overview of the Poker-bot application, its structure, key modules, and how they interact.

## Project Overview

Poker-bot is an automated poker playing software designed to play on various poker platforms (Pokerstars, Partypoker, GGPoker, etc.). It uses screen scraping (OCR and image recognition) to understand the game state, Monte Carlo simulations for equity calculation, and a decision engine (potentially improved by genetic algorithms) to determine the best action.

## Directory Structure

```
/home/dan/Desktop/web/Poker-bot/
├── poker/                  # Main source code package
│   ├── decisionmaker/      # Logic for making poker decisions
│   ├── gui/                # Graphical User Interface logic and resources
│   ├── scraper/            # Screen scraping and computer vision logic
│   ├── tools/              # Utility scripts (logging, mouse control, DB)
│   ├── main.py             # Application entry point
│   └── ...
├── website/                # Website related files (documentation/landing page)
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── readme.rst              # Original project README
```

## Key Files and Modules

### 1. Entry Point
- **`poker/main.py`**:
    - **Role**: The main driver of the application.
    - **Functionality**:
        - Initializes the Qt Application and UI (`UiPokerbot`).
        - Starts the `ThreadManager` which runs the main game loop.
        - **Main Loop**:
            - Scrapes the table (`TableScreenBased`).
            - Runs Monte Carlo simulations (`run_montecarlo_wrapper`).
            - Invokes the decision maker (`Decision`).
            - Executes the decision via mouse actions.
            - Updates the GUI.
            - Logs the game state (`GameLogger`).

### 2. Decision Maker (`poker/decisionmaker/`)
This package handles the "brain" of the bot.

- **`decisionmaker.py`**:
    - **Class `Decision`**: The core class that takes the game state (`Table` object) and history, applies the selected strategy, and returns a decision (Call, Bet, Fold, Check, etc.).
    - **Methods**: `preflop_table_analyser`, `calling`, `betting`, `bluff`, `bully`.
- **`montecarlo_python.py`** (and `montecarlo_numpy*.py`):
    - **Role**: Performs Monte Carlo simulations to estimate specific hand equity against opponent ranges.
- **`genetic_algorithm.py`**:
    - **Role**: Implements a genetic algorithm to optimize strategy parameters over time.
- **`current_hand_memory.py`**:
    - **Role**: Stores state information about the current hand and previous actions to track game history.

### 3. Scraper (`poker/scraper/`)
This package is responsible for "seeing" what's happening on the screen.

- **`table_screen_based.py`**:
    - **Class `TableScreenBased`**: The primary scraper class.
    - **Functionality**:
        - `take_screenshot`: Captures the game window.
        - `get_my_cards`, `get_table_cards`: Identifies cards using OCR/template matching.
        - `get_total_pot_value`, `get_round_pot_value`: Reads pot sizes.
        - `check_for_button*`: Detects which buttons (Call, Bet, Fold) are available.
        - `get_other_player_status`: Detailed info about opponents.
- **`table_setup_actions_and_signals.py`**:
    - **Class `TableSetupActionAndSignals`**: The logic behind the "Table Setup" window.
    - **Functionality**:
        - Allows users to define where on the screen specific elements (cards, buttons, pot) are located.
        - Saves these coordinates and images to create new table mappings.
        - Manages screenshots for training or template matching.

### 4. GUI (`poker/gui/`)
Handles the user interface.

- **`action_and_signals.py`**:
    - **Class `UIActionAndSignals`**: Bridges the backend logic and the Qt UI.
    - **Functionality**:
        - Updates labels, charts, and progress bars.
        - Handles menu actions (opening settings, strategy editor, analyzer).

### 5. Tools (`poker/tools/`)
Helper modules.

- **`mouse_mover.py`**: Handles low-level mouse interactions to click buttons on the poker client.
- **`game_logger.py`**: Logs hand history, decisions, and screenshots for analysis.
- **`mongo_manager.py`**: Manages connections to a MongoDB database, used for storing table mappings and potentially neural network weights.

## Configuration and Setup

- **`requirements.txt`**: Lists all Python libraries required (e.g., `numpy`, `pandas`, `PyQt6`, `opencv`, `pillow`).
- **`Dockerfile`**: Defines the environment for running the bot in a container (typically recommended to isolate it from the host system / allow virtual display).
- **`config.ini` / `config_default.ini`**: Stores configuration settings (can be edited via the GUI Setup).

## Workflow Summary

1.  **Launch**: User runs `main.py`. GUI opens.
2.  **Setup**: User configures the "Table Scraper" (defining where buttons/cards are on the screen).
3.  **Run**: User starts the bot.
4.  **Loop**:
    - **Scrape**: `TableScreenBased` reads the pixels.
    - **Analyze**: `MonteCarlo` + `Decision` logic analyzes the situation.
    - **Act**: `MouseMover` clicks the appropriate button.
    - **Log**: Results are saved.
