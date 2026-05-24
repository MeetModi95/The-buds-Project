# Architecture & Project Structure

Sonic Voice Studio II follows a modular, Model-View-Controller (MVC) inspired architecture. The separation of concerns ensures that the user interface operates smoothly alongside the real-time audio processing threads.

## Directory Layout

```text
.
├── app/
│   ├── components/       # Reusable CustomTkinter UI widgets
│   ├── engine/           # Backend processing and core logic
│   │   ├── audio_manager.py     # Handles the PyAudio/sounddevice streams
│   │   ├── command_processor.py # Maps recognized text to system actions (pynput)
│   │   └── voice_engine.py      # Manages the Vosk ML model and inference logic
│   ├── pages/            # Individual screens for the UI
│   │   ├── audio.py             # Audio device selection and tuning
│   │   ├── commands.py          # Command mapping and editing
│   │   ├── dashboard.py         # Main status screen
│   │   ├── profiles.py          # Environment profiles (Gaming, Work, etc.)
│   │   └── settings.py          # Global app settings
│   ├── main_window.py    # The root CustomTkinter application window
│   ├── theme.py          # UI color palettes and styling configurations
│   └── __init__.py
├── build/                # PyInstaller build artifacts (generated)
├── data/                 # Application data (saved profiles, config JSONs)
├── dist/                 # Final compiled executables (generated)
├── model/                # Vosk ML offline speech model (User provided)
├── buds2.py              # Legacy prototype (Sonic Voice Studio I)
├── build.py              # PyInstaller build orchestration script
├── sonic_studio.py       # Main Application Entry Point
└── README.md             # Project overview
```

## Core Components

### 1. The Entry Point (`sonic_studio.py`)
This script initializes the path, checks for bundled PyInstaller directories (`sys._MEIPASS`), and launches the `MainWindow` loop.

### 2. The User Interface (`app/`)
Built entirely in `customtkinter`, the UI uses a containerized frame approach. 
- `MainWindow` manages navigation and swaps out frames from the `app/pages/` directory.
- `theme.py` ensures a consistent dark mode aesthetic.
- The UI safely communicates with the audio threads without blocking the main event loop (`mainloop`).

### 3. The Audio Pipeline (`app/engine/`)
This is the heart of the application:
1. **AudioManager (`audio_manager.py`)**: Uses `sounddevice` to open a raw audio input stream. Audio frames are captured in a background thread and placed into a thread-safe Queue.
2. **VoiceEngine (`voice_engine.py`)**: Consumes the audio Queue, feeding chunks of byte data into `KaldiRecognizer.AcceptWaveform()`. When a phrase is finalized, it passes the text string to the `CommandProcessor`.
3. **CommandProcessor (`command_processor.py`)**: Receives strings (e.g., "play music") and uses `pynput.keyboard` controllers to simulate physical keystrokes and media hotkeys.

## Build System (`build.py`)

A custom wrapper around PyInstaller. It ensures `customtkinter` assets are dynamically located and bundled via `--add-data`. It also packages `sounddevice` and `pynput` as hidden imports to ensure the compiled `.exe` runs silently and efficiently on any Windows machine, without requiring Python to be installed.
