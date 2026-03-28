from winsound import Beep
import os
import sys
import json
import time
import random
import winsound
import datetime
from typing import Tuple, List, Optional

import keyboard as kb
import pyautogui as pag

import grid_size
import icon_organizer as io
from physical_mouse_blocking import MouseBlocker
import mouse_hide

from hud_overlay import GameOverlay
from leaderboard_ui import show_visual_leaderboard

# ==============================================================================
# ======================== DESKTOP SNAKE GAME ==================================
# ==============================================================================

overlay = None

# --- Game Configuration & Grid Setup ---
window_size = pag.size()     # Current screen resolution
duration_drag = 0.2          # Mouse drag duration for moving icons
wd = 95                      # Initial cell width
ln = 130                     # Initial cell length
r = 8                        # Total grid rows
c = 20                       # Total grid columns
BORDER_PADDING = 25          # Padding from screen edges
EASTER_EGG_ICON_COUNT = 23   # Icon count to trigger Easter Egg
GAME_TICK = duration_drag              # Fixed interval (in seconds) for each game frame

# Retrieve accurate spacing based on screen metrics
wd, ln, r, c = grid_size.get_true_desktop_spacing(window_size)
BORDER_PADDING = int(((wd+ln)/2)*0.2)         # Padding from screen edges

# --- Game State Variables ---
fruit: Optional[Tuple[int, int]] = None  # Coordinates of the active fruit
snake_body: List[Tuple[int, int]] = []  # Tracks (x, y) coordinates of every snake segment
on = True                    # Master flag for the main game loop
previous = 'right'           # Tracks the current movement direction
next_direction = None        # Queue for upcoming direction input
reason = ''                  # Descriptive reason for exiting the game
paused = False               # Flag for pausing the game
mute = False                 # Flag for muting the game
# ==============================================================================
# ======================== HIGH SCORE SYSTEM ===================================
# ==============================================================================

HIGH_SCORE_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "snake_game_desktop", "high_scores.json")
MAX_LEADERBOARD_ENTRIES = 5

def load_scores() -> list:
    """Load high scores from JSON file. Returns a list of score dicts."""
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_score(score: int, max_score: int, difficulty: str, won: bool) -> list:
    """
    Append a new score entry, sort descending, keep top MAX_LEADERBOARD_ENTRIES,
    persist to disk and return the updated leaderboard.
    """
    difficulty_score={'easy':5,'medium':10,'hard':20}
    # pct=round((score*max_score * difficulty_score[difficulty]*100)/((r*c*0.7)**2*difficulty_score['hard'])) if max_score else 0
    diff_val = difficulty_score.get(difficulty, 5)
    pct = round((score / max_score) * 100 * (diff_val / difficulty_score['hard'])) if max_score else 0
    scores = load_scores()
    entry = {
        'score': score,
        'max': max_score,
        'pct': pct if not won else pct+20 ,
        'difficulty': difficulty,
        'won': won,
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    scores.append(entry)
    scores.sort(key=lambda e: (e['pct'], e['score']), reverse=True)
    scores = scores[:MAX_LEADERBOARD_ENTRIES]
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=2)
    except Exception as ex:
        print(f'⚠️ Could not save high score: {ex}')
    return scores

def format_leaderboard(scores: list, highlight_score: int) -> str:
    """Return a human-readable leaderboard string for display in a dialog."""
    if not scores:
        return 'No scores recorded yet.'
    lines = ['🏆  TOP SCORES  🏆', '-' * 36]
    medals = ['🥇', '🥈', '🥉']
    for i, e in enumerate(scores):
        medal = medals[i] if i < 3 else f' {i+1}.'
        crown = ' ◀ YOU' if e['score'] == highlight_score and i == next(
            (j for j, s in enumerate(scores) if s['score'] == highlight_score), -1) else ''
        won_tag = ' 🏆' if e['won'] else ''
        lines.append(
            f"{medal} {e['score']:>3}/{e['max']:<3} ({e['pct']:>3}%)  "
            f"{e['difficulty']:<6}  {e['date']}{won_tag}{crown}"
        )
    return '\n'.join(lines)

# ==============================================================================
# ======================== CORE FUNCTIONS ======================================
# ==============================================================================
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def sound(path: str):
    """Play a sound effect when the snake eats a fruit."""
    if mute:
        return
    sound_file = resource_path(f'sounds\\{path}')
    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
def get_pixels(col: int, row: int) -> Tuple[int, int]:
    """Convert abstract grid coordinate to precise desktop screen pixel coordinates."""
    return int(wd/2) + col * wd, int(ln/2) + row * ln


def on_key_event(event) -> None:
    """
    Handle keyboard events for direction changes smoothly.
    Listens for arrow keys and ESC to update the movement queue.
    """
    global next_direction, on, previous, reason, paused, mute
    
    try:
        # Convert to string and lowercase to avoid CapsLock/Shift bugs
        key_name = str(event.name).lower()
        
        if event.event_type == 'down':
            if (key_name == 'up' or key_name == 'w') and previous != 'down':
                next_direction = 'up'
                sound('keyboard_click.wav')
            elif (key_name == 'left' or key_name == 'a') and previous != 'right':
                next_direction = 'left'
                sound('keyboard_click.wav')
            elif (key_name == 'down' or key_name == 's') and previous != 'up':
                next_direction = 'down'
                sound('keyboard_click.wav')
            elif (key_name == 'right' or key_name == 'd') and previous != 'left':
                next_direction = 'right'
                sound('keyboard_click.wav')
            elif key_name == 'p':
                paused = not paused
                print("⏸️ Game Paused" if paused else "▶️ Game Resumed")
                sound('keyboard_click.wav')
            elif key_name == 'esc':
                reason = "ESC pressed - exiting! 🚪"
                on = False
                sound('keyboard_click.wav')
            elif key_name == 'm':
                mute = not mute
                print("🔇 Game Muted" if mute else "🔊 Game Unmuted")
                sound('keyboard_click.wav')
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
    if overlay:
        overlay.update_fruit_position(target_x, target_y, wd, ln)



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
    global on, next_direction, previous, snake_body, reason, duration_drag, GAME_TICK, overlay, BORDER_PADDING, paused, mute
    on=True;reason="";paused=False;mute=False;overlay=None;next_direction="right";previous="left";snake_body=[];duration_drag=0.2;GAME_TICK=0.2
    mouse_blocker = None
    difficulty = 'unknown'  # Safe default if game exits before difficulty prompt
    ic = 0                  # Safe default if init fails before ic is assigned

    # ---------------------------
    # 1. Environment Initialization
    # ---------------------------
    try:
        print("🎮 Initializing Desktop Snake Game...")
        io.open_desktop()  # Ensure the desktop is in focus       
        time.sleep(0.5)
        pag.click(1,1)
        # Take a snapshot of the original layout for backup safety
        timestamp = time.strftime("%H_%M_%S", time.localtime())
        os.makedirs(os.path.join(os.path.expanduser("~"), "Desktop", "snake_game_desktop"), exist_ok=True)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "snake_game_desktop", f"original_desktop_{timestamp}.png") 
        pag.screenshot(desktop_path)
        
        print("Saving current layout...")
        my_layout = io.save_layout()
        time.sleep(0.1)
        io.set_auto_arrange(True)
        time.sleep(0.1)
        io.set_auto_arrange(False)
        time.sleep(0.1)
        ic = int(io.count_icons())  
        icon = ic
        difficulty=pag.confirm(text='Choose Difficulty', title='Desktop Snake Game', buttons=['easy','medium','hard']) or 'unknown'
        if difficulty=='easy':
            duration_drag=0.3
        elif difficulty=='medium':
            duration_drag=0.2
        elif difficulty=='hard':
            duration_drag=0.1
        GAME_TICK = duration_drag  # Sync game tick to chosen difficulty
        
        # Start overlay
        if overlay is None:
            overlay = GameOverlay()
            
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
    
    if overlay:
        overlay.update_boundary((icon_col+1) * wd, int(BORDER_PADDING*0.2), window_size[0] - BORDER_PADDING, r * ln - int(BORDER_PADDING))
    
    pag.alert(text='🎮 Controls:\n- WASD or Arrow Keys: Move\n- P: Pause/Resume\n- M: Mute/Unmute\n- ESC: Exit', title='Desktop Snake Game', button='OK')

    print("🛡️ Starting physical mouse blocking and cursor hiding...")
    mouse_blocker = MouseBlocker()
    mouse_blocker.start()
    mouse_hide.hide_cursor() # Hide the cursor

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
    
    
        
    print("⏳ Starting countdown...")
    for i in range(3, 0, -1):
        if overlay:
            overlay.update_center_text(str(i), "white")
        sound('keyboard_click.wav')
        time.sleep(1)
    if overlay:
        overlay.update_center_text("GO!", "#00ff00")
    sound('fruit_eat.wav')
    time.sleep(1)
    if overlay:
        overlay.update_center_text("")
        overlay.update_score(0, ic-1, 1, ic-1)
    try:
        kb.hook(on_key_event, suppress=True) # Listen & suppress keys to avoid Windows ding
    except Exception as e:
        print(f"❌ Error setting up keyboard listener: {e}")
        return
    
    # ---------------------------
    # 3. Execution Game Loop
    # ---------------------------
    try:
        while on:
            loop_start_time = time.time()

            if paused:
                if overlay:
                    overlay.update_status(f"PAUSED{' & MUTED' if mute else ''}")
                time.sleep(0.1)
                continue
            else:
                if overlay:
                    overlay.update_status("MUTED" if mute else "")

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
            # winsound.PlaySound(Beep(1000,100), winsound.SND_FILENAME | winsound.SND_ASYNC)

            # --- Check Collision Rules ---
            
            pixel_x, pixel_y = get_pixels(new_head_col, new_head_row)
            
            # 1. Wall Hit Check
            out_of_bounds_x = not ((icon_col+1) * wd < pixel_x < (window_size[0] - BORDER_PADDING))
            out_of_bounds_y = not (BORDER_PADDING < pixel_y < (r * ln))
            if out_of_bounds_x or out_of_bounds_y:
                reason = "💥 Crash! The snake hit the desktop border - Game Over!"
                on = False
                sound('lose.wav')
                break
            
            new_position = (new_head_col, new_head_row)
            
            # 2. Self Collision Check
            if snake_body_collission(new_position):
                reason = '💥 Ouch! The snake has entangled and eaten its own body!'
                on = False
                sound('lose.wav')
                break

            # 3. Win Condition Check
            if win(ic, len(snake_body)):
                reason = '🏆 VICTORY! You Have Won The Game!'
                icon = ic
                sound('win.wav')
                # Secret easter egg execution if icons >= EASTER_EGG_ICON_COUNT
                if ic >= EASTER_EGG_ICON_COUNT:
                    if overlay:
                        overlay.play_easter_egg_animation()
                    io.set_auto_arrange(True)
                    time.sleep(0.5)
                    io.set_auto_arrange(False)
                    time.sleep(0.5)
                    pag.click(1,1)
                    time.sleep(0.5)
                    for i in range(EASTER_EGG_ICON_COUNT):
                        win_icon_col = (icon-1) // r
                        win_icon_row = (icon-1) % r
                        
                        target_x, target_y = get_pixels(win_icon_col, win_icon_row)
                        
                        pag.moveTo(target_x, target_y)
                        time.sleep(0.1)
                        if not on:  # ESC was pressed; on_key_event already set on=False
                            break

                        try:
                            pag.mouseDown(button='left') 
                            final_x, final_y = win_mssg(i)
                            pag.moveTo(final_x, final_y, duration=duration_drag)
                        finally:
                            pag.mouseUp(button='left')
                        
                        icon -= 1 if icon > 0 else 0
                on = False
                break
            
            # --- Move & Consume ---
            
            if fruit_eat(new_position):
                sound('fruit_eat.wav')
                # Consume fruit & Grow!
                snake_body.insert(0, new_position)
                
                # Setup Next Fruit
                icon_col = (icon-1) // r
                icon_row = (icon-1) % r
                fruit_transport(icon_col, icon_row)
                icon -= 1 if icon > 0 else 0
                
                if overlay:
                    overlay.update_boundary((icon_col+1) * wd, int(BORDER_PADDING*0.2), window_size[0] - BORDER_PADDING, r * ln - int(BORDER_PADDING))
                
                # Orient crosshairs back to the snake head
                pag.moveTo(pixel_x, pixel_y)
                print(f"🍎 Yum! +1 Score. Length: {len(snake_body)} | Remaining Icons: {icon}")
                if overlay:
                    overlay.update_score(len(snake_body)-1, ic-1, len(snake_body), icon)
            
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
        # Unhook keyboard FIRST and unconditionally — if the suppressing hook
        # isn't removed here, Windows keeps blocking all keystrokes after exit.
        time.sleep(0.05)  # Let any in-flight suppressed key event drain
        kb.unhook_all()

        if mouse_blocker:
            print("🛡️ Restoring physical mouse and cursor...")
            mouse_blocker.stop()
            mouse_hide.show_cursor() # Show the cursor
        try:
            max_score = ic-1
            final_score = len(snake_body) - 1
            won = win(ic, len(snake_body))

            print("\n=========================================")
            print(f"🎯 Final Score: {final_score}/{max_score} Icons eaten")
            print(f"📝 Reason: {reason}")
            print("=========================================\n")

            if overlay:
                overlay.stop()
                overlay = None

            # --- Save & display high scores ---
            updated_scores = save_score(final_score, max_score, difficulty, won)
            
            final_text = f"Final Score: {final_score}/{max_score}"
            play_again = show_visual_leaderboard(updated_scores, final_score, final_text, reason, won)

            if won:
                pag.click(1, 1)
                pag.hotkey('ctrl', 'a')
                res = pag.confirm('Do you Want to restore the layout?', title='Desktop Snake Game - VICTORY!', buttons=['Yes', 'No'])
                if res == 'Yes':
                    io.restore_layout(my_layout)
            else:
                    # Standardize arrangement before abandoning UI
                    io.open_desktop()
                    io.set_auto_arrange(True)
                    time.sleep(0.1)
                    io.set_auto_arrange(False)
                    time.sleep(0.1)
                    io.restore_layout(my_layout)
                    if play_again:
                        # Execute play again
                        main()
        except Exception as e:
            print(f"Cleanup non-fatal error: {e}")

if __name__ == "__main__":
    main()
