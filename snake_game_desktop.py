import random
import pyautogui as pag
import time
import icon_organizer as io
import keyboard as kb
import os

fruit = []
snake_body = []          # Tracks the (x, y) coordinates of every icon in the snake
duration_drag = 0.3      # Set the duration for dragging the mouse
wd=95;ln=125
on = True                # game loop continue
previous = 'right'       # Variable to track the previous direction for turns
next_direction = None    # Queue for the next direction input
window_size=pag.size()   # Window size
reason=''                # Reason for exit from game 
def on_key_event(event):
    """Handle keyboard events for direction changes."""
    global next_direction, on, previous,reason
    
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
                # print("ESC pressed - exiting")
                reason="ESC pressed - exiting"
                on = False
    except Exception as e:
        print(f"Error in on_key_event: {e}")

def fruit_transport(row, col):
    """Moves a desktop icon to act as a random fruit."""
    pag.moveTo(wd/2 + (col-1) * wd, ln/2 + (row-1) * ln)
    while True:
        br=True
        x = random.randint(col, 19) 
        y = random.randint(0, 7)
        x=wd/2 + x * wd
        y= ln/2 + y * ln
        global snake_body
        for positions in snake_body:
            dx = abs(x - positions[0])
            dy = abs(y - positions[1])
            # Using your original proximity logic
            if ((dx < wd and dy < 50) or (dx < 50 and dy < ln)):
                br=False
                break
        if br:
            break
    pag.dragTo(x,y, duration=duration_drag)
    global fruit
    fruit = pag.position()

def fruit_eat(dir,position):
    """Checks if the snake head is close enough to the fruit."""
    global fruit
    if not fruit:
        return False
        
    dx = abs(fruit[0] - position[0])
    dy = abs(fruit[1] - position[1])
    
    # Using your original proximity logic
    if (dx < wd and dy < 50 and dir in ['left','right']) or (dx < 50 and dy < ln and dir in ['up','down']):
        return True    
    return False

def snake_body_collission(currentx,currenty):
    col=False
    for positions in snake_body:
        dx = abs(currentx - positions[0])
        dy = abs(currenty - positions[1])
        # Using your original proximity logic
        if ((dx < wd and dy < 50) or (dx < 50 and dy < ln)):
            col=True
            break
    return col

def win(icon,l):
    return icon==l

def win_mssg(i):
    mssg = [(6, 4), (6, 5), (6, 6), (7, 7), (8, 6), (9, 7), (10, 6), (10, 5), (10, 4), (13, 4), (13, 5), (13, 6), (13, 7), (16, 4), (16, 5), (16, 6), (16, 7), (17, 5), (18, 6), (19, 4), (19, 5), (19, 6), (19, 7), (13, 3)]
    x=wd/2 + mssg[i][0] * wd
    y=ln/2 + mssg[i][1] * ln
    return (x,y)

def main():
    global on, next_direction, previous, snake_body, reason
    # setting up necessary conditions for the game
    try:
        io.open_desktop() # Open the desktop to ensure the snake game is in focus       
        time.sleep(0.2)
        desktop = os.path.join(os.path.expanduser("~"), "Desktop", "orignal_desktop.png") 
        pag.screenshot(desktop)
        io.medium_icons() # Set medium icons for better visibility
        io.move_icons() # Enable auto arrange to keep icons organized
        ic = int(io.scan_desktop('Desktop Snake Game')) # Get the number of icons on the desktop
        icon=ic
    except Exception as e:
        print(f"Failed to initialize icon_organizer: {e}")
        return

    column = ((icon-1) // 8) + 1
    row = icon % 8 if icon%8!=0 else 8

    # First icon transfer
    fruit_transport(row, column) # Move fruit to random position
    icon -= 1 
    column = ((icon-1) // 8) + 1
    row = icon % 8 if icon%8!=0 else 8
    icon-=1
    pag.alert(text='Use arrow keys to move. Press ESC to exit',title='Desktop Snake Game',button='OK')

    # Initialize the snake body with the starting coordinate
    start_x = wd/2 + (column-1) * wd
    start_y = ln/2 + (row-1) * ln
    snake_body = [(start_x, start_y)]
    
    pag.click(start_x, start_y) 
    time.sleep(0.2)
    
    print("Snake movement controls active!")
    print("Use arrow keys to move")
    print("Press ESC to exit")
    
    # Continuos game loop
    try:
        kb.on_press(on_key_event) # detect key press
    except Exception as e:
        print(f"Error setting up keyboard listener: {e}")
        return
    
    try:
        while on:
            # 1. Update direction from queue
            if next_direction is not None:
                previous = next_direction
                next_direction = None
                
            # 2. Calculate the exact coordinate for the new head position
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
            
            # 3. Wall hit check
            if not(column * wd<new_head_x <(window_size[0]-25) and 25<new_head_y<(8 * ln)):
                reason="Snake hit the wall - game over!"
                on = False
                break
            
            # 4. Snake body eaten check
            if snake_body_collission(new_head_x,new_head_y):
                reason='Your snake has eaten its own body'
                on=False
                break

            # 5. Win
            if win(ic,len(snake_body)):
                icon=ic
                # Display win Message If icon count >=24
                if ic>=24:
                    io.move_icons()
                    for i in range(24):
                        column = ((icon-1) // 8) + 1
                        row = icon % 8 if icon%8!=0 else 8
                        pag.moveTo(wd/2 + (column-1) * wd, ln/2 + (row-1) * ln)
                        time.sleep(0.2)
                        pag.mouseDown(button='left') 
                        pag.moveTo(win_mssg(i)[0],win_mssg(i)[1], duration=duration_drag)
                        pag.mouseUp(button='left')
                        icon-=1
                reason='You Have Won'
                on=False
                break
            
            # 6. Move and check for fruit
            new_position = (new_head_x, new_head_y)
            
            if fruit_eat(previous,new_position):
                # Snake grows: The fruit icon becomes the new head
                snake_body.insert(0, new_position)
                
                # Fetch a new icon for the next fruit
                column = ((icon-1) // 8) + 1
                row = icon % 8 if icon%8!=0 else 8
                fruit_transport(row, column)
                icon -= 1 
                
                # Place mouse back on the new head
                pag.moveTo(new_head_x, new_head_y)
                print(f"{len(snake_body)-1} Icons eaten! Snake length increased to {len(snake_body)}. Remaining icons: {icon}")
            
            else:
                # Normal move: Drag the tail icon to the new head position
                tail_x, tail_y = snake_body[-1]
                pag.moveTo(tail_x, tail_y)
                time.sleep(0.1)
                pag.mouseDown(button='left') 
                pag.moveTo(new_head_x, new_head_y, duration=duration_drag)
                pag.mouseUp(button='left')                
                # Update snake array 
                snake_body.insert(0, new_position)
                snake_body.pop() # Remove the old tail

            time.sleep(0.2)
    
    # Exit            
    except KeyboardInterrupt:
        on = False
        print("\nExiting snake control...")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        try:
            kb.remove_all_hotkeys()
            print(f'Final Score : {len(snake_body)-1} Icons eaten out of {len(snake_body)+icon}')
            print(f'Reason for exit : {reason}')
            # Win message
            if win(ic,len(snake_body)):
                pag.alert(text='Congratulations You have eaten all the icons in your desktop',title='Desktop Snake Game',button='OK')
                print('Congratulations You have eaten all the icons in your desktop')
            # Other exit messages
            else:
                pag.alert(text=f'Reason for exit : {reason}',title='Desktop Snake Game',button='OK')
                pag.alert(text=f'Final Score : {len(snake_body)-1} Icons eaten out of {len(snake_body)+icon}',title='Desktop Snake Game',button='OK')
            
                # arranging the icons in  a proper way before leaving
                io.open_desktop()
                io.move_icons()
        except:
            pass

if __name__ == "__main__":
    main()