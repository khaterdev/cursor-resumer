import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cursor_resumer import CursorResumer


class TestCursorResumer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.resumer = CursorResumer()
    
    def test_initialization(self):
        """Test CursorResumer initialization"""
        self.assertEqual(self.resumer.click_count, 0)
        self.assertEqual(self.resumer.last_click_time, 0)
        self.assertEqual(self.resumer.debug_counter, 0)
    
    @patch('subprocess.run')
    def test_is_cursor_running(self, mock_run):
        """Test checking if Cursor is running"""
        # Test when Cursor is running
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(self.resumer.is_cursor_running())
        
        # Test when Cursor is not running
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(self.resumer.is_cursor_running())
    
    @patch('subprocess.run')
    def test_bring_cursor_to_front(self, mock_run):
        """Test bringing Cursor to front"""
        self.resumer.bring_cursor_to_front()
        mock_run.assert_called_once()
        
        # Check that osascript was called
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], 'osascript')
        self.assertIn('Cursor', ' '.join(call_args))
    
    @patch('subprocess.run')
    def test_get_cursor_window_bounds(self, mock_run):
        """Test getting Cursor window bounds"""
        # Test successful bounds retrieval
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='100,200,800,600\n'
        )
        bounds = self.resumer.get_cursor_window_bounds()
        self.assertEqual(bounds, (100, 200, 800, 600))
        
        # Test failed bounds retrieval
        mock_run.return_value = MagicMock(returncode=1)
        bounds = self.resumer.get_cursor_window_bounds()
        self.assertIsNone(bounds)
    
    @patch('cursor_resumer.main.ImageGrab')
    @patch.object(CursorResumer, 'get_cursor_window_bounds')
    def test_capture_cursor_window(self, mock_get_bounds, mock_imagegrab):
        """Test capturing Cursor window screenshot"""
        # Test with bounds
        mock_get_bounds.return_value = (100, 200, 800, 600)
        mock_screenshot = MagicMock()
        mock_imagegrab.grab.return_value = mock_screenshot
        
        screenshot, offset = self.resumer.capture_cursor_window()
        
        mock_imagegrab.grab.assert_called_with(bbox=(100, 200, 900, 800))
        self.assertEqual(offset, (100, 200))
        
        # Test without bounds (fallback to full screen)
        mock_get_bounds.return_value = None
        screenshot, offset = self.resumer.capture_cursor_window()
        
        mock_imagegrab.grab.assert_called_with()
        self.assertEqual(offset, (0, 0))
    
    def test_configuration_values(self):
        """Test that configuration values are set correctly"""
        from cursor_resumer.main import (
            CHECK_INTERVAL, MIN_CLICK_INTERVAL, 
            VERBOSE, DEBUG_SAVE_SCREENSHOTS, BACKGROUND_MODE
        )
        
        self.assertEqual(CHECK_INTERVAL, 1)
        self.assertEqual(MIN_CLICK_INTERVAL, 10)
        self.assertFalse(VERBOSE)
        self.assertFalse(DEBUG_SAVE_SCREENSHOTS)
        self.assertTrue(BACKGROUND_MODE)


class TestCommandLineInterface(unittest.TestCase):
    @patch('sys.argv', ['cursor-resumer', '--help'])
    def test_help_option(self):
        """Test --help command line option"""
        from cursor_resumer.main import main
        
        with self.assertRaises(SystemExit):
            with patch('builtins.print') as mock_print:
                main()
                # Check that help text was printed
                mock_print.assert_called()


if __name__ == '__main__':
    unittest.main()