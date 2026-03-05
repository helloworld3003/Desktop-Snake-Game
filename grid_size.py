import ctypes
from ctypes import wintypes
from pyautogui import size

def get_true_desktop_spacing(system_dimension):
    user32 = ctypes.windll.user32

    # 1. Find the specific "SysListView32" window (the actual desktop grid).
    # Modern Windows often hides the desktop under a "WorkerW" process if you have custom wallpapers.
    desktop_handle = 0
    
    def enum_windows_callback(hwnd, lParam):
        nonlocal desktop_handle
        # Look for a window that has "SHELLDLL_DefView" as a child
        shell_def_view = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if shell_def_view:
            # Inside that, find the actual list view containing the icons
            desktop_handle = user32.FindWindowExW(shell_def_view, 0, "SysListView32", None)
        return True

    # Run the window enumeration
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

    # Fallback to the older Progman method if WorkerW fails
    if not desktop_handle:
        progman = user32.FindWindowW("Progman", None)
        shell_def_view = user32.FindWindowExW(progman, 0, "SHELLDLL_DefView", None)
        desktop_handle = user32.FindWindowExW(shell_def_view, 0, "SysListView32", None)

    if not desktop_handle:
        print("Error: Could not find the Windows Desktop icon grid.")
        exit()

    # 2. Send the LVM_GETITEMSPACING message to the desktop grid
    # Hex code 0x1033 specifically asks a list view for its item spacing
    LVM_GETITEMSPACING = 0x1033
    
    # SendMessage returns a single 32-bit number containing BOTH width and height
    result = user32.SendMessageW(desktop_handle, LVM_GETITEMSPACING, 0, 0)

    # 3. Split the 32-bit number: Width is the bottom 16 bits, Height is the top 16 bits
    grid_width = result & 0xFFFF
    grid_height = (result >> 16) & 0xFFFF
    row=int(system_dimension[1]/grid_height)
    column=int(system_dimension[0]/grid_width)

    return (grid_width,grid_height,row,column)

    

if __name__ == "__main__":
    wd,ln,r,c=get_true_desktop_spacing(size())
    print("-" * 40)
    print(f"True Desktop Grid Width:  {wd} pixels")
    print(f"True Desktop Grid Height: {ln} pixels")
    print(f'No. of Rows: {r}')
    print(f'No. of Columns: {c}')
    print("-" * 40)