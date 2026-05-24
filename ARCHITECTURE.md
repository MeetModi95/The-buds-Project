# Architecture & Project Structure

Sonic Voice Studio II follows a modular, Model-View-Controller (MVC) inspired architecture. The separation of concerns ensures that the user interface operates smoothly alongside the real-time audio processing threads.

## Directory Layout

```text
.
├── app/
│   ├── components/       # Reusable CustomTkinter UI widgets
│   │   ├── background_canvas.py
│   │   ├── sidebar.py           # Left sidebar navigation (renders brand logo)
│   │   └── ...
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
│   ├── main_window.py    # The root CustomTkinter application window (sets window/taskbar icons)
│   ├── theme.py          # UI color palettes and styling configurations
│   └── __init__.py
├── build/                # PyInstaller build artifacts (generated)
├── data/                 # Application data (saved profiles, config JSONs)
├── dist/                 # Final compiled executables (generated)
│   ├── model/            # Speech recognition model copied adjacent to EXE
│   ├── SonicVoiceStudio.exe
│   └── sonic logo.png
├── model/                # Vosk ML offline speech model (User provided)
├── buds2.py              # Legacy prototype (Sonic Voice Studio I)
├── build.py              # PyInstaller build orchestration script
├── sonic logo.png        # Custom brand logo image
├── sonic_studio.py       # Main Application Entry Point
└── README.md             # Project overview & download instructions
```

## Core Components & Key Implementations

### 1. The Entry Point (`sonic_studio.py`)
This script initializes the path, check for bundled PyInstaller directories (`sys._MEIPASS`), and launches the `MainWindow` loop.

### 2. The User Interface (`app/`)
Built entirely in `customtkinter`, the UI uses a containerized frame approach. 
- `MainWindow` manages navigation and swaps out frames from the `app/pages/` directory.
- `theme.py` ensures a consistent dark mode aesthetic (Apple Music-inspired purple glassmorphism).
- **Logo Integration**: 
  - `MainWindow` sets `sonic logo.png` as the application-wide icon (`wm_iconphoto`) and assigns a Windows AppUserModelID using `ctypes` so the custom logo is grouped correctly on the Windows taskbar.
  - `Sidebar` loads `sonic logo.png` using PIL and CustomTkinter's `CTkImage` at 32x32 size, packing it next to the brand title text in the sidebar brand frame.
- The UI safely communicates with the audio threads without blocking the main event loop (`mainloop`).

### 3. The Audio Pipeline & Vosk Model Loading (`app/engine/`)
This is the heart of the application:
1. **AudioManager (`audio_manager.py`)**: Uses `sounddevice` to open a raw audio input stream. Audio frames are captured in a background thread and placed into a thread-safe Queue.
2. **VoiceEngine (`voice_engine.py`)**: Consumes the audio Queue, feeding chunks of byte data into `KaldiRecognizer.AcceptWaveform()`. When a phrase is finalized, it passes the text string to the `CommandProcessor`.
3. **Vosk Model Location**: To keep the compiled size small and ensure **instantaneous launch speed**, the Vosk ML speech model folder (`model/`) is not bundled inside the single executable. At runtime, the application resolves the path to load the model:
   - Check if frozen (`getattr(sys, 'frozen', False)`). If yes, it loads from the folder adjacent to the running executable (`os.path.dirname(sys.executable)`).
   - If not frozen, it looks for the folder adjacent to the source tree root.
   - If both fail, it falls back to the temp directory resource path (`sys._MEIPASS`).
4. **CommandProcessor (`command_processor.py`)**: Receives strings (e.g., "play music") and uses `pynput.keyboard` controllers to simulate physical keystrokes and media hotkeys.

## Build System & Compilation Optimization (`build.py`)

A custom wrapper around PyInstaller optimized for size and startup speed:
- **Logo Packing**: Bundles `sonic logo.png` into the root of the executable's virtual environment (`sys._MEIPASS`) so the UI can load it on any client machine out of the box.
- **Model Copying**: Avoids packing the massive `model/` folder inside the single EXE. Instead, it copies the `model/` directory adjacent to the binary in `dist/model/` at build time. This avoids extraction latency at launch.
- **Module Exclusions**: Shrinks final file size down to **44.5 MB** by explicitly excluding heavy unused libraries (like `matplotlib`, `scipy`, `pandas`, `IPython`, `notebook`, `sqlite3`, etc.) which might otherwise be auto-analyzed and bundled.
- **Instant Launch**: Utilizes the `--noupx` argument to disable UPX compression, eliminating the OS decompression delay when launching the program on Windows.
