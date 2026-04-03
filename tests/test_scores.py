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

def test_format_leaderboard_medals():
    """Test that 🥇/🥈/🥉 medals and numbered positions are applied correctly."""
    sample_scores = [
        {'score': 20, 'max': 20, 'pct': 100, 'difficulty': 'hard', 'won': True, 'date': '2026-01-01 10:00'},
        {'score': 15, 'max': 20, 'pct': 75,  'difficulty': 'hard', 'won': False, 'date': '2026-01-02 10:00'},
        {'score': 10, 'max': 20, 'pct': 50,  'difficulty': 'medium', 'won': False, 'date': '2026-01-03 10:00'},
        {'score': 5,  'max': 20, 'pct': 25,  'difficulty': 'easy', 'won': False, 'date': '2026-01-04 10:00'},
    ]
    result = snake_game_desktop.format_leaderboard(sample_scores, -1)  # -1 = nobody highlighted
    assert '🥇' in result
    assert '🥈' in result
    assert '🥉' in result
    assert ' 4.' in result  # 4th place uses a number, not a medal

def test_format_leaderboard_won_tag():
    """Test that the win trophy 🏆 tag appears only on entries where won=True."""
    sample_scores = [
        {'score': 20, 'max': 20, 'pct': 100, 'difficulty': 'hard', 'won': True, 'date': '2026-01-01'},
        {'score': 10, 'max': 20, 'pct': 50,  'difficulty': 'medium', 'won': False, 'date': '2026-01-02'},
    ]
    result = snake_game_desktop.format_leaderboard(sample_scores, -1)
    lines = result.split('\n')
    first_entry_line = lines[2]  # Header + divider occupy indices 0 and 1
    second_entry_line = lines[3]
    assert '🏆' in first_entry_line
    assert '🏆' not in second_entry_line

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

def test_load_scores_no_file():
    """Test that load_scores returns an empty list when the score file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = snake_game_desktop.HIGH_SCORE_FILE
        snake_game_desktop.HIGH_SCORE_FILE = os.path.join(tmpdir, 'nonexistent.json')
        try:
            result = snake_game_desktop.load_scores()
            assert result == []
        finally:
            snake_game_desktop.HIGH_SCORE_FILE = old_path

def test_load_scores_existing_file():
    """Test that load_scores correctly reads and returns scores from a JSON file."""
    sample = [{'score': 7, 'max': 10, 'pct': 70, 'difficulty': 'easy', 'won': False, 'date': '2026'}]
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as tmp:
        json.dump(sample, tmp)
        temp_path = tmp.name
    old_path = snake_game_desktop.HIGH_SCORE_FILE
    snake_game_desktop.HIGH_SCORE_FILE = temp_path
    try:
        result = snake_game_desktop.load_scores()
        assert result == sample
    finally:
        snake_game_desktop.HIGH_SCORE_FILE = old_path
        os.remove(temp_path)

def test_load_scores_corrupt_file():
    """Test that load_scores gracefully returns [] when the JSON file is corrupted."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as tmp:
        tmp.write("THIS IS NOT VALID JSON {{{")
        temp_path = tmp.name
    old_path = snake_game_desktop.HIGH_SCORE_FILE
    snake_game_desktop.HIGH_SCORE_FILE = temp_path
    try:
        result = snake_game_desktop.load_scores()
        assert result == []
    finally:
        snake_game_desktop.HIGH_SCORE_FILE = old_path
        os.remove(temp_path)

def test_save_score_creates_file_when_none_exists():
    """Test that save_score works correctly when no high-score file exists yet."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = snake_game_desktop.HIGH_SCORE_FILE
        snake_game_desktop.HIGH_SCORE_FILE = os.path.join(tmpdir, 'new_scores.json')
        try:
            result = snake_game_desktop.save_score(score=5, max_score=20, difficulty='medium', won=False)
            assert len(result) == 1
            assert result[0]['score'] == 5
            assert result[0]['difficulty'] == 'medium'
        finally:
            snake_game_desktop.HIGH_SCORE_FILE = old_path

def test_save_score_pct_calculation():
    """Test that the percentage is calculated correctly for different difficulties."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_path = snake_game_desktop.HIGH_SCORE_FILE
        snake_game_desktop.HIGH_SCORE_FILE = os.path.join(tmpdir, 'scores.json')
        try:
            # On 'hard', a 10/20 = 50% at full hard weight (diff_val/hard = 1.0)
            result = snake_game_desktop.save_score(score=10, max_score=20, difficulty='hard', won=False)
            assert result[0]['pct'] == 50

            # On 'easy', a 10/20 = 50% * (5/20) = 12.5% → rounded to 13
            result = snake_game_desktop.save_score(score=10, max_score=20, difficulty='easy', won=False)
            easy_entry = next(e for e in result if e['difficulty'] == 'easy' and e['score'] == 10)
            assert easy_entry['pct'] == round((10 / 20) * 100 * (5 / 20))
        finally:
            snake_game_desktop.HIGH_SCORE_FILE = old_path
