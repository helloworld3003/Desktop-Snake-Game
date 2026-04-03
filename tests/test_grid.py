import sys
import os
import ctypes
import pytest
from unittest.mock import patch, MagicMock

# Mock pyautogui before importing grid_size so the module-level `from pyautogui import size` succeeds
sys.modules['pyautogui'] = MagicMock()

# On Linux, ctypes.windll and ctypes.WINFUNCTYPE do not exist.
# Provide stubs so grid_size.py can be imported and its functions called safely in tests.
if not hasattr(ctypes, 'windll'):
    ctypes.windll = MagicMock()
if not hasattr(ctypes, 'WINFUNCTYPE'):
    ctypes.WINFUNCTYPE = ctypes.CFUNCTYPE

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


@patch.object(grid_size, 'ctypes')
def test_1080p_standard_dpi(mock_ctypes):
    """Test a standard 1920x1080 screen with typical 75x75 pixel icon spacing."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=75, icon_height=75)
    
    # Simulate a screen size of 1920x1080
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1920, 1080))
    
    assert result_w == 75
    assert result_h == 75
    # The game calculates rows and columns using integer division
    assert rows == int(1080 / 75)  # Should be 14 maximum rows of icons
    assert cols == int(1920 / 75)  # Should be 25 maximum columns of icons

@patch.object(grid_size, 'ctypes')
def test_4k_display_high_dpi(mock_ctypes):
    """Test a 4K resolution screen with 200% display scaling (huge 150x150 icons)."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=150, icon_height=150)
    
    # Simulate a screen size of 3840x2160
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((3840, 2160))
    
    assert result_w == 150
    assert result_h == 150
    assert rows == int(2160 / 150)  # 14 rows
    assert cols == int(3840 / 150)  # 25 columns

@patch.object(grid_size, 'ctypes')
def test_ultrawide_monitor_custom_icons(mock_ctypes):
    """Test a 21:9 Ultrawide display using non-square, custom icon layouts."""
    # Sometimes users tweak registry settings to make icons tall and skinny
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=50, icon_height=60)
    
    # Simulate an Ultrawide 2560x1080 resolution
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((2560, 1080))
    
    assert result_w == 50
    assert result_h == 60
    assert rows == int(1080 / 60)  # 18 rows
    assert cols == int(2560 / 50)  # 51 columns (a very long snake board!)

@patch.object(grid_size, 'ctypes')
def test_low_res_laptop_display(mock_ctypes):
    """Test a classic older laptop standard 1366x768 resolution."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=90, icon_height=90)
    
    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1366, 768))
    
    assert rows == int(768 / 90)   # 8 rows
    assert cols == int(1366 / 90)  # 15 columns

@patch.object(grid_size, 'ctypes')
def test_square_screen_equal_rows_cols(mock_ctypes):
    """Test that a square screen with square icons produces equal rows and columns."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=100, icon_height=100)

    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1000, 1000))

    assert rows == cols == 10

@patch.object(grid_size, 'ctypes')
def test_returns_correct_grid_dimensions_type(mock_ctypes):
    """Test that the return values are all integers."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=80, icon_height=100)

    result = grid_size.get_true_desktop_spacing((1920, 1080))

    assert len(result) == 4
    assert all(isinstance(v, int) for v in result)

@patch.object(grid_size, 'ctypes')
def test_minimum_icon_size_1x1(mock_ctypes):
    """Test extremely small icon size (1x1 pixel) produces large grid."""
    mock_user32 = mock_ctypes.windll.user32
    setup_fake_windows_desktop(mock_user32, icon_width=1, icon_height=1)

    result_w, result_h, rows, cols = grid_size.get_true_desktop_spacing((1920, 1080))

    assert result_w == 1
    assert result_h == 1
    assert rows == 1080
    assert cols == 1920
