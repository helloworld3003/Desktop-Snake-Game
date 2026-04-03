import sys
import os
from unittest.mock import MagicMock, patch

# ==============================================================================
# 🛠️ MOCKING EXTERNAL LIBRARIES
# We must mock libraries that require a physical desktop or sound card
# so that these tests can run successfully in the background on GitHub Actions!
# ==============================================================================

# Create fake mock objects for our dependencies
sys.modules['pyautogui'] = MagicMock()
sys.modules['winsound'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['icon_organizer'] = MagicMock()
sys.modules['physical_mouse_blocking'] = MagicMock()
sys.modules['mouse_hide'] = MagicMock()

# Mock the PyQt overlays so they don't try to open windows
mock_overlay = MagicMock()
sys.modules['hud_overlay'] = mock_overlay
mock_leaderboard = MagicMock()
sys.modules['leaderboard_ui'] = mock_leaderboard

# Critically, mock grid_size to return fake desktop metrics
# Otherwise it will crash looking for the Windows Desktop in the cloud!
mock_grid_size = MagicMock()
mock_grid_size.get_true_desktop_spacing.return_value = (95, 130, 8, 20)
sys.modules['grid_size'] = mock_grid_size

# Now we can safely import our game logic
# We need to add the parent directory to sys.path so it can find our main file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import snake_game_desktop

# ==============================================================================
# 🟢 ACTUAL UNIT TESTS 
# ==============================================================================

def test_fruit_eat_true():
    """Test that if the snake head matches the fruit, it returns True."""
    # Setup test condition
    snake_game_desktop.fruit = (5, 5)
    # Run test
    result = snake_game_desktop.fruit_eat((5, 5))
    assert result is True

def test_fruit_eat_false():
    """Test that if the snake head misses the fruit, it returns False."""
    snake_game_desktop.fruit = (5, 5)
    # Testing coordinate (4, 5) instead of (5, 5)
    assert snake_game_desktop.fruit_eat((4, 5)) is False

def test_fruit_eat_no_fruit_spawned():
    """Test what happens if the fruit hasn't spawned yet (is None)."""
    snake_game_desktop.fruit = None
    assert snake_game_desktop.fruit_eat((5, 5)) is False

def test_snake_body_collission_true():
    """Test standard collision with own tail."""
    # Simulate a snake taking up 3 grid spots
    snake_game_desktop.snake_body = [(2, 2), (2, 3), (2, 4)]
    
    # If the snake's next move is (2, 3) it should register a crash
    assert snake_game_desktop.snake_body_collission((2, 3)) is True

def test_snake_body_collission_false():
    """Test safe movement into an empty tile."""
    snake_game_desktop.snake_body = [(2, 2), (2, 3), (2, 4)]
    
    # Grid coordinate (2, 1) is safe and empty
    assert snake_game_desktop.snake_body_collission((2, 1)) is False

def test_win_condition_true():
    """Test if eating all icons triggers the win condition."""
    total_desktop_icons = 25
    current_snake_length = 25
    assert snake_game_desktop.win(total_desktop_icons, current_snake_length) is True

def test_win_condition_false():
    """Test that the win condition stays False if icons are remaining."""
    total_desktop_icons = 25
    current_snake_length = 24
    assert snake_game_desktop.win(total_desktop_icons, current_snake_length) is False

# ==============================================================================
# 🔢 get_pixels() TESTS
# ==============================================================================

def test_get_pixels_origin():
    """Test that grid position (0, 0) maps to the correct pixel coordinate."""
    # wd=95, ln=130 (from mock). Half of each is the starting offset.
    x, y = snake_game_desktop.get_pixels(0, 0)
    assert x == int(snake_game_desktop.wd / 2)
    assert y == int(snake_game_desktop.ln / 2)

def test_get_pixels_col_row():
    """Test a non-origin grid position maps to the correct pixel coordinates."""
    col, row = 3, 2
    x, y = snake_game_desktop.get_pixels(col, row)
    expected_x = int(snake_game_desktop.wd / 2) + col * snake_game_desktop.wd
    expected_y = int(snake_game_desktop.ln / 2) + row * snake_game_desktop.ln
    assert x == expected_x
    assert y == expected_y

def test_get_pixels_large_grid():
    """Test a large grid coordinate to verify the formula scales correctly."""
    col, row = 19, 7
    x, y = snake_game_desktop.get_pixels(col, row)
    expected_x = int(snake_game_desktop.wd / 2) + col * snake_game_desktop.wd
    expected_y = int(snake_game_desktop.ln / 2) + row * snake_game_desktop.ln
    assert x == expected_x
    assert y == expected_y

# ==============================================================================
# 🏆 win_mssg() TESTS
# ==============================================================================

def test_win_mssg_returns_two_ints():
    """Test that win_mssg always returns a (x, y) pixel tuple."""
    result = snake_game_desktop.win_mssg(0)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(v, int) for v in result)

def test_win_mssg_all_indices():
    """Test that all 23 win message icon positions return valid pixel coordinates."""
    # win_mssg is defined with 23 positions (indices 0-22)
    for i in range(23):
        x, y = snake_game_desktop.win_mssg(i)
        assert isinstance(x, int)
        assert isinstance(y, int)

# ==============================================================================
# 🔇 sound() MUTE TESTS
# ==============================================================================

def test_sound_not_called_when_muted():
    """Test that winsound.PlaySound is NOT called when the game is muted."""
    snake_game_desktop.mute = True
    snake_game_desktop.winsound.PlaySound.reset_mock()
    snake_game_desktop.sound('fruit_eat.wav')
    snake_game_desktop.winsound.PlaySound.assert_not_called()

def test_sound_called_when_unmuted():
    """Test that winsound.PlaySound IS called when the game is not muted."""
    snake_game_desktop.mute = False
    snake_game_desktop.winsound.PlaySound.reset_mock()
    snake_game_desktop.sound('fruit_eat.wav')
    snake_game_desktop.winsound.PlaySound.assert_called_once()
