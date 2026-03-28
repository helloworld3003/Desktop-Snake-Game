import sys
import os
import struct
import pytest
from unittest.mock import patch, MagicMock

# Create mocked versions of Win32 libraries for safe CI execution
mock_win32gui = MagicMock()
sys.modules['win32gui'] = mock_win32gui
mock_win32process = MagicMock()
mock_win32process.GetWindowThreadProcessId.return_value = (0, 1234) # Safe unpack format
sys.modules['win32process'] = mock_win32process
sys.modules['win32con'] = MagicMock()
sys.modules['win32api'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if 'icon_organizer' in sys.modules and type(sys.modules['icon_organizer']).__name__ == 'MagicMock':
    del sys.modules['icon_organizer']
import icon_organizer
import importlib
importlib.reload(icon_organizer)

@patch('icon_organizer._get_desktop_listview_hwnd')
@patch('icon_organizer.count_icons')
def test_save_layout_empty_desktop(mock_count, mock_hwnd):
    """Test that it safely handles an empty desktop without memory operations."""
    mock_hwnd.return_value = 12345
    mock_count.return_value = 0 # No icons physically present
    
    layout = icon_organizer.save_layout()
    assert layout == []

@patch('icon_organizer._get_desktop_listview_hwnd')
def test_set_auto_arrange_toggle(mock_hwnd):
    """Test that Auto Arrange correctly bitwise ORs/ANDs the GWL_STYLE."""
    mock_hwnd.return_value = 12345
    
    # Let's say the current style is totally blank (0)
    mock_win32gui.GetWindowLong.return_value = 0
    icon_organizer.LVS_AUTOARRANGE = 0x0100 # Redefine here since we mocked the lib
    icon_organizer.GWL_STYLE = -16
    icon_organizer.LVM_ARRANGE = 0x1016
    
    # Enable Auto Arrange
    icon_organizer.set_auto_arrange(True)
    # It should call SetWindowLong with 0x0100 (0 | 0x0100)
    mock_win32gui.SetWindowLong.assert_called_with(12345, -16, 0x0100)
    
    # Disable Auto Arrange (assuming starting from 0x0100)
    mock_win32gui.GetWindowLong.return_value = 0x0100
    icon_organizer.set_auto_arrange(False)
    # It should strip the 0x0100 with AND NOT (~), resulting in 0
    mock_win32gui.SetWindowLong.assert_called_with(12345, -16, 0)
