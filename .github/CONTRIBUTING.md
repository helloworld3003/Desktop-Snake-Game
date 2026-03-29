# Contributing to Desktop Snake Game

First off, thank you for considering contributing to the Desktop Snake Game! It's people like you that make Desktop Snake Game such a great and fun project to work on.

This project is a unique take on the classic Snake game, played directly on your desktop by manipulating elements or using the desktop grid structure. 

## How to Contribute

There are many ways you can contribute to this project:
- **Reporting Bugs**: If you find an issue (e.g., incorrect collision detection, buggy icon dragging, or overlapping fruits), please open a new issue describing what you did, what happened, and what you expected to happen.
- **Requesting Features**: Have a cool idea? Let us know by opening a feature request issue.
- **Submitting Code**: Found a fix or want to add a feature? Awesome! Read below for how to submit a Pull Request.

## Areas for Improvement

We are continually looking to improve the game. Here are some key areas where contributions would be highly valuable:

- **Performance Optimization**: The current implementation heavily relies on OS-level interactions (like `PyAutoGUI` and `PyGetWindow`). Optimizations to reduce latency or lower CPU usage during icon manipulation and input blocking are very welcome.
- **Cross-Platform Compatibility**: Currently, the game is heavily tailored for Windows. Creating abstractions to support macOS or Linux desktop environments would be a massive step forward.
- **Enhanced Visuals and UI**: Refining the visual feedback when eating a fruit, ensuring the game-over screen is perfectly centered for any resolution, and building out more robust notification systems.
- **Robust Input Handling**: Refining the logic that separates programmatic mouse movements from physical mouse inputs to avoid any accidental interruptions or icon dragging issues.
- **Test Coverage**: Adding unit tests and integration tests for core game logic, grid coordinate calculations, and Python-OS interaction layers.

## Development Setup

The game relies heavily on OS-level interaction to organize the desktop grid and handle movements.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/helloworld3003/Desktop-Snake-Game.git
   cd Desktop-Snake-Game
   ```
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

**Core Files:**
- `snake_game_desktop.py`: The main game loop and control logic.
- `icon_organizer.py`: Manages the desktop icon calculations and precise movements.
- `grid_size.py`: Handles display properties, coordinate resolution, and virtual grid mapping.
- `physical_mouse_blocking.py`: Responsible for blocking physical mouse events to allow PyAutoGUI to simulate inputs safely without user interference.

## Making Changes

1. **Fork** the repository and create a descriptive branch for your changes (e.g., `feature/cross-platform-support` or `bugfix/icon-dragging`).
2. **Code**: Keep your code clean and add comments where necessary. When touching the movement/physics code, ensure that programmatic mouse movements (`PyAutoGUI`) do not conflict with physical mouse behavior.
3. **Test**: Before committing, run the game locally to ensure:
   - The snake eats the fruit correctly and increases in size.
   - Fruits do not spawn inside the snake's body or over reserved icons.
   - Physical mouse inputs are properly blocked and unblocked during execution.
   - The win/game-over UI displays nicely on the screen.
4. **Commit**: Write clear, concise commit messages detailing what your changes do.

## Pull Request Process

1. Open a Pull Request on GitHub.
2. In your PR description, explain thoroughly what you have changed. Link any issues that are related to your Pull Request.
3. Wait for code review. There might be some feedback or needed adjustments before your code is merged into the main branch.

## Code Style

- **Python**: Follow PEP 8 guidelines. Try substituting complex logic with well-named functions or class methods. Type hints are highly encouraged!

Thank you for contributing!
