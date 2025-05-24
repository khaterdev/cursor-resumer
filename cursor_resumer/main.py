#!/usr/bin/env python3
"""
Cursor Resumer Script
Automatically clicks "resume the conversation" when Cursor hits the 25 tool call limit
"""

import time
import subprocess
import sys
import os
import re
from datetime import datetime

try:
    import pyautogui
    import cv2
    import numpy as np
    from PIL import ImageGrab, Image
    import pytesseract
except ImportError as e:
    print(f"Missing required module: {e}")
    print("\nInstall required modules with:")
    print("pip3 install pyautogui opencv-python pillow pytesseract")
    sys.exit(1)

# Configuration
CHECK_INTERVAL = 1  # seconds
MIN_CLICK_INTERVAL = 10  # minimum seconds between clicks
VERBOSE = False
DEBUG_SAVE_SCREENSHOTS = False  # Save screenshots for debugging
BACKGROUND_MODE = True  # Run quietly in background until resume is found

class CursorResumer:
    def __init__(self):
        self.click_count = 0
        self.last_click_time = 0
        self.debug_counter = 0
        
        # Disable pyautogui failsafe for production
        # (move mouse to corner to abort)
        pyautogui.FAILSAFE = True
        
        # Create debug directory if needed
        if DEBUG_SAVE_SCREENSHOTS:
            os.makedirs("debug_screenshots", exist_ok=True)
        
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            print("\n" + "="*60)
            print("❌ Tesseract OCR is not installed!")
            print("="*60)
            print("\nCursor-resumer requires Tesseract OCR to function.")
            print("\nTo install Tesseract:")
            print("  brew install tesseract")
            print("\nIf you don't have Homebrew, install it first:")
            print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("="*60 + "\n")
            
            # Offer to install if running interactively
            if sys.stdin.isatty():
                response = input("Would you like to try installing Tesseract now? [Y/n]: ").strip().lower()
                if response in ['', 'y', 'yes']:
                    try:
                        print("\nAttempting to install Tesseract...")
                        result = subprocess.run(['brew', 'install', 'tesseract'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print("✅ Tesseract installed successfully! Please restart cursor-resumer.")
                        else:
                            print(f"❌ Installation failed: {result.stderr}")
                    except FileNotFoundError:
                        print("❌ Homebrew is not installed. Please install it first.")
            
            sys.exit(1)
    
    def is_cursor_running(self):
        """Check if Cursor app is running"""
        try:
            result = subprocess.run(['pgrep', '-x', 'Cursor'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def bring_cursor_to_front(self):
        """Bring Cursor app to front"""
        try:
            subprocess.run(['osascript', '-e', 
                          'tell application "Cursor" to activate'], 
                          capture_output=True)
            time.sleep(0.5)  # Wait for window to come to front
        except:
            pass
    
    def get_cursor_window_bounds(self):
        """Get Cursor window position and size"""
        try:
            script = '''
            tell application "System Events"
                tell process "Cursor"
                    set frontWindow to front window
                    set {x, y} to position of frontWindow
                    set {w, h} to size of frontWindow
                    return (x as string) & "," & (y as string) & "," & (w as string) & "," & (h as string)
                end tell
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                bounds = result.stdout.strip().split(',')
                x, y, w, h = map(int, bounds)
                return (x, y, w, h)
        except:
            pass
        return None
    
    def capture_cursor_window(self):
        """Capture screenshot of Cursor window (even if not in front)"""
        bounds = self.get_cursor_window_bounds()
        
        if bounds:
            x, y, w, h = bounds
            # Capture specific region even if window is in background
            # On macOS, this works even for background windows
            screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            return screenshot, (x, y)
        else:
            # Fallback to full screen
            return ImageGrab.grab(), (0, 0)
    
    def save_debug_screenshot(self, image, suffix=""):
        """Save screenshot for debugging"""
        if DEBUG_SAVE_SCREENSHOTS:
            # Ensure directory exists
            os.makedirs("debug_screenshots", exist_ok=True)
            filename = f"debug_screenshots/debug_{self.debug_counter:04d}{suffix}.png"
            image.save(filename)
            if not BACKGROUND_MODE or VERBOSE:
                print(f"Saved debug screenshot: {filename}")
            self.debug_counter += 1
    
    def find_resume_button_comprehensive(self, screenshot, window_offset):
        """Comprehensive search for the resume button"""
        # Convert PIL Image to numpy array
        img_np = np.array(screenshot)
        
        # Save original for debugging
        if DEBUG_SAVE_SCREENSHOTS:
            self.save_debug_screenshot(screenshot, "_original")
        
        # Method 1: Full OCR scan
        if not BACKGROUND_MODE or VERBOSE:
            print("Performing OCR scan...")
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Try different preprocessing methods
        methods = [
            ("original", gray),
            ("threshold", cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]),
            ("adaptive", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                             cv2.THRESH_BINARY, 11, 2)),
        ]
        
        for method_name, processed_img in methods:
            ocr_data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
            
            # First, check if we found the 25 tool calls text
            found_limit_text = False
            limit_text_y = 0
            
            for i in range(len(ocr_data['text'])):
                text = str(ocr_data['text'][i]).strip()
                
                # Look for "25" and check surrounding text
                if '25' in text:
                    # Check surrounding words
                    context = ' '.join([str(ocr_data['text'][j]) for j in range(max(0, i-3), min(len(ocr_data['text']), i+4))])
                    if 'tool' in context.lower() and 'call' in context.lower():
                        found_limit_text = True
                        limit_text_y = ocr_data['top'][i]
                        if VERBOSE:
                            print(f"Found limit text at y={limit_text_y} using {method_name} method")
                        break
            
            if found_limit_text:
                # Now look for resume link near this text
                # Build complete phrases from adjacent words
                for i in range(len(ocr_data['text'])):
                    text = str(ocr_data['text'][i]).strip().lower()
                    
                    # Check if this is "resume"
                    if 'resume' in text:
                        y_pos = ocr_data['top'][i]
                        
                        # Check if it's near the limit text (within 150 pixels)
                        if abs(y_pos - limit_text_y) < 150:
                            # Calculate center of the word "resume"
                            x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                            y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                            
                            if VERBOSE:
                                print(f"✓ Found 'resume' text at ({x}, {y})")
                            
                            # Return absolute screen coordinates
                            return (x + window_offset[0], y + window_offset[1])
        
        # Method 2: Look for blue link color
        if not BACKGROUND_MODE or VERBOSE:
            print("Looking for blue links...")
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        
        # Multiple blue ranges to catch different link colors
        blue_ranges = [
            # Standard web link blue
            ([100, 50, 50], [130, 255, 255]),
            # VS Code/Cursor specific blues
            ([95, 100, 100], [115, 255, 255]),
            # Lighter blue
            ([90, 50, 100], [120, 255, 255]),
        ]
        
        for lower, upper in blue_ranges:
            lower_blue = np.array(lower)
            upper_blue = np.array(upper)
            
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Sort contours by y position (top to bottom)
            contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if size is reasonable for a text link
                if 30 < w < 500 and 8 < h < 60:
                    # Check if this blue region is in the lower half of the screen
                    # (resume link usually appears after the message)
                    if y > screenshot.height * 0.3:
                        # Extract the region to check if it contains the right text
                        roi = img_np[y:y+h, x:x+w]
                        
                        # Convert blue region to grayscale for OCR
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                        
                        # Enhance contrast for better OCR
                        _, roi_thresh = cv2.threshold(roi_gray, 128, 255, cv2.THRESH_BINARY)
                        
                        # Try OCR on this specific region
                        try:
                            text = pytesseract.image_to_string(roi_thresh, config='--psm 8').strip().lower()
                            if VERBOSE:
                                print(f"Blue region at ({x}, {y}) contains text: '{text}'")
                            
                            # Check if this contains "resume"
                            if 'resume' in text:
                                center_x = x + w // 2
                                center_y = y + h // 2
                                
                                if VERBOSE:
                                    print(f"✓ Found 'resume' link at ({center_x}, {center_y})")
                                
                                # Save debug image showing the blue region
                                if DEBUG_SAVE_SCREENSHOTS:
                                    debug_img = img_np.copy()
                                    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                    cv2.putText(debug_img, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                                    self.save_debug_screenshot(Image.fromarray(debug_img), "_blue_region_matched")
                                
                                # Return absolute screen coordinates
                                return (center_x + window_offset[0], center_y + window_offset[1])
                        except:
                            # If OCR fails on this region, continue to next
                            pass
        
        # Method 3: Pattern matching for text layout
        # Sometimes the resume link appears as regular text, not blue
        if not BACKGROUND_MODE or VERBOSE:
            print("Looking for text pattern...")
        
        # Look for any clickable text after the 25 tool calls message
        if found_limit_text:
            # Find all text below the limit message
            clickable_candidates = []
            
            for i in range(len(ocr_data['text'])):
                if ocr_data['top'][i] > limit_text_y + 20:  # Below the limit text
                    text = str(ocr_data['text'][i]).strip()
                    if len(text) > 3:  # Ignore very short text
                        x = ocr_data['left'][i] + ocr_data['width'][i] // 2
                        y = ocr_data['top'][i] + ocr_data['height'][i] // 2
                        clickable_candidates.append((x + window_offset[0], y + window_offset[1], text))
            
            # Try clicking on the first substantial text below the message
            if clickable_candidates:
                x, y, text = clickable_candidates[0]
                if VERBOSE:
                    print(f"Attempting to click on text: '{text}' at ({x}, {y})")
                return (x, y)
        
        return None
    
    def click_at_position(self, x, y):
        """Click at the specified position"""
        if VERBOSE:
            print(f"Moving to ({x}, {y}) and clicking...")
        
        # Move to position first
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.1)  # Small pause
        
        # Click
        pyautogui.click()
        
        # Alternative: try double-click if single doesn't work
        # pyautogui.doubleClick()
    
    def try_keyboard_navigation(self):
        """Try to navigate to the link using keyboard"""
        if VERBOSE:
            print("Trying keyboard navigation...")
        
        # Press Tab multiple times to navigate to the link
        for i in range(30):
            pyautogui.press('tab')
            time.sleep(0.05)
        
        # Press Enter
        pyautogui.press('enter')
    
    def monitor_and_click(self):
        """Main monitoring loop"""
        print("Cursor Resumer Monitor Started")
        if BACKGROUND_MODE:
            print("Running in background mode - Cursor won't be brought to front until resume is found")
        print(f"Checking every {CHECK_INTERVAL} second{'s' if CHECK_INTERVAL != 1 else ''}")
        print("Press Ctrl+C to stop\n")
        
        consecutive_finds = 0
        
        while True:
            try:
                if not self.is_cursor_running():
                    if VERBOSE and not BACKGROUND_MODE:
                        print("Cursor not running. Waiting...")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Check minimum time between clicks
                current_time = time.time()
                if current_time - self.last_click_time < MIN_CLICK_INTERVAL:
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                # Capture screenshot WITHOUT bringing Cursor to front
                screenshot, window_offset = self.capture_cursor_window()
                
                # Try comprehensive search
                position = self.find_resume_button_comprehensive(screenshot, window_offset)
                
                if position:
                    # Only bring Cursor to front when we need to click
                    if VERBOSE:
                        print("Found resume button! Bringing Cursor to front...")
                    self.bring_cursor_to_front()
                    time.sleep(0.5)  # Brief pause to ensure window is active
                    
                    self.click_at_position(position[0], position[1])
                    self.click_count += 1
                    self.last_click_time = current_time
                    print(f"✅ Clicked resume button! (Total: {self.click_count})")
                    consecutive_finds = 0
                    time.sleep(5)  # Wait after successful click
                else:
                    # If we've found the text multiple times but can't click,
                    # try keyboard navigation as fallback
                    if consecutive_finds > 3:
                        if VERBOSE:
                            print("Multiple finds without successful click, trying keyboard navigation...")
                        self.try_keyboard_navigation()
                        consecutive_finds = 0
                        self.last_click_time = current_time
                        time.sleep(5)
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n\nStopping monitor...")
                break
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(CHECK_INTERVAL)

def main():
    # Parse command line arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Cursor Resumer Script")
        print("\nUsage: python3 cursor_resumer.py [options]")
        print("\nOptions:")
        print("  -h, --help     Show this help message")
        print("  -q, --quiet    Disable verbose output")
        print("  --no-debug     Disable debug screenshot saving")
        sys.exit(0)
    
    if '--quiet' in sys.argv or '-q' in sys.argv:
        global VERBOSE
        VERBOSE = False
    
    if '--no-debug' in sys.argv:
        global DEBUG_SAVE_SCREENSHOTS
        DEBUG_SAVE_SCREENSHOTS = False
    
    # Create and run monitor
    monitor = CursorResumer()
    
    try:
        monitor.monitor_and_click()
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        print(f"Total resumes: {monitor.click_count}")

if __name__ == "__main__":
    main()
