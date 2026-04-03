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

@patch('hud_overlay.threading.Thread')
def test_hud_status_update(mock_thread):
    """Test that update_status puts a 'status' command with the correct text."""
    overlay = hud_overlay.GameOverlay()

    overlay.update_status("PAUSED")

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'status'
    assert data == "PAUSED"

@patch('hud_overlay.threading.Thread')
def test_hud_fruit_position(mock_thread):
    """Test that update_fruit_position queues a 'fruit' command with pixel/size data."""
    overlay = hud_overlay.GameOverlay()

    overlay.update_fruit_position(x=200, y=300, size_w=95, size_h=130)

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'fruit'
    assert data == (200, 300, 95, 130)

@patch('hud_overlay.threading.Thread')
def test_hud_center_text(mock_thread):
    """Test that update_center_text queues a 'center_text' command with text and color."""
    overlay = hud_overlay.GameOverlay()

    overlay.update_center_text("GO!", "#00ff00")

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'center_text'
    assert data == ("GO!", "#00ff00")

@patch('hud_overlay.threading.Thread')
def test_hud_center_text_default_color(mock_thread):
    """Test that update_center_text uses red as the default color."""
    overlay = hud_overlay.GameOverlay()

    overlay.update_center_text("3")

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'center_text'
    assert data == ("3", "red")

@patch('hud_overlay.threading.Thread')
def test_hud_stop_command(mock_thread):
    """Test that stop() queues a 'stop' command."""
    overlay = hud_overlay.GameOverlay()

    overlay.stop()

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'stop'
    assert data is None

@patch('hud_overlay.threading.Thread')
def test_hud_easter_egg_command(mock_thread):
    """Test that play_easter_egg_animation() queues an 'easter_egg' command."""
    overlay = hud_overlay.GameOverlay()

    overlay.play_easter_egg_animation()

    cmd, data = overlay.cmd_queue.get()
    assert cmd == 'easter_egg'
    assert data is None

@patch('hud_overlay.threading.Thread')
def test_hud_queue_ordering(mock_thread):
    """Test that multiple commands are queued and dequeued in FIFO order."""
    overlay = hud_overlay.GameOverlay()

    overlay.update_score(1, 10, 2, 9)
    overlay.update_status("MUTED")
    overlay.stop()

    assert overlay.cmd_queue.qsize() == 3
    assert overlay.cmd_queue.get()[0] == 'score'
    assert overlay.cmd_queue.get()[0] == 'status'
    assert overlay.cmd_queue.get()[0] == 'stop'
