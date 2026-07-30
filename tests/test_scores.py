import sys
import os
import json
import tempfile
from unittest.mock import MagicMock

# ==============================================================================
# 🛠️ MOCKING EXTERNAL LIBRARIES
# Similar to test_logic.py, we must mock libraries that require a physical desktop
# ==============================================================================

sys.modules['pyautogui'] = MagicMock()
sys.modules['winsound'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['icon_organizer'] = MagicMock()
sys.modules['physical_mouse_blocking'] = MagicMock()
sys.modules['mouse_hide'] = MagicMock()

mock_overlay = MagicMock()
sys.modules['hud_overlay'] = mock_overlay
mock_leaderboard = MagicMock()
sys.modules['leaderboard_ui'] = mock_leaderboard

mock_grid_size = MagicMock()
mock_grid_size.get_true_desktop_spacing.return_value = (95, 130, 8, 20)
sys.modules['grid_size'] = mock_grid_size

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import snake_game_desktop

# ==============================================================================
# 🏆 SCORE SYSTEM UNIT TESTS 
# ==============================================================================

def test_format_leaderboard_empty():
    """Test formatting when there are no scores."""
    result = snake_game_desktop.format_leaderboard([], 0)
    assert result == 'No scores recorded yet.'

def test_format_leaderboard_crown():
    """Test that the 'YOU' crown is appropriately attached to the current user's score."""
    sample_scores = [
        {'score': 15, 'max': 20, 'pct': 75, 'difficulty': 'hard', 'won': False, 'date': '2026-03-28 12:00'},
        {'score': 10, 'max': 20, 'pct': 50, 'difficulty': 'medium', 'won': False, 'date': '2026-03-28 11:00'}
    ]
    # Highlight score is 10, should append ◀ YOU to the second line
    result = snake_game_desktop.format_leaderboard(sample_scores, 10)
    
    # 🥇 goes to first place, 🥈 goes to second place
    assert '🥇  15' in result
    assert '◀ YOU' in result
    assert '🥈  10/20  ( 50%)  medium  2026-03-28 11:00 ◀ YOU' in result

def test_save_score_sorting_andFileIO():
    """Test saving a score creates the file, keeps top 5, and sorts descending by percentage."""
    
    # We don't want to actually write to the user's desktop high_score.json during a test!
    # So we temporarily redirect HIGH_SCORE_FILE to a safe temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        temp_file_path = tmp.name
        
    old_file_path = snake_game_desktop.HIGH_SCORE_FILE
    snake_game_desktop.HIGH_SCORE_FILE = temp_file_path
    
    try:
        # Pre-seed the leaderboard with 5 dummy scores (scores out of 20, max pct is 100)
        dummy_data = [
            {'score': 5, 'max': 20, 'pct': 25, 'difficulty': 'easy', 'won': False, 'date': '2026'},
            {'score': 15, 'max': 20, 'pct': 75, 'difficulty': 'hard', 'won': False, 'date': '2026'},
            {'score': 10, 'max': 20, 'pct': 50, 'difficulty': 'medium', 'won': False, 'date': '2026'},
            {'score': 8, 'max': 20, 'pct': 40, 'difficulty': 'medium', 'won': False, 'date': '2026'},
            {'score': 2, 'max': 20, 'pct': 10, 'difficulty': 'easy', 'won': False, 'date': '2026'},
        ]
        with open(temp_file_path, 'w') as f:
            json.dump(dummy_data, f)
            
        # Call save_score with an absolute top score (20/20 on Hard = 100% + won bonus)
        result_scores = snake_game_desktop.save_score(score=20, max_score=20, difficulty='hard', won=True)
        
        # Validate logic:
        # 1. Length should STILL be 5 (MAX_LEADERBOARD_ENTRIES capped)
        assert len(result_scores) == 5
        
        # 2. The new amazing score should logically be sorted to position 0 (Top Score)
        assert result_scores[0]['score'] == 20
        assert result_scores[0]['won'] is True
        
        # 3. The worst score (2) should have been completely pushed off the bottom of the list
        assert not any(entry['score'] == 2 for entry in result_scores)
        
    finally:
        # Cleanup: Put the old file path back so we don't break anything, and delete the temp file
        snake_game_desktop.HIGH_SCORE_FILE = old_file_path
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
