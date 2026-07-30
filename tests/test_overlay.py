import sys
import os
import pytest
from unittest.mock import patch

# We mock tkinter entirely so that no actual windows pop up causing tests to fail
sys.modules['tkinter'] = __import__('unittest.mock').mock.MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if 'hud_overlay' in sys.modules and type(sys.modules['hud_overlay']).__name__ == 'MagicMock':
    del sys.modules['hud_overlay']
import hud_overlay
import importlib
importlib.reload(hud_overlay)

# We patch threading.Thread so GameOverlay doesn't actually launch the UI
# because running `root.mainloop()` in a test will freeze indefinitely!
@patch('hud_overlay.threading.Thread')
def test_hud_score_formatting(mock_thread):
    # Instantiate without freezing
    overlay = hud_overlay.GameOverlay()
    
    # Send a score update command
    overlay.update_score(score=5, max_score=20, length=6, icons_left=15)
    
    # Verify the message entered the queue successfully
    assert overlay.cmd_queue.qsize() == 1
    
    cmd, data = overlay.cmd_queue.get()
    
    # Verify the exact structural tuple format created
    assert cmd == 'score'
    assert data == (5, 20, 6, 15)

@patch('hud_overlay.threading.Thread')
def test_hud_boundary_command(mock_thread):
    overlay = hud_overlay.GameOverlay()
    
    overlay.update_boundary(left=10, top=10, right=500, bottom=500)
    
    cmd, data = overlay.cmd_queue.get()
    
    assert cmd == 'boundary'
    assert data == (10, 10, 500, 500)
