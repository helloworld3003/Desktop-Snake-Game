## Desktop Snake Game - Complete Game Flow Architecture
Complete architectural trace of the Desktop Snake Game showing how it transforms Windows desktop icons into a playable Snake game. Covers initialization [1a-1e], dynamic grid detection [2a-2d], input control systems [3a-3e], HUD overlay communication [4a-4d], core game physics [5a-5e], fruit mechanics [6a-6e], victory conditions [7a-7e], and safe cleanup [8a-8e].
### 1. Game Initialization & Desktop Safety Setup
How the game prepares the desktop environment and ensures icon safety before gameplay begins
### 1a. Focus Desktop (`snake_game_desktop.py:280`)
Brings desktop to foreground using Win+D hotkey
```text
io.open_desktop()  # Ensure the desktop is in focus
```
### 1b. Backup Screenshot (`snake_game_desktop.py:287`)
Takes visual backup of desktop state
```text
pag.screenshot(desktop_path)
```
### 1c. Save Icon Positions (`snake_game_desktop.py:290`)
Captures exact (x,y) coordinates of all desktop icons
```text
my_layout = io.save_layout()
```
### 1d. Access Explorer Memory (`icon_organizer.py:72`)
Opens explorer.exe process to read icon positions via shared memory
```text
hProcess = ctypes.windll.kernel32.OpenProcess
```
### 1e. Read Icon Coordinates (`icon_organizer.py:85`)
Queries Windows for each icon's exact pixel position
```text
win32gui.SendMessage(hwnd, LVM_GETITEMPOSITION, i, pMem)
```
### 2. Dynamic Grid Detection & Screen Resolution Adaptation
How the game automatically adapts to any screen resolution and DPI scaling
### 2a. Query Desktop Grid (`snake_game_desktop.py:40`)
Gets actual icon spacing from Windows API
```text
wd, ln, r, c = grid_size.get_true_desktop_spacing(window_size)
```
### 2b. Find Desktop ListView (`grid_size.py:18`)
Locates the Windows desktop icon grid window
```text
desktop_handle = user32.FindWindowExW(shell_def_view, 0, "SysListView32", None)
```
### 2c. Get Icon Spacing (`grid_size.py:40`)
Retrieves pixel spacing between desktop icons
```text
result = user32.SendMessageW(desktop_handle, LVM_GETITEMSPACING, 0, 0)
```
### 2d. Parse Dimensions (`grid_size.py:43`)
Extracts width/height from packed 32-bit Windows API result
```text
grid_width = result & 0xFFFF
grid_height = (result >> 16) & 0xFFFF
```
### 3. Input Control & Physical Mouse Blocking System
How the game blocks physical input while allowing scripted icon movements
### 3a. Start Mouse Blocker (`snake_game_desktop.py:340`)
Activates global mouse hook in background thread
```text
mouse_blocker = MouseBlocker()
mouse_blocker.start()
```
### 3b. Install Global Hook (`physical_mouse_blocking.py:55`)
Installs low-level mouse hook system-wide
```text
self.hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, self.pointer, None, 0)
```
### 3c. Detect Injected Input (`physical_mouse_blocking.py:47`)
Distinguishes between physical and scripted mouse events
```text
is_injected = (hook_struct.flags & LLMHF_INJECTED) or (hook_struct.flags & LLMHF_LOWER_IL_INJECTED)
```
### 3d. Block Physical Mouse (`physical_mouse_blocking.py:48`)
Prevents real mouse clicks from interfering
```text
if not is_injected:
    return 1 # Block physical interaction!
```
### 3e. Hide System Cursor (`snake_game_desktop.py:342`)
Replaces cursor with transparent version
```text
mouse_hide.hide_cursor() # Hide the cursor
```
### 4. HUD Overlay Thread-Safe Communication System
How the transparent UI overlay communicates with the main game thread
### 4a. Create Overlay (`snake_game_desktop.py:309`)
Instantiates thread-safe HUD system
```text
overlay = GameOverlay()
```
### 4b. Queue Score Update (`hud_overlay.py:17`)
Sends score data to UI thread via queue
```text
self.cmd_queue.put(('score', (score, max_score, length, icons_left)))
```
### 4c. Make Click-Through (`hud_overlay.py:56`)
Sets window to be transparent to mouse clicks
```text
style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT
```
### 4d. Process Commands (`hud_overlay.py:81`)
UI thread processes queued updates from game logic
```text
cmd, data = self.cmd_queue.get_nowait()
```
### 5. Core Game Loop & Snake Movement Physics
The main game loop that handles snake movement, collision detection, and icon dragging
### 5a. Hook Keyboard Input (`snake_game_desktop.py:372`)
Captures direction keys while suppressing Windows sounds
```text
kb.hook(on_key_event, suppress=True)
```
### 5b. Calculate New Position (`snake_game_desktop.py:408`)
Computes next head position based on direction
```text
new_head_col = head_col + dc
new_head_row = head_row + dr
```
### 5c. Drag Icon Physically (`snake_game_desktop.py:503`)
Uses PyAutoGUI to drag desktop icon to new position
```text
pag.mouseDown(button='left') 
pag.moveTo(pixel_x, pixel_y, duration=duration_drag)
```
### 5d. Update Snake Body (`snake_game_desktop.py:509`)
Adds new head and removes tail for movement
```text
snake_body.insert(0, new_position)
snake_body.pop() # Evict trailing tail pixel
```
### 5e. Check Self Collision (`snake_game_desktop.py:428`)
Detects if snake hits itself
```text
if snake_body_collission(new_position):
```
### 6. Fruit System & Eating Mechanics
How fruits are spawned, moved, and consumed by the snake
### 6a. Spawn First Fruit (`snake_game_desktop.py:326`)
Moves first icon to become initial fruit
```text
fruit_transport(icon_col, icon_row)
```
### 6b. Drag Fruit Icon (`snake_game_desktop.py:203`)
Physically drags icon to fruit position
```text
pag.mouseDown(button='left')
pag.moveTo(target_x, target_y, duration=duration_drag)
```
### 6c. Check Fruit Collision (`snake_game_desktop.py:473`)
Detects when snake head reaches fruit
```text
if fruit_eat(new_position):
```
### 6d. Grow Snake (`snake_game_desktop.py:476`)
Adds new head without removing tail for growth
```text
snake_body.insert(0, new_position)
```
### 6e. Update Fruit Glow (`snake_game_desktop.py:211`)
Tells HUD to highlight new fruit position
```text
overlay.update_fruit_position(target_x, target_y, wd, ln)
```
### 7. Victory Conditions & Easter Egg Animation
Win condition detection and the special icon art animation
### 7a. Check Win Condition (`snake_game_desktop.py:435`)
Detects when all icons have been eaten
```text
if win(ic, len(snake_body)):
```
### 7b. Trigger Easter Egg (`snake_game_desktop.py:440`)
Checks if enough icons for special animation
```text
if ic >= EASTER_EGG_ICON_COUNT:
```
### 7c. Start Victory Animation (`snake_game_desktop.py:442`)
Triggers confetti and VICTORY text
```text
overlay.play_easter_egg_animation()
```
### 7d. Draw WIN Message (`snake_game_desktop.py:462`)
Arranges icons to spell W I N on desktop
```text
final_x, final_y = win_mssg(i)
pag.moveTo(final_x, final_y, duration=duration_drag)
```
### 7e. Create Confetti (`hud_overlay.py:128`)
Generates 200 falling colored particles
```text
self.confetti_items.append({"id": item, "dx": dx, "dy": dy})
```
### 8. Game Cleanup & Desktop Restoration
How the game safely restores the desktop and saves scores after ending
### 8a. Remove Keyboard Hook (`snake_game_desktop.py:529`)
Critical cleanup to restore keyboard functionality
```text
kb.unhook_all()
```
### 8b. Restore Mouse Control (`snake_game_desktop.py:533`)
Removes mouse block and shows cursor
```text
mouse_blocker.stop()
mouse_hide.show_cursor() # Show the cursor
```
### 8c. Save High Score (`snake_game_desktop.py:550`)
Persists score to JSON leaderboard file
```text
updated_scores = save_score(final_score, max_score, difficulty, won)
```
### 8d. Restore Icon Layout (`snake_game_desktop.py:560`)
Moves all icons back to original positions
```text
io.restore_layout(my_layout)
```
### 8e. Move Icon Back (`icon_organizer.py:116`)
Uses Windows API to restore each icon position
```text
win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, item["index"], lparam)
```



