import sys
import os
import pytest
from unittest.mock import patch

# Add the parent directory to the system path so we can import grid_size
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import grid_size

# ==============================================================================
# 🖥️ DESKTOP DISPLAY UNIT TESTS 
# We use Python's patch decorator to simulate Windows API calls so that
# we can test how the game reacts to bizarre screen resolutions and icon spaces
# without actually changing your computer's resolution!
# ==============================================================================

def setup_fake_windows_desktop(mock_user32, icon_width, icon_height):
    """
    Helper function that tricks grid_size.py into thinking it found a physical desktop
    and feeds it custom icon spacing metrics.
    """
    # 1. Give fake window handles so it doesn't trigger the "Could not find..." exit() block
    mock_user32.FindWindowW.return_value = 12345
    mock_user32.FindWindowExW.return_value = 12345
    
    # 2. Re-create how Windows packs dimensions into a 32-bit integer.
    # Windows puts Height in the top 16 bits, and Width in the bottom 16 bits.
    packed_result = (icon_height << 16) | (icon_width & 0xFFFF)
    mock_user32.SendMessageW.return_value = packed_result


@patch('grid_size.ctypes.windll.user32')
def test_1080p_standard_dpi(mock_user32):
    """Test a standard 1920x1080 screen with typical 75x75 pixel icon spacing."""
    setup_fake_windows_desktop(mock_user32, icon_width=75, icon_height=75)
    
    # Simulate a screen size of 1920x1080
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1920, 1080))
    
    assert result_w == 75
    assert result_h == 75
    # The game calculates rows and columns using integer division
    assert rows == int(1080 / 75)  # Should be 14 maximum rows of icons
    assert cols == int(1920 / 75)  # Should be 25 maximum columns of icons

@patch('grid_size.ctypes.windll.user32')
def test_4k_display_high_dpi(mock_user32):
    """Test a 4K resolution screen with 200% display scaling (huge 150x150 icons)."""
    setup_fake_windows_desktop(mock_user32, icon_width=150, icon_height=150)
    
    # Simulate a screen size of 3840x2160
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((3840, 2160))
    
    assert result_w == 150
    assert result_h == 150
    assert rows == int(2160 / 150)  # 14 rows
    assert cols == int(3840 / 150)  # 25 columns

@patch('grid_size.ctypes.windll.user32')
def test_ultrawide_monitor_custom_icons(mock_user32):
    """Test a 21:9 Ultrawide display using non-square, custom icon layouts."""
    # Sometimes users tweak registry settings to make icons tall and skinny
    setup_fake_windows_desktop(mock_user32, icon_width=50, icon_height=60)
    
    # Simulate an Ultrawide 2560x1080 resolution
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((2560, 1080))
    
    assert result_w == 50
    assert result_h == 60
    assert rows == int(1080 / 60)  # 18 rows
    assert cols == int(2560 / 50)  # 51 columns (a very long snake board!)

@patch('grid_size.ctypes.windll.user32')
def test_low_res_laptop_display(mock_user32):
    """Test a classic older laptop standard 1366x768 resolution."""
    setup_fake_windows_desktop(mock_user32, icon_width=90, icon_height=90)
    
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1366, 768))
    
    assert rows == int(768 / 90)   # 8 rows
    assert cols == int(1366 / 90)  # 15 columns
