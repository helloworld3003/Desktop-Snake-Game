# 🐍 Desktop Snake Game

A highly experimental, Python-based Snake game that literally uses your Windows desktop icons as the snake! Eat icons to grow longer, and navigate your desktop grid to win. 

Instead of drawing pixels on a canvas, this script uses `pyautogui` to physically drag your desktop shortcuts around the screen. If you manage to eat enough icons, you might even trigger a custom pixel-art Easter egg!

## ⚠️ Assumptions & Requirements
Because this game interacts directly with your OS GUI, it requires a specific environment to run correctly:
* **Operating System:** Windows 
* **Display Resolution:** 1920x1080
* **Icon Settings:** Medium Icons, Auto-arrange disabled during gameplay, Align to grid.
* **Grid Dimensions:** Assumes a standard 95x125 desktop icon grid spacing.
* **Settings:** "Drag to share" or "Single-click to open an item" must be turned OFF in Windows settings.

## 🎮 How to Play (For Gamers)
If you just want to play the game without messing with Python code:
1. Navigate to the **[Releases](#)** tab on the right side of this GitHub page.
2. Download the latest `snake_game_desktop.exe` file.
3. Double-click the `.exe` to launch.
4. **Controls:** Use the `Up`, `Down`, `Left`, and `Right` arrow keys to steer. Press `ESC` to exit at any time.

## 💻 How to Install (For Developers)
If you want to view the code, debug, or modify the game:

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/Desktop-Snake-Game.git](https://github.com/YourUsername/Desktop-Snake-Game.git)
   ```
2. Navigate into the project directory:
   ```bash
   cd Desktop-Snake-Game
   ```
3. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the game:
   ```bash
   python snake_game_desktop.py
   ```

## 📂 File Structure
* `snake_game_desktop.py`: The main game loop, input handling, and grid math.
* `icon_organizer.py`: A custom supporting module that prepares the desktop by aligning and organizing icons before the game starts.
* `requirements.txt`: Python package dependencies (primarily `pyautogui` and `keyboard`).

## 🏆 Winning the Game
The game ends if you hit the edge of the screen, run into your own tail, or press `ESC`. However, if you successfully eat all the target icons, you win. If your desktop has 24 or more icons, you will unlock a special automated desktop-icon arrangement at the end of the game!