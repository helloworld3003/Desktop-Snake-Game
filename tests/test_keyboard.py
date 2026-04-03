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

def test_all_illegal_180_turns():
    """Test all four illegal reverse-direction combinations."""
    illegal_combos = [
        ('right', 'left'),
        ('left', 'right'),
        ('up', 'down'),
        ('down', 'up'),
    ]
    for current, attempted in illegal_combos:
        snake_game_desktop.previous = current
        snake_game_desktop.next_direction = None
        snake_game_desktop.on_key_event(FakeKeyEvent(attempted))
        assert snake_game_desktop.next_direction is None, (
            f"Expected blocked turn from {current} to {attempted}"
        )

def test_legal_turns():
    """Test that all four legal perpendicular turns are accepted."""
    legal_combos = [
        ('right', 'up'),
        ('right', 'down'),
        ('left', 'up'),
        ('left', 'down'),
        ('up', 'left'),
        ('up', 'right'),
        ('down', 'left'),
        ('down', 'right'),
    ]
    for current, attempted in legal_combos:
        snake_game_desktop.previous = current
        snake_game_desktop.next_direction = None
        snake_game_desktop.on_key_event(FakeKeyEvent(attempted))
        assert snake_game_desktop.next_direction == attempted, (
            f"Expected allowed turn from {current} to {attempted}"
        )

def test_wasd_controls():
    """Test that W/A/S/D alternative keys map to the correct directions."""
    # For each WASD key, choose a current direction that is NOT its opposite
    # so the move is always legal (opposite would block the turn).
    wasd_map = [
        ('w', 'right', 'up'),    # W=up, not blocked when going right
        ('s', 'right', 'down'),  # S=down, not blocked when going right
        ('a', 'up', 'left'),     # A=left, not blocked when going up
        ('d', 'up', 'right'),    # D=right, not blocked when going up
    ]
    for key, current_dir, expected_dir in wasd_map:
        snake_game_desktop.previous = current_dir
        snake_game_desktop.next_direction = None
        snake_game_desktop.on_key_event(FakeKeyEvent(key))
        assert snake_game_desktop.next_direction == expected_dir, (
            f"WASD key '{key}' should produce direction '{expected_dir}'"
        )

def test_key_up_event_ignored():
    """Test that key release (event_type='up') events do NOT change direction."""
    snake_game_desktop.previous = 'right'
    snake_game_desktop.next_direction = None
    snake_game_desktop.on_key_event(FakeKeyEvent('up', event_type='up'))
    assert snake_game_desktop.next_direction is None  # key-release must be ignored

def test_pause_toggle():
    snake_game_desktop.paused = False
    
    # Press P
    snake_game_desktop.on_key_event(FakeKeyEvent('p'))
    assert snake_game_desktop.paused is True
    
    # Press P again
    snake_game_desktop.on_key_event(FakeKeyEvent('p'))
    assert snake_game_desktop.paused is False

def test_mute_toggle():
    """Test that the M key toggles the mute flag."""
    snake_game_desktop.mute = False

    snake_game_desktop.on_key_event(FakeKeyEvent('m'))
    assert snake_game_desktop.mute is True

    snake_game_desktop.on_key_event(FakeKeyEvent('m'))
    assert snake_game_desktop.mute is False

def test_esc_exit():
    snake_game_desktop.on = True
    snake_game_desktop.on_key_event(FakeKeyEvent('esc'))
    assert snake_game_desktop.on is False
    assert "ESC pressed" in snake_game_desktop.reason
