import os
import time
import random
from typing import Tuple, List, Optional

import keyboard as kb
import pyautogui as pag

import grid_size
import icon_organizer as io
from physical_mouse_blocking import MouseBlocker

# ==============================================================================
# ======================== DESKTOP SNAKE GAME ==================================
# ==============================================================================

# --- Game Configuration & Grid Setup ---
window_size = pag.size()     # Current screen resolution
duration_drag = 0.3          # Mouse drag duration for moving icons
wd = 95                      # Initial cell width
ln = 130                     # Initial cell length
r = 8                        # Total grid rows
c = 20                       # Total grid columns
BORDER_PADDING = 25          # Padding from screen edges
EASTER_EGG_ICON_COUNT = 24   # Icon count to trigger Easter Egg
GAME_TICK = 0.3              # Fixed interval (in seconds) for each game frame

# Retrieve accurate spacing based on screen metrics
wd, ln, r, c = grid_size.get_true_desktop_spacing(window_size)

# --- Game State Variables ---
fruit: Optional[Tuple[int, int]] = None  # Coordinates of the active fruit
snake_body: List[Tuple[int, int]] = []  # Tracks (x, y) coordinates of every snake segment
on = True                    # Master flag for the main game loop
previous = 'right'           # Tracks the current movement direction
next_direction = None        # Queue for upcoming direction input
reason = ''                  # Descriptive reason for exiting the game

# ==============================================================================
# ======================== CORE FUNCTIONS ======================================
# ==============================================================================

def get_pixels(col: int, row: int) -> Tuple[int, int]:
    """Convert abstract grid coordinate to precise desktop screen pixel coordinates."""
    return int(wd/2) + col * wd, int(ln/2) + row * ln


def on_key_event(event) -> None:
    """
    Handle keyboard events for direction changes smoothly.
    Listens for arrow keys and ESC to update the movement queue.
    """
    global next_direction, on, previous, reason
    
    try:
        # Convert to string and lowercase to avoid CapsLock/Shift bugs
        key_name = str(event.name).lower()
        
        if event.event_type == 'down':
            if key_name == '8' and previous != 'down':
                next_direction = 'up'
            elif key_name == '4' and previous != 'right':
                next_direction = 'left'
            elif key_name == '5' and previous != 'up':
                next_direction = 'down'
            elif key_name == '6' and previous != 'left':
                next_direction = 'right'
            elif key_name == 'esc':
                reason = "ESC pressed - exiting! 🚪"
                on = False
    except Exception as e:
        print(f"⚠️ Error in on_key_event: {e}")


def fruit_transport(icon_col: int, icon_row: int) -> None:
    """
    Generates a new fruit by moving a target desktop icon to a random, 
    unoccupied grid coordinate.
    """
    global fruit, snake_body

    # Navigate to the target icon's original grid position
    start_x, start_y = get_pixels(icon_col, icon_row)
    pag.moveTo(start_x, start_y)
    time.sleep(0.1)
    
    while True:
        # Pick random column and row for the fruit purely in the PLAYABLE zone
        grid_col = random.randint(icon_col + 1, c-1) 
        grid_row = random.randint(0, r-1)
        
        # Check against existing snake body coordinates to avoid overlaps
        if (grid_col, grid_row) not in snake_body:
            break
            
    # Drag the icon to form the new fruit
    target_x, target_y = get_pixels(grid_col, grid_row)
    
    try:
        pag.mouseDown(button='left')
        pag.moveTo(target_x, target_y, duration=duration_drag)
    finally:
        pag.mouseUp(button='left')
        
    time.sleep(0.1)
    fruit = (grid_col, grid_row)



def fruit_eat(position: Tuple[int, int]) -> bool:
    """
    Validates if the snake's head perfectly aligns with the fruit on the grid.
    """
    global fruit
    if not fruit:
        return False
    return position == fruit


def snake_body_collission(position: Tuple[int, int]) -> bool:
    """
    Checks if the snake has collided with its own body segments on the grid.
    """
    return position in snake_body


def win(icon_count: int, snake_length: int) -> bool:
    """
    Determines if the winning condition is met.
    """
    return icon_count == snake_length


def win_mssg(i: int) -> Tuple[int, int]:
    """
    Coordinates to draw out a winning message ("W I N !") using desktop icons,
    positioned dynamically in the lower right corner of the desktop grid.
    """
    # Calculate starting offsets to position the message in the bottom right
    # The message spans 14 columns (0 to 13) and 4 rows (0 to 3)
    start_c = c - 14  
    start_r = r - 4  
    
    mssg = [
        # W
        (start_c+2, start_r), (start_c+2, start_r+1), (start_c+2, start_r+2), 
        (start_c+3, start_r+3), (start_c+4, start_r+2), (start_c+5, start_r+3), 
        (start_c+6, start_r+2), (start_c+6, start_r+1), (start_c+6, start_r), 
        # I
        (start_c+8, start_r), (start_c+8, start_r+1), (start_c+8, start_r+2), (start_c+8, start_r+3), 
        # N
        (start_c+10, start_r), (start_c+10, start_r+1), (start_c+10, start_r+2), (start_c+10, start_r+3), 
        (start_c+11, start_r+1), (start_c+12, start_r+2), 
        (start_c+13, start_r), (start_c+13, start_r+1), (start_c+13, start_r+2), (start_c+13, start_r+3), 
    ]
    return get_pixels(mssg[i][0], mssg[i][1])


# ==============================================================================
# ======================== MAIN GAME LOOP ======================================
# ==============================================================================

def main() -> None:
    global on, next_direction, previous, snake_body, reason
    mouse_blocker = None
    
    # ---------------------------
    # 1. Environment Initialization
    # ---------------------------
    try:
        print("🎮 Initializing Desktop Snake Game...")
        io.open_desktop()  # Ensure the desktop is in focus       
        time.sleep(0.2)
        
        # Take a snapshot of the original layout for backup safety
        timestamp = time.strftime("%H_%M_%S", time.localtime())
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"original_desktop_{timestamp}.png") 
        pag.screenshot(desktop_path)
        
        io.move_icons()     # Align icons neatly
        ic = int(io.scan_desktop('Desktop Snake Game')) 
        icon = ic
        
        if not (2 <= ic < int(r * c * 0.7)):
            print("❌ Invalid number of icons on the desktop. Exiting.")
            return
            
    except Exception as e:
        print(f"❌ Failed to initialize desktop environment: {e}")
        return

    # ---------------------------
    # 2. Starting Setup
    # ---------------------------
    
    icon_col = (icon-1) // r
    icon_row = (icon-1) % r

    # Move the very first fruit into play area
    fruit_transport(icon_col, icon_row) 
    icon -= 1 if icon > 0 else 0
    
    # Set the start coordinate of the snake head
    icon_col = (icon-1) // r
    icon_row = (icon-1) % r
    icon -= 1 if icon > 0 else 0
    
    pag.alert(text='🎮 Use 4-left, 6-right, 8-up, 5-down to move.\n🛑 Press ESC to exit.', title='Desktop Snake Game', button='OK')

    print("🛡️ Starting physical mouse blocking...")
    mouse_blocker = MouseBlocker()
    mouse_blocker.start()

    snake_body = [(icon_col, icon_row)]
    
    # Emulate the start by clicking at the root coordinate
    start_x, start_y = get_pixels(icon_col, icon_row)
    pag.click(start_x, start_y) 
    time.sleep(0.2)
    
    print("\n=========================================")
    print("🐍 Snake movement controls are ACTIVE! 🐍")
    print("   🕹️  Use arrow keys to move")
    print("   🚪  Press ESC to exit")
    print("=========================================\n")
    
    try:
        kb.on_press(on_key_event) # Listen for key events
    except Exception as e:
        print(f"❌ Error setting up keyboard listener: {e}")
        return
    
    # ---------------------------
    # 3. Execution Game Loop
    # ---------------------------
    try:
        while on:
            loop_start_time = time.time()
            # Update direction logically 
            if next_direction is not None:
                previous = next_direction
                next_direction = None
                
            # Compute new head coordinate
            head_col, head_row = snake_body[0]
            offsets = {
                'right': (1, 0),
                'left': (-1, 0),
                'down': (0, 1),
                'up': (0, -1)
            }
            
            dc, dr = offsets[previous]
            new_head_col = head_col + dc
            new_head_row = head_row + dr
            
            # --- Check Collision Rules ---
            
            pixel_x, pixel_y = get_pixels(new_head_col, new_head_row)
            
            # 1. Wall Hit Check
            out_of_bounds_x = not ((icon_col) * wd < pixel_x < (window_size[0] - BORDER_PADDING))
            out_of_bounds_y = not (BORDER_PADDING < pixel_y < (r * ln))
            if out_of_bounds_x or out_of_bounds_y:
                reason = "💥 Crash! The snake hit the desktop border - Game Over!"
                on = False
                break
            
            new_position = (new_head_col, new_head_row)
            
            # 2. Self Collision Check
            if snake_body_collission(new_position):
                reason = '💥 Ouch! The snake has entangled and eaten its own body!'
                on = False
                break

            # 3. Win Condition Check
            if win(ic, len(snake_body)):
                icon = ic
                # Secret easter egg execution if icons >= EASTER_EGG_ICON_COUNT
                if ic >= EASTER_EGG_ICON_COUNT:
                    io.move_icons()
                    for i in range(EASTER_EGG_ICON_COUNT):
                        win_icon_col = (icon-1) // r
                        win_icon_row = (icon-1) % r
                        
                        target_x, target_y = get_pixels(win_icon_col, win_icon_row)
                        
                        pag.moveTo(target_x, target_y)
                        time.sleep(0.2)
                        
                        try:
                            pag.mouseDown(button='left') 
                            final_x, final_y = win_mssg(i)
                            pag.moveTo(final_x, final_y, duration=duration_drag)
                        finally:
                            pag.mouseUp(button='left')
                        
                        icon -= 1 if icon > 0 else 0
                reason = '🏆 VICTORY! You Have Won The Game!'
                on = False
                break
            
            # --- Move & Consume ---
            
            if fruit_eat(new_position):
                # Consume fruit & Grow!
                snake_body.insert(0, new_position)
                
                # Setup Next Fruit
                icon_col = (icon-1) // r
                icon_row = (icon-1) % r
                fruit_transport(icon_col, icon_row)
                icon -= 1 if icon > 0 else 0
                
                # Orient crosshairs back to the snake head
                pag.moveTo(pixel_x, pixel_y)
                print(f"🍎 Yum! +1 Score. Length: {len(snake_body)} | Remaining Icons: {icon}")
            
            else:
                # Ordinary movement (Shift tail to new head pos)
                tail_col, tail_row = snake_body[-1]
                tail_x, tail_y = get_pixels(tail_col, tail_row)
                
                pag.moveTo(tail_x, tail_y)
                time.sleep(0.1)
                
                # Visual effect of sliding the icon on desk
                try:
                    pag.mouseDown(button='left') 
                    pag.moveTo(pixel_x, pixel_y, duration=duration_drag)
                finally:
                    pag.mouseUp(button='left')  
                              
                # Logical body adjustment
                snake_body.insert(0, new_position)
                snake_body.pop() # Evict trailing tail pixel

            elapsed = time.time() - loop_start_time
            if elapsed < GAME_TICK:
                time.sleep(GAME_TICK - elapsed)
            
    except KeyboardInterrupt:
        on = False
        print("\n🛑 Force Exiting snake control...")
    except Exception as e:
        print(f"⚠️ Error encountered during execution loop: {e}")
        
    # ---------------------------
    # 4. Graceful Cleanup
    # ---------------------------
    finally:
        if mouse_blocker:
            print("🛡️ Restoring physical mouse...")
            mouse_blocker.stop()
        try:
            kb.remove_all_hotkeys()
            final_score = len(snake_body) - 1
            max_score = ic
            
            print("\n=========================================")
            print(f"🎯 Final Score: {final_score}/{max_score} Icons eaten")
            print(f"📝 Reason: {reason}")
            print("=========================================\n")
            
            if win(ic, len(snake_body)):
                pag.alert(text='🏆 Congratulations! You have consumed all the icons on your desktop!', title='Desktop Snake Game', button='OK')
                pag.click(1, 1)
                pag.hotkey('ctrl', 'a')
            else:
                msg = f"{reason}\nFinal Score: {final_score}/{max_score}"
                pag.alert(text=msg, title='Desktop Snake Game', button='OK')
            
                # Standardize arrangement before abandoning UI
                io.open_desktop()
                io.move_icons()
        except Exception as e:
            print(f"Cleanup non-fatal error: {e}")

if __name__ == "__main__":
    main()
