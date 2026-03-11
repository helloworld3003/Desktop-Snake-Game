# 🐍 Desktop Snake Game

A highly experimental, Python-based Snake game that literally uses your Windows desktop icons as the snake! Eat icons to grow longer, and navigate your desktop grid to win. 

Instead of drawing pixels on a canvas, this script uses `pyautogui` to physically drag your desktop shortcuts around the screen. If you manage to eat enough icons, you might even trigger a custom pixel-art Easter egg!

**Gameplay**

https://github.com/user-attachments/assets/174f84a1-ccaf-4fec-8917-75a5817e8738


**📸 Peace of Mind Feature:** Don't worry about losing your carefully arranged desktop layout! Before the game auto-arranges anything, it automatically takes a screenshot of your screen and saves it right to your Desktop as `orignal_desktop_time.png` so you can easily restore your layout later.


## ⚠️ Assumptions & Requirements
Because this game interacts directly with your OS GUI, it requires a specific environment to run correctly:
* **Operating System:** Windows 
* **Display Resolution:** Any(Automatically detects and adjusts)
* **Icon Settings:** Medium Icons, Auto-arrange disabled during gameplay, Align to grid.
* **Settings:** "Drag to share" or "Single-click to open an item" must be turned OFF in Windows settings. Rainmeter is not running.

## 🎮 How to Play (For Gamers)
If you just want to play the game without messing with Python code:
1. Navigate to the **[Releases](#)** tab on the right side of this GitHub page.
2. Download the latest `snake_game_desktop.exe` file.
3. Double-click the `.exe` to launch.
4. **Controls:** Use 4-left, 6-right, 8-up, 5-down to move.\n🛑 Press ESC to exit.

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

## 🤝 Feedback & Contributions Wanted!

Because this game physically drags your desktop icons and relies on specific OS interactions, it is highly experimental. Every computer setup is a little different, so I would love your help testing it out and improving it!

**🎮 For Players & Testers:**
* **Play the game:** Download the `.exe` from the Releases tab and give it a try.
* **Report Bugs:** Did the snake glitch near the taskbar? Did it accidentally open an app while dragging? If something breaks, please open an **Issue** on this repository. Let me know your screen resolution and Windows version!
* **Suggest Features:** Have a cool idea for a new feature or a different pixel-art win screen? Let me know in the Issues tab.

**💻 For Developers:**
* **Review & Optimize:** Feel free to fork this repository! If you can improve the `pyautogui` dragging efficiency, make the `fruit_transport` logic faster, or optimize the `icon_organizer.py`, your pull requests are welcome.
* **Expand Compatibility:** Currently, the grid math is heavily optimized for a 1920x1080 display. If you can help make the grid calculations dynamically scale to any monitor resolution, that would be a massive improvement. 

To contribute code, simply fork the repo, create a new branch for your feature or bug fix, and submit a Pull Request (PR)!

### 🚀 Latest Updates
v1.0.1 - March 3, 2026
The game engine has been completely overhauled to remove all hardcoded constraints, replacing fixed values with dynamic variables. The grid math now automatically scales to flawlessly match any screen resolution and Windows DPI setting. This is powered by a newly added `grid_size.py` utility, which directly queries the hidden Windows `SysListView32` to extract your true physical desktop rendering metrics. Alongside these structural upgrades, the core codebase and terminal outputs have been polished and decorated for a cleaner, more intuitive experience.

v1.0.2 - March 11, 2026
* **1. Grid-Based Architecture**<br>
       Coord Translation: Added `get_pixels(col, row)` to dynamically map grid positions to absolute screen pixels.<br>
       Grid Migration: Switched from volatile pixel calculations to a stable `(col, row)` grid system.
* **2. Physical Mouse Blocking Engine**<br>
       New Feature: Added `physical_mouse_blocking.py` (via `ctypes` Windows hooks) to stop physical mouse interference during gameplay.<br>
       Smart Whitelist: Allows `PyAutoGUI` injected commands to pass through unhindered.<br>
       Stability Fixes: Resolved 64-bit `OverflowError` crashes and guaranteed mouse restoration on game exit/crash.
* **3. Icon & Drag Refinements**<br>
       Math Safety: Prevented negative index bounds at game end (`icon -= 1 if icon > 0 else 0`).
* **4. Gameplay Enhancements**<br>
       Collision Safety: Fruits now safely spawn only on empty grid spaces, avoiding snake body overlaps.<br>
       Simplified Checks: Wall and self-collision detection now use lightning-fast list checks instead of pixel boundaries.<br>
       Control Scheme: Updated directional movement bindings from generic arrow keys to the numpad (4, 5, 6, 8) for improved accessibility.<br>
       Dynamic Animations: Centered the "W I N" endgame desktop icon message cleanly in the bottom-right corner.









