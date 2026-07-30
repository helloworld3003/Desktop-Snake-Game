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

class FakeKeyEvent:
    def __init__(self, key_name, event_type='down'):
        self.name = key_name
        self.event_type = event_type

def test_illegal_180_turn():
    # Snake is moving RIGHT
    snake_game_desktop.previous = 'right'
    snake_game_desktop.next_direction = None
    
    # Try to move LEFT (Illegal)
    snake_game_desktop.on_key_event(FakeKeyEvent('left'))
    assert snake_game_desktop.next_direction is None # Should remain blocked
    
    # Try to move UP (Legal)
    snake_game_desktop.on_key_event(FakeKeyEvent('up'))
    assert snake_game_desktop.next_direction == 'up' # Acceptable move

def test_pause_toggle():
    snake_game_desktop.paused = False
    
    # Press P
    snake_game_desktop.on_key_event(FakeKeyEvent('p'))
    assert snake_game_desktop.paused is True
    
    # Press P again
    snake_game_desktop.on_key_event(FakeKeyEvent('p'))
    assert snake_game_desktop.paused is False

def test_esc_exit():
    snake_game_desktop.on = True
    snake_game_desktop.on_key_event(FakeKeyEvent('esc'))
    assert snake_game_desktop.on is False
    assert "ESC pressed" in snake_game_desktop.reason
