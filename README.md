# Speed Reader Pro

A modern speed reading application that uses the RSVP (Rapid Serial Visual Presentation) technique to help you read faster and more efficiently. By presenting words one at a time in a fixed position, RSVP eliminates the need for eye movement, allowing you to focus entirely on comprehension.

## What is RSVP?

RSVP is a speed reading technique that displays words sequentially in a fixed position on the screen. This method:
- Eliminates eye movement (saccades) which is a major bottleneck in traditional reading
- Forces your brain to process words at a consistent pace
- Reduces subvocalization (inner voice) by presenting words too quickly to pronounce them
- Helps you break the habit of regression (re-reading words)

## Features

- RSVP reading mode with adjustable speed (words per minute)
- Multiple reading modes:
  - Word-by-word (RSVP)
  - Sentence-by-sentence
  - Paragraph-by-paragraph
- Text-to-speech support with adjustable rate and voice selection
- Customizable themes and colors
- Reading statistics and progress tracking
- Bookmark support
- Library management
- Multiple display modes:
  - Standard: Clean, centered text
  - Focus: Highlights the middle character for optimal fixation
  - Dynamic: Adjusts text size based on word length
- Keyboard shortcuts

## Installation

### Method 1: Quick Install (Recommended)

1. Download the latest release
2. Run `setup.bat` to install the application and create a desktop shortcut
3. Double-click the desktop shortcut or run `run_speedreader.bat` to start the application

### Method 2: Manual Installation

1. Make sure you have Python 3.8 or higher installed
2. Install the required packages:
   ```bash
   pip install customtkinter pyttsx3
   ```
3. Run the application:
   ```bash
   python src/speedreader.py
   ```

### Method 3: Development Installation

1. Clone the repository
2. Install the package in development mode:
   ```bash
   pip install -e .
   ```
3. Run the application:
   ```bash
   speedreader
   ```

## Usage

1. Click "Import" to load a text file
2. Start with a comfortable speed (around 200-300 WPM)
3. Choose your preferred reading mode:
   - Word-by-word (RSVP): Best for speed training
   - Sentence-by-sentence: Good for comprehension
   - Paragraph-by-paragraph: Useful for overview
4. Enable text-to-speech if desired
5. Press SPACE to start/stop reading
6. Use LEFT/RIGHT arrow keys to navigate manually
7. Press ESC to stop reading

## Tips for Effective RSVP Reading

1. Start with a comfortable speed and gradually increase it
2. Focus on the center of the screen where words appear
3. Try to suppress subvocalization (inner voice)
4. Use the Focus mode to train your eyes to stay centered
5. Practice regularly to improve your reading speed
6. Monitor your comprehension and adjust speed accordingly

## Keyboard Shortcuts

- SPACE: Start/Stop reading
- ESC: Stop reading
- LEFT ARROW: Previous word
- RIGHT ARROW: Next word

## Requirements

- Python 3.8 or higher
- Windows 10 or higher (for text-to-speech support)
- Required Python packages:
  - customtkinter >= 5.2.2
  - pyttsx3 >= 2.90
  - pillow >= 10.0.0
  - darkdetect >= 0.8.0
  - packaging >= 24.1

## Troubleshooting

If you encounter any issues:

1. Make sure Python is installed and added to your system PATH
2. Try running `setup.bat` again to reinstall dependencies
3. Try reinstalling the required packages manually:
   ```bash
   pip install --upgrade customtkinter pyttsx3
   ```
4. Check if your text file is properly encoded (UTF-8 recommended)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 