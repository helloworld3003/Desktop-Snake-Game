
# <img width="50" height="50"  align="left" alt="icon" src="https://github.com/user-attachments/assets/49c3d638-2334-4f03-99ed-1896ac9ef359" /> Desktop Snake Game
Welcome to **Desktop Snake Game**! This is a **custom made, highly experimental** game that transforms your boring Windows desktop into a fully playable game of Snake. 

Instead of a traditional windowed game, this script uses **PyAutoGUI** to physically drag your actual desktop shortcuts around the screen! Your Desktop icons *are* the snake! 




---

## 🚀 Quick Overview

**Desktop Snake Game** takes control of your Windows desktop to play Snake using your shortcuts. 

- **The Snake:** Made entirely of your desktop shortcuts and icons!
- **The Gameplay:** Use `W, A, S, D` or `Arrow Keys` to slither around the desktop grid and "eat" other icons to grow longer. Use `esc` to exit the game, `p` to pause and `m` to mute.
- **The Magic:** We use `pyautogui` to rapidly physically drag icons across the screen. 
- **The Safety:** Before any chaos begins, the game automatically takes a screenshot and **saves your precise desktop layout**. When you finish/quit, it automatically arranges everything back to your original layout. No icons lost!
- **The UI:** A beautiful, custom-made `HUD overlay` that displays your current score, remaining icons, a glowing fruit box, and a "Ready-Set-Go!" countdown.
- **The Sound:** A custom-made sound system that `plays sound effects` for eating fruits, growing longer, and winning the game.

---
## Gameplay(v1.0.3)
https://github.com/user-attachments/assets/6516ae1b-2b29-497d-8e8d-ff5a626f769c

## 🧠 Detailed Breakdown

If you're curious about how this wizardry works under the hood, here is the detailed breakdown of the components:

### 1. The Core Engine (`snake_game_desktop.py` & `grid_size.py`)
This is the heart of the game. It controls the game loop, snake mechanics (movement, collisions, and eating), and keyboard listeners. 
- **Grid Calculation (`grid_size.py`):** Automatically detects your screen resolution to calculate the perfect grid spacing so the icons snap perfectly as they move.
- **Physical Dragging:** The game physically selects an icon and uses `pyautogui.moveTo()` with a calculated drag duration to slide it across your wallpaper to its new position.

### 2. Desktop Organization & Safety (`icon_organizer.py`)
Moving users' icons is dangerous, so this module ensures safety.
- **Auto-Save Layout:** Uses Windows APIs (`win32gui`) to read the exact `(x, y)` coordinate of every shortcut *before* the game starts. 
- **Auto-Restore Layout:** When the game ends (win, lose, or quit), restoring your shortcuts to their exact starting pixels. 

### 3. Attractive UI & Hud (`hud_overlay.py` & `leaderboard_ui.py`)
Who says a desktop game can't look incredibly polished? 
- **HUD Overlay:** A transparent, click-through overlay built in Tkinter that draws the game boundary wall, displays your current score, remaining icons, a glowing icon box, and a "Ready-Set-Go!" countdown.
- **Leaderboards:** A gorgeous custom Tkinter UI that pops up post-game to show your high scores, tracking the longest snake you've ever built!

### 4. Input Blocking (`physical_mouse_blocking.py` & `mouse_hide.py`)
- To prevent you from accidentally clicking and breaking the dragging events, we employ Windows Hooks to block physical mouse movements during gameplay, and entirely hide the cursor from the screen for total immersion.

### 5. Sound System (`sounds` folder)
- A custom-made sound system that plays sound effects for eating fruits, growing longer, and winning the game.

### 🎁 The Secret Easter Egg!
If you are skilled enough to manage to eat a massive amount of your icons (at least 23 icons!), you might even trigger a **custom pixel-art Easter egg!** The game will use your icons to draw out a massive "WIN!" message directly on your wallpaper. 

---

## 🎮 Play and Test It!

I highly encourage you to pull this repository and give it a try on your PC!
1. Ensure you have a good handful of desktop icons and shortcuts (at least 5-10) lying around.
2. Download the latest release `snake_game_desktop.exe` from the [Releases](https://github.com/helloworld3003/Desktop-Snake-Game/releases) page.
3. Run `snake_game_desktop.exe`
4. Choose your difficulty and watch your icons come to life! 

**Let me know how it goes!** I am looking for playtesters to see how well it works on different monitor resolutions and scaling factors. 

---

## 🛠️ Suggest Features & Improvements

Since this is highly experimental, there's always room to grow! If you have any feedback or ideas, please open an Issue or a Pull Request! 
Some ideas for the future:
- **Obstacles:** Designate some apps/files (like the Recycle Bin) as "bombs" that you have to avoid.
- **Multi-monitor support:** Slither your app icons from one screen to the next!
- **Mac/Linux Ports:** Currently relies on Win32 UI APIs. Help me bring it to macOS and Linux!

---

### ⭐ Give It a Star!
If you found this project cool, funny, or technically interesting, **please consider leaving a ⭐️ on the repository!** It helps a ton and motivates me to keep building crazy stuff like this. Happy slithering! 🐍


#### Tapomoy Sarkar - [helloworld3003](https://github.com/helloworld3003)

## 🚀 Latest Updates
v1.0.1 - March 3, 2026<br>
* The game engine has been completely overhauled to remove all hardcoded constraints, replacing fixed values with dynamic variables.
* The grid math now automatically scales to flawlessly match any screen resolution and Windows DPI setting.
* Alongside these structural upgrades, the core codebase and terminal outputs have been polished and decorated for a cleaner, more intuitive experience.

v1.0.2 - March 11, 2026
* Grid-Based Architecture<br>
       Coord Translation: Added `get_pixels(col, row)` to dynamically map grid positions to absolute screen pixels.<br>
       Grid Migration: Switched from volatile pixel calculations to a stable `(col, row)` grid system.
* Physical Mouse Blocking Engine<br>
       New Feature: Added `physical_mouse_blocking.py` (via `ctypes` Windows hooks) to stop physical mouse interference during gameplay.<br>
       Smart Whitelist: Allows `PyAutoGUI` injected commands to pass through unhindered.<br>
       Stability Fixes: Resolved 64-bit `OverflowError` crashes and guaranteed mouse restoration on game exit/crash.
* Icon & Drag Refinements<br>
       Math Safety: Prevented negative index bounds at game end (`icon -= 1 if icon > 0 else 0`).
* Gameplay Enhancements<br>
       Collision Safety: Fruits now safely spawn only on empty grid spaces, avoiding snake body overlaps.<br>
       Simplified Checks: Wall and self-collision detection now use lightning-fast list checks instead of pixel boundaries.<br>
       Control Scheme: Updated directional movement bindings from generic arrow keys to the numpad (4, 5, 6, 8) for improved accessibility.<br>
       Dynamic Animations: Centered the "W I N" endgame desktop icon message cleanly in the bottom-right corner.

v1.0.3 - March 18, 2026<br>
* Highscore & Persistence: Added a `persistent highscore system` and automatic desktop snapshots, all stored in a dedicated folder: Desktop/snake_game_desktop/.<br>
* Standardized Controls: Reverted movement keys from experimental mappings back to the standard `Arrow Keys` for a more intuitive experience.<br>
* Enhanced Audio: Integrated `custom sound effects (asynchronous .wav files)` and successfully suppressed annoying Windows "exclamation" dings.<br>
* Cursor Protection: Implemented `cursor hiding mechanism` for seamless gameplay(Cursor is hidden during gameplay and restored when the game is exited). 

v1.0.4 - March 21, 2026 <br>
* Added Automatic Icon Restore
* Make it very fast and unfailing
* Working flawlessly

v1.0.5 - March 28, 2026 <br>
* Added a transparent display to show score, mute/paused status.
* Added animation for fruits, and boundary wall.
* Updated the Message boxes, added Play again and leaderboard reset options.
