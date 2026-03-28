import sys
import os
import pytest
from unittest.mock import MagicMock

sys.modules['pyautogui'] = MagicMock()
sys.modules['winsound'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['icon_organizer'] = MagicMock()
sys.modules['physical_mouse_blocking'] = MagicMock()
sys.modules['mouse_hide'] = MagicMock()
sys.modules['hud_overlay'] = MagicMock()
sys.modules['leaderboard_ui'] = MagicMock()

mock_grid = MagicMock()
mock_grid.get_true_desktop_spacing.return_value = (95, 130, 8, 20)
sys.modules['grid_size'] = mock_grid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import snake_game_desktop

def test_resource_path_development():
    """Test normal path resolution when running purely as a Python script (.py)"""
    # Remove _MEIPASS if it somehow exists
    if hasattr(sys, '_MEIPASS'):
        delattr(sys, '_MEIPASS')
        
    resolved_path = snake_game_desktop.resource_path('sounds\\win.wav')
    
    # In dev, the path should resolve absolutely without crashing
    assert 'sounds\\win.wav' in resolved_path

def test_resource_path_pyinstaller_compiled():
    """Test path resolution when the game is compiled as an executable (.exe)"""
    # PyInstaller injects a secret "_MEIPASS" directory into the sys object
    sys._MEIPASS = 'C:\\Simulated_Temp\\_MEI9999'
    
    resolved_path = snake_game_desktop.resource_path('sounds\\win.wav')
    
    # Function must flawlessly fetch from that simulated random Windows Temp folder
    assert resolved_path == os.path.join('C:\\Simulated_Temp\\_MEI9999', 'sounds\\win.wav')
    
    # Clean up
    delattr(sys, '_MEIPASS')
