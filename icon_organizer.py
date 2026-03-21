import ctypes
import struct
import win32gui
import win32process
import win32con
import win32api
from win32gui import GetWindowText, GetForegroundWindow


# --- Windows API Constants ---
LVM_GETITEMCOUNT = 0x1004
LVM_GETITEMPOSITION = 0x1010
LVM_SETITEMPOSITION = 0x100F
LVM_ARRANGE = 0x1016
# New constants for Auto Arrange
GWL_STYLE = -16
LVS_AUTOARRANGE = 0x0100

# Arrange flags
LVA_DEFAULT = 0x0000
LVA_SNAPTOGRID = 0x0005

def open_desktop():
    if GetWindowText(GetForegroundWindow()) != "Program Manager":  # Check if the current window is not the desktop
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Press Win key
        ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # Press D key
        ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # Release D key
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Release Win key

def _get_desktop_listview_hwnd():
    """
    Locates the handle (HWND) for the Windows Desktop ListView.
    Accounts for both Windows 7/8 (Progman) and Windows 10/11 (WorkerW).
    """
    hwnd = win32gui.FindWindow("Progman", "Program Manager")
    hwnd = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
    
    if hwnd:
        return win32gui.FindWindowEx(hwnd, 0, "SysListView32", None)

    # Windows 10/11 Fallback: If wallpaper engines or updates hide Progman, it moves to WorkerW
    hwnds = []
    win32gui.EnumWindows(lambda h, param: param.append(h), hwnds)
    for w in hwnds:
        if win32gui.GetClassName(w) == "WorkerW":
            child = win32gui.FindWindowEx(w, 0, "SHELLDLL_DefView", None)
            if child:
                return win32gui.FindWindowEx(child, 0, "SysListView32", None)
    return 0

def count_icons():
    """Returns the total number of icons currently on the desktop."""
    hwnd = _get_desktop_listview_hwnd()
    if not hwnd:
        print("Error: Could not find Desktop ListView.")
        return 0
    return win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)

def save_layout():
    """
    Reads the (X, Y) coordinates of every icon on the desktop.
    Returns a list of dictionaries containing the index and coordinates.
    """
    hwnd = _get_desktop_listview_hwnd()
    count = count_icons()
    if count == 0: return []

    # Get the Process ID of explorer.exe
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
    # Open the explorer process to allocate memory inside it
    hProcess = ctypes.windll.kernel32.OpenProcess(
        win32con.PROCESS_VM_OPERATION | win32con.PROCESS_VM_READ | win32con.PROCESS_VM_WRITE, 
        False, pid
    )
    
    # Allocate 8 bytes of memory (for X and Y integers) inside explorer.exe
    pMem = ctypes.windll.kernel32.VirtualAllocEx(
        hProcess, 0, 8, win32con.MEM_COMMIT, win32con.PAGE_READWRITE
    )
    
    layout = []
    for i in range(count):
        # Ask the ListView to copy the position of icon 'i' into our allocated memory
        win32gui.SendMessage(hwnd, LVM_GETITEMPOSITION, i, pMem)
        
        # Read that memory back into our Python script
        buffer = ctypes.create_string_buffer(8)
        bytes_read = ctypes.c_size_t(0)
        ctypes.windll.kernel32.ReadProcessMemory(
            hProcess, pMem, buffer, 8, ctypes.byref(bytes_read)
        )
        
        # Unpack the raw bytes into two integers (X, Y)
        x, y = struct.unpack("ii", buffer.raw)
        layout.append({"index": i, "x": x, "y": y})
        
    # Clean up memory! (Critical to prevent memory leaks in Windows Explorer)
    ctypes.windll.kernel32.VirtualFreeEx(hProcess, pMem, 0, win32con.MEM_RELEASE)
    ctypes.windll.kernel32.CloseHandle(hProcess)
    
    return layout

def restore_layout(layout):
    """
    Takes a saved layout list and moves the icons back to their saved (X, Y) coordinates.
    """
    hwnd = _get_desktop_listview_hwnd()
    if not hwnd: return

    for item in layout:
        # The Windows API expects the X and Y coordinates packed into a single 32-bit integer (lParam)
        lparam = win32api.MAKELONG(item["x"], item["y"])
        
        # Send the command to move the icon
        win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, item["index"], lparam)
        
    print("Layout restored successfully.")

def set_auto_arrange(enable=True):
    """
    Toggles the Windows 'Auto arrange icons' setting.
    This locks the icons and packs them to the left side of the screen.
    """
    hwnd = _get_desktop_listview_hwnd()
    if not hwnd:
        print("Error: Could not find Desktop ListView.")
        return

    # 1. Get the current styling of the Desktop ListView
    current_style = win32gui.GetWindowLong(hwnd, GWL_STYLE)

    # 2. Add or remove the Auto Arrange bit
    if enable:
        new_style = current_style | LVS_AUTOARRANGE
    else:
        new_style = current_style & ~LVS_AUTOARRANGE

    # 3. Apply the new style back to the desktop
    win32gui.SetWindowLong(hwnd, GWL_STYLE, new_style)

    # 4. Force Windows to visually refresh and apply the layout instantly
    # Sending LVM_ARRANGE with '0' (LVA_DEFAULT) triggers the style we just set
    win32gui.SendMessage(hwnd, LVM_ARRANGE, 0, 0)
    
    status = "ON" if enable else "OFF"
    print(f"Windows 'Auto Arrange' is now {status}.")

# ==========================================
# EXAMPLE USAGE
# ==========================================
if __name__ == "__main__":
    import time
    open_desktop()
    print(f"Total Icons Found: {count_icons()}")
    
    print("Saving current layout...")
    my_layout = save_layout()
    time.sleep(2)
    set_auto_arrange(True)
    time.sleep(2)
    set_auto_arrange(False)
    time.sleep(2)
    
    print("Restoring layout...")
    restore_layout(my_layout)
    
    # If you want to snap them to the grid after moving them around:
    # auto_arrange(snap_to_grid=True)
