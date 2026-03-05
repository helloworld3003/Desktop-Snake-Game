import os
import time
import random
from typing import Tuple, List

import keyboard as kb
import pyautogui as pag

import grid_size
import icon_organizer as io

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

# Retrieve accurate spacing based on screen metrics
wd, ln, r, c = grid_size.get_true_desktop_spacing(window_size)

# --- Game State Variables ---
fruit: List[int] = []        # Coordinates of the active fruit
snake_body: List[Tuple[int, int]] = []  # Tracks (x, y) coordinates of every snake segment
on = True                    # Master flag for the main game loop
previous = 'right'           # Tracks the current movement direction
next_direction = None        # Queue for upcoming direction input
reason = ''                  # Descriptive reason for exiting the game

# ==============================================================================
# ======================== CORE FUNCTIONS ======================================
# ==============================================================================

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
            if key_name == 'up' and previous != 'down':
                next_direction = 'up'
            elif key_name == 'left' and previous != 'right':
                next_direction = 'left'
            elif key_name == 'down' and previous != 'up':
                next_direction = 'down'
            elif key_name == 'right' and previous != 'left':
                next_direction = 'right'
            elif key_name == 'esc':
                reason = "ESC pressed - exiting! 🚪"
                on = False
    except Exception as e:
        print(f"⚠️ Error in on_key_event: {e}")


def fruit_transport(row: int, col: int) -> None:
    """
    Generates a new fruit by moving a target desktop icon to a random, 
    unoccupied grid coordinate.
    """
    global fruit, snake_body

    # Navigate to the target icon's original grid position
    start_x = int(wd/2) + (col-1) * wd
    start_y = int(ln/2) + (row-1) * ln
    pag.moveTo(start_x, start_y)
    
    while True:
        is_valid_position = True
        
        # Pick random column and row for the fruit
        grid_col = random.randint(col, c-1) 
        grid_row = random.randint(0, r-1)
        
        # Calculate actual screen coordinates
        target_x = int(wd/2) + grid_col * wd
        target_y = int(ln/2) + grid_row * ln
        
        # Check against existing snake body coordinates to avoid overlaps
        for positions in snake_body:
            dx = abs(target_x - positions[0])
            dy = abs(target_y - positions[1])
            
            # Using original proximity logic
            if ((dx < wd and dy < 50) or (dx < 50 and dy < ln)):
                is_valid_position = False
                break
                
        if is_valid_position:
            break
            
    # Drag the icon to form the new fruit
    pag.dragTo(target_x, target_y, duration=duration_drag)
    fruit = pag.position()


def fruit_eat(direction: str, position: Tuple[int, int]) -> bool:
    """
    Validates if the snake's head is hovering sufficiently close to eat the fruit.
    """
    global fruit
    if not fruit:
        return False
        
    dx = abs(fruit[0] - position[0])
    dy = abs(fruit[1] - position[1])
    
    # Proximity hit-box logic based on direction
    if (dx < wd and dy < 50 and direction in ['left', 'right']) or \
       (dx < 50 and dy < ln and direction in ['up', 'down']):
        return True    
    return False


def snake_body_collission(currentx: int, currenty: int) -> bool:
    """
    Checks if the snake has collided with its own body segments.
    """
    for positions in snake_body:
        dx = abs(currentx - positions[0])
        dy = abs(currenty - positions[1])
        
        # Precision hit-box check to confirm collision
        if ((dx < wd and dy < int(ln/2)) or (dx < int(wd/2) and dy < ln)):
            return True
            
    return False


def win(icon_count: int, snake_length: int) -> bool:
    """
    Determines if the winning condition is met.
    """
    return icon_count == snake_length


def win_mssg(i: int) -> Tuple[int, int]:
    """
    Coordinates to draw out a winning message using desktop icons!
    """
    mssg = [
        (6, 4), (6, 5), (6, 6), (7, 7), (8, 6), (9, 7), (10, 6), (10, 5), (10, 4), 
        (13, 4), (13, 5), (13, 6), (13, 7), 
        (16, 4), (16, 5), (16, 6), (16, 7), (17, 5), (18, 6), (19, 4), (19, 5), (19, 6), (19, 7), 
        (13, 3)
    ]
    x = int(wd/2) + mssg[i][0] * wd
    y = int(ln/2) + mssg[i][1] * ln
    return (x, y)


# ==============================================================================
# ======================== MAIN GAME LOOP ======================================
# ==============================================================================

def main() -> None:
    global on, next_direction, previous, snake_body, reason
    
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
    column = ((icon-1) // r) + 1
    row = icon % r if icon % r != 0 else r

    # Move the very first fruit into play area
    fruit_transport(row, column) 
    icon -= 1 
    
    # Set the start coordinate of the snake head
    column = ((icon-1) // r) + 1
    row = icon % r if icon % r != 0 else r
    icon -= 1
    
    pag.alert(text='🎮 Use arrow keys to move.\n🛑 Press ESC to exit.', title='Desktop Snake Game', button='OK')

    start_x = int(wd/2) + (column-1) * wd
    start_y = int(ln/2) + (row-1) * ln
    snake_body = [(start_x, start_y)]
    
    # Emulate the start by clicking at the root coordinate
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
            # Update direction logically 
            if next_direction is not None:
                previous = next_direction
                next_direction = None
                
            # Compute new head coordinate
            head_x, head_y = snake_body[0]
            offsets = {
                'right': (wd, 0),
                'left': (-wd, 0),
                'down': (0, ln),
                'up': (0, -ln)
            }
            
            dx, dy = offsets[previous]
            new_head_x = head_x + dx
            new_head_y = head_y + dy
            
            # --- Check Collision Rules ---
            
            # 1. Wall Hit Check
            out_of_bounds_x = not (column * wd < new_head_x < (window_size[0] - 25))
            out_of_bounds_y = not (25 < new_head_y < (r * ln))
            if out_of_bounds_x or out_of_bounds_y:
                reason = "💥 Crash! The snake hit the desktop border - Game Over!"
                on = False
                break
            
            # 2. Self Collision Check
            if snake_body_collission(new_head_x, new_head_y):
                reason = '💥 Ouch! The snake has entangled and eaten its own body!'
                on = False
                break

            # 3. Win Condition Check
            if win(ic, len(snake_body)):
                icon = ic
                # Secret easter egg execution if icons >= 24
                if ic >= 24:
                    io.move_icons()
                    for i in range(24):
                        column = ((icon-1) // r) + 1
                        row = icon % r if icon % r != 0 else r
                        
                        target_x = int(wd/2) + (column-1) * wd
                        target_y = int(ln/2) + (row-1) * ln
                        
                        pag.moveTo(target_x, target_y)
                        time.sleep(0.2)
                        
                        pag.mouseDown(button='left') 
                        final_x, final_y = win_mssg(i)
                        pag.moveTo(final_x, final_y, duration=duration_drag)
                        pag.mouseUp(button='left')
                        
                        icon -= 1
                reason = '🏆 VICTORY! You Have Won The Game!'
                on = False
                break
            
            # --- Move & Consume ---
            
            new_position = (new_head_x, new_head_y)
            
            if fruit_eat(previous, new_position):
                # Consume fruit & Grow!
                snake_body.insert(0, new_position)
                
                # Setup Next Fruit
                column = ((icon-1) // r) + 1
                row = icon % r if icon % r != 0 else r
                fruit_transport(row, column)
                icon -= 1 
                
                # Orient crosshairs back to the snake head
                pag.moveTo(new_head_x, new_head_y)
                print(f"🍎 Yum! +1 Score. Length: {len(snake_body)} | Remaining Icons: {icon}")
            
            else:
                # Ordinary movement (Shift tail to new head pos)
                tail_x, tail_y = snake_body[-1]
                
                pag.moveTo(tail_x, tail_y)
                time.sleep(0.1)
                
                # Visual effect of sliding the icon on desk
                pag.mouseDown(button='left') 
                pag.moveTo(new_head_x, new_head_y, duration=duration_drag)
                pag.mouseUp(button='left')  
                              
                # Logical body adjustment
                snake_body.insert(0, new_position)
                snake_body.pop() # Evict trailing tail pixel

            time.sleep(0.2)
            
    except KeyboardInterrupt:
        on = False
        print("\n🛑 Force Exiting snake control...")
    except Exception as e:
        print(f"⚠️ Error encountered during execution loop: {e}")
        
    # ---------------------------
    # 4. Graceful Cleanup
    # ---------------------------
    finally:
        try:
            kb.remove_all_hotkeys()
            final_score = len(snake_body) - 1
            max_score = len(snake_body) + icon
            
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
