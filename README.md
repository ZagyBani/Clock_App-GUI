# Clock App (KAVASRI)

**Short summary**  
A cross-platform Python desktop app that provides an analog & digital clock, stopwatch, countdown timer, and timezone viewer. Designed for lightweight, real-time time management and productivity tracking with a modern Tkinter interface.

## Key features
- Real-time analog clock with smooth hand movements
- Digital clock with current date display
- Stopwatch with start, stop, reset, and resume functions
- Countdown timer with customizable hours, minutes, and seconds
- Timezone viewer for global time conversions using `pytz`
- Lightweight, dependency-minimal Tkinter UI with a clean modern theme (`clam`)
- Fast updates every 100ms for smooth clock and stopwatch animations

## Requirements
- Python 3.8+ (3.10+ recommended)  
- `pip` package manager  
- See `requirements.txt` for pip-installable dependencies (`pytz`)  

## Quick install
```bash
# create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the app
python main.py
