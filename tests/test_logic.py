import sys
import os
from unittest.mock import MagicMock

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
