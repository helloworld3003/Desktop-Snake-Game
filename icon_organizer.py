import pyautogui as pag
import time
from win32gui import GetWindowText, GetForegroundWindow
import subprocess

def open_desktop():
    if GetWindowText(GetForegroundWindow()) != "Program Manager":  # Check if the current window is not the desktop
        pag.hotkey('win', 'd')  # Minimize all windows to show the desktop

def scan_desktop(title_text):
    total=pag.prompt(text='Enter the number of icons on your desktop:', title=title_text, default='0')
    return total

def is_auto_arrange_enabled():
    pag.press('F5')  # Refresh the desktop to ensure the context menu is up to date
    result=subprocess.run(['powershell', '-Command', '(Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\Shell\\Bags\\1\\Desktop").FFlags'], capture_output=True, text=True)
    return result.stdout.strip()


def medium_icons():
    """Set desktop icons to medium size"""
    screen_width, screen_height = pag.size()    
    # time.sleep(1)  # Wait for user to be ready    
    # Right-click on desktop
    pag.rightClick(screen_width-1, 1)  # Right-click at the top-right corner of the desktop
    time.sleep(0.1)
    pag.hotkey('alt', 'v')  # Open View submenu  
    time.sleep(0.1)
    pag.hotkey('alt', 'm')  # Select medium icons

def auto_arrange():
    screen_width, screen_height = pag.size()       
    # Right-click on desktop
    pag.rightClick(screen_width-1, 1)  # Right-click at the top-right corner of the desktop
    time.sleep(0.1)
    pag.hotkey('alt', 'v')  # Open View submenu  
    time.sleep(0.1)    
    pag.hotkey('alt', 'a')  # Toggle auto arrange icons

def align_icons_to_grid():
    screen_width, screen_height = pag.size()       
    # Right-click on desktop
    pag.rightClick(screen_width-1, 1)  # Right-click at the top-right corner of the desktop
    time.sleep(0.1)
    pag.hotkey('alt', 'v')  # Open View submenu  
    time.sleep(0.1)
    pag.hotkey('alt', 'i')  # Toggle align icons to grid

def move_icons():
    if is_auto_arrange_enabled()=='1075839524': # Check if auto arrange is enabled
        auto_arrange()
        auto_arrange()
    elif is_auto_arrange_enabled()=='1075839520':
        auto_arrange()
        align_icons_to_grid() 
        auto_arrange()
    else:
        auto_arrange()


def main():

    open_desktop()
    time.sleep(0.1)
    move_icons()
    # medium_icons()
    # move_icons_manually()
    # move_icons_manually()
    # # print("\nOrganization complete!")
    # print(f"Total icons found: {scan_desktop()}")   


if __name__ == "__main__":
    main()
