# MusicChecker

MusicChecker is a tool for detecting and quarantining silent or whisper-level audio files.  
It comes with two versions:

- **music_checker_gui**: A graphical interface using Tkinter.  
- **music_checker_cli**: A command-line version for batch scanning.

## Installation

1. Clone the repository or download the archive.  
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Version
```bash
python music_checker_gui/music_checker_gui.py
```

### CLI Version
```bash
python music_checker_cli/music_checker_cli.py
```

## Output
- A report (`silent_music_report.txt`) is created in the scanned folder.  
- Silent files are moved into a `Quarantine_Silent` subfolder.  

## License
MIT License (add LICENSE file on GitHub).

