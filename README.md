# Cursor Resumer

A Python script that automatically detects and clicks the "resume the conversation" button when Cursor AI reaches its 25 tool call limit.

## Overview

This script runs in the background and monitors your Cursor AI editor for the message:
> "Note: By default, we stop the agent after 25 tool calls. You can resume the conversation."

When detected, it automatically clicks the blue "resume" link to continue the AI agent's work without manual intervention.

## Important: Visibility Requirements

For the script to work properly, one of the following conditions must be met:
- **Option 1**: Cursor app is the active window and the chat is visible
- **Option 2**: Cursor's chat tab is visible alongside other apps (split screen, floating window, etc.) and scrolled to show the latest messages

The script needs to be able to see the "resume" button on screen to click it.

## Features

- **Smart Detection**: Uses OCR and color detection to find the resume button
- **Precise Clicking**: Only clicks on blue "resume" text, not random blue elements
- **Background Operation**: Runs quietly without bringing Cursor to front until needed
- **Minimal Output**: Only shows successful clicks in quiet mode
- **No Disk Usage**: Doesn't save screenshots by default to preserve disk space

## Prerequisites

- macOS (uses macOS-specific screenshot and window management)
- Python 3.7+
- Tesseract OCR installed via Homebrew
- Cursor AI editor

## Installation

### Prerequisites

First, install Tesseract OCR:
```bash
brew install tesseract
```

### Option 1: Install from pip

For standard installation:
```bash
pip install cursor-resumer
```

**Note for macOS users with Python 3.11+**: If you encounter an "externally-managed-environment" error, use one of these methods:

**Method A: Virtual Environment (Recommended)**
```bash
python3 -m venv cursor-env
source cursor-env/bin/activate
pip install cursor-resumer
```

**Method B: pipx (Isolated Installation)**
```bash
brew install pipx
pipx install cursor-resumer
```

**Method C: Force Installation (Not Recommended)**
```bash
pip install --break-system-packages cursor-resumer
# OR
pip install --user cursor-resumer
```

### Option 2: Install from source

```bash
# Clone the repository
git clone https://github.com/khaterdev/cursor-resumer
cd cursor-resumer

# Install in development mode
pip install -e .
```

### Option 3: Manual installation with virtual environment

```bash
# Clone the repository
git clone https://github.com/khaterdev/cursor-resumer
cd cursor-resumer

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux

# Install the package
pip install .
```

## Usage

### Basic Usage

After installation, you can run the script from anywhere:

```bash
cursor-resumer
```

Or if running from source:

```bash
python -m cursor_resumer
```

The script will start monitoring:
```
Cursor Resumer Monitor Started
Running in background mode - Cursor won't be brought to front until resume is found
Checking every 1 second
Press Ctrl+C to stop
```

Continue using your computer normally. When Cursor hits the 25 tool limit, the script will automatically click resume:
```
Clicked resume button! (Total: 1)
```

Stop the script with `Ctrl+C`

### Command Line Options

```bash
# Show help
cursor-resumer --help

# Run in verbose mode (shows all detection attempts)
cursor-resumer --verbose

# Enable debug screenshots (saves images to debug_screenshots/)
cursor-resumer --debug

# Run in quiet mode (default)
cursor-resumer --quiet
```

## Configuration

You can modify these settings in the source code (`cursor_resumer/main.py`):

```python
CHECK_INTERVAL = 1  # How often to check (seconds)
MIN_CLICK_INTERVAL = 10  # Minimum seconds between clicks
VERBOSE = False  # Show detailed logging
DEBUG_SAVE_SCREENSHOTS = False  # Save screenshots for debugging
BACKGROUND_MODE = True  # Run quietly in background
```

## How It Works

1. **Window Detection**: Finds the Cursor window position and size
2. **Screenshot Capture**: Takes screenshots of the Cursor window (not the entire screen)
3. **Text Detection**: Uses multiple methods to find the resume button:
   - OCR to find "25 tool calls" message and nearby "resume" text
   - Color detection to find blue link text
   - Pattern matching for text layout
4. **Smart Clicking**: Only activates Cursor and clicks when resume is found

## Troubleshooting

### "externally-managed-environment" Error
This error occurs on macOS with Python 3.11+ due to system Python protection. Solutions:

1. **Use virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install cursor-resumer
   ```

2. **Use pipx**:
   ```bash
   brew install pipx
   pipx install cursor-resumer
   ```

3. **Force install** (not recommended):
   ```bash
   pip install --break-system-packages cursor-resumer
   ```

### "Tesseract is not installed!"
Install Tesseract OCR:
```bash
brew install tesseract
```

### Script doesn't detect the resume button
1. Make sure Cursor window is visible (not minimized)
2. Try running with `--verbose` to see what's being detected
3. Enable debug screenshots with `--debug` to see what the script sees

### Permission errors
Grant Terminal/IDE accessibility permissions:
1. System Preferences → Security & Privacy → Privacy
2. Select Accessibility
3. Add Terminal (or your IDE) to the list

### Script clicks wrong things
The script only clicks on blue text containing "resume". If it's clicking incorrectly:
1. Check that your Cursor theme shows links in blue
2. Adjust the blue color ranges in the script if needed

## Virtual Environment Management

### Activate virtual environment
```bash
source venv/bin/activate
```

### Deactivate virtual environment
```bash
deactivate
```

### Recreate virtual environment
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Development

### Project Structure
```
cursor-resumer/
├── cursor_resumer/
│   ├── __init__.py    # Package initialization
│   └── main.py        # Main script
├── setup.py           # Package setup file
├── pyproject.toml     # Modern Python packaging config
├── requirements.txt   # Python dependencies
├── README.md         # This file
├── LICENSE           # MIT License
└── venv/             # Virtual environment (not in git)
```

### Debug Mode
Run with debug screenshots enabled:
```bash
cursor-resumer --debug
```

This creates a `debug_screenshots/` folder with images showing:
- Original screenshots
- Detected blue regions
- OCR results

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues or pull requests if you find bugs or have improvements!