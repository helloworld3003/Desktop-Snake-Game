import ctypes
import keyboard

# --- Win32 API Constants ---
OCR_NORMAL = 32512        # The standard arrow cursor
SPI_SETCURSORS = 0x0057   # Command to reload system cursors

# Access the user32 library
user32 = ctypes.windll.user32

def hide_cursor():
    """Creates a transparent cursor and replaces the system arrow with it."""
    # Create masks for a 32x32 pixel cursor for full transparency
    and_mask = bytearray([0xFF] * 128)
    xor_mask = bytearray([0x00] * 128)

    hCursor = user32.CreateCursor(0, 0, 0, 32, 32, bytes(and_mask), bytes(xor_mask))
    user32.SetSystemCursor(hCursor, OCR_NORMAL)

def show_cursor():
    """Forces Windows to reload all default cursors from the registry."""
    user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, 0)

def main():
    print("Hiding the cursor system-wide...")
    hide_cursor()
    
    # Notice the difference here: you don't need to be in the console window anymore!
    print("Cursor is hidden. Press 'ESC' *anywhere* to show it and exit.")

    try:
        # keyboard.wait() halts the script right here until the exact key is pressed.
        # It's much more CPU-efficient than a while loop.
        keyboard.wait('esc')
        print("ESC detected. Restoring cursor...")
            
    finally:
        # CRITICAL SAFETY: Still ensuring this runs even if the script crashes
        show_cursor()
        print("Cursor restored. Program terminated.")

if __name__ == "__main__":
    main()