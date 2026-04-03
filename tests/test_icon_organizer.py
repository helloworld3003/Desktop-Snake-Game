import sys
import os
import struct
import pytest
from unittest.mock import patch, MagicMock, call

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

def test_save_layout_empty_desktop():
    """Test that it safely handles an empty desktop without memory operations."""
    with patch.object(icon_organizer, '_get_desktop_listview_hwnd', return_value=12345), \
         patch.object(icon_organizer, 'count_icons', return_value=0):
        layout = icon_organizer.save_layout()
    assert layout == []

def test_set_auto_arrange_enable():
    """Test that enabling Auto Arrange ORs the LVS_AUTOARRANGE bit into the window style."""
    fake_hwnd = 12345
    icon_organizer.LVS_AUTOARRANGE = 0x0100
    icon_organizer.GWL_STYLE = -16
    icon_organizer.LVM_ARRANGE = 0x1016

    with patch.object(icon_organizer, '_get_desktop_listview_hwnd', return_value=fake_hwnd):
        mock_win32gui.GetWindowLong.return_value = 0  # Starting style is blank
        icon_organizer.set_auto_arrange(True)

    # New style should be 0 | 0x0100 = 0x0100
    mock_win32gui.SetWindowLong.assert_called_with(fake_hwnd, -16, 0x0100)

def test_set_auto_arrange_disable():
    """Test that disabling Auto Arrange strips the LVS_AUTOARRANGE bit from the window style."""
    fake_hwnd = 12345
    icon_organizer.LVS_AUTOARRANGE = 0x0100
    icon_organizer.GWL_STYLE = -16
    icon_organizer.LVM_ARRANGE = 0x1016

    with patch.object(icon_organizer, '_get_desktop_listview_hwnd', return_value=fake_hwnd):
        mock_win32gui.GetWindowLong.return_value = 0x0100  # Only autoarrange bit is set
        icon_organizer.set_auto_arrange(False)

    # New style should be 0x0100 & ~0x0100 = 0
    mock_win32gui.SetWindowLong.assert_called_with(fake_hwnd, -16, 0)

def test_set_auto_arrange_no_hwnd(capsys):
    """Test that set_auto_arrange exits gracefully when no desktop handle is found."""
    with patch.object(icon_organizer, '_get_desktop_listview_hwnd', return_value=0):
        icon_organizer.set_auto_arrange(True)  # Should not raise
    captured = capsys.readouterr()
    assert 'Error' in captured.out

def test_count_icons_no_hwnd(capsys):
    """Test that count_icons returns 0 when no desktop handle is found."""
    with patch.object(icon_organizer, '_get_desktop_listview_hwnd', return_value=0):
        result = icon_organizer.count_icons()
    assert result == 0
    captured = capsys.readouterr()
    assert 'Error' in captured.out
