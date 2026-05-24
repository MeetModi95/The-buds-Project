# Sonic Voice Studio II

Sonic Voice Studio II is a production-grade, offline voice command control software designed to trigger keyboard and media shortcuts using localized speech recognition. It ensures absolute privacy and minimal latency by running entirely on your local machine using the Vosk speech recognition engine.

---

### 🚀 Download Standalone Application
You can download the compiled, pre-packaged Windows executable directly from Google Drive:
👉 **[Download Sonic Voice Studio II (Windows)](https://drive.google.com/file/d/1pg7G3WRWZ3PLaz7oIRKPbZLqBjcc1D8X/view?usp=drive_link)**

*Note: After downloading and extracting the ZIP file, ensure that you keep the `model/` folder in the same directory as `SonicVoiceStudio.exe` to allow the speech recognition engine to function.*

---

## ⚡ Features

- **Offline Speech Recognition**: Powered by the lightweight Vosk ML engine, meaning no audio data is ever sent to the cloud.
- **Modern User Interface**: A sleek, dark-themed dashboard built with `customtkinter`, themed in a premium Apple Music-inspired purple glassmorphism style.
- **Brand Identity**: Features the custom Sonic Voice logo embedded in both the sidebar navigation and the Windows window/taskbar icons.
- **Modular Architecture**: Clean separation between UI components and backend audio processing, allowing for easy expansion and testing.
- **Customizable Profiles & Commands**: Seamlessly switch between different environments (e.g., Gaming, Productivity) with adjustable sensitivity thresholds.
- **Media Control**: Out-of-the-box support for media playback, next/previous tracks, and volume controls via `pynput`.
- **Standalone Executable**: Built and space-optimized via PyInstaller with hidden-import stripping, UPX compression disabled for instant launches, and external model folder loading.

## 🛠️ Prerequisites

- **Python 3.8+** (only if running from source)
- A working microphone
- The Vosk English Model: Download a Vosk model (e.g., `vosk-model-small-en-us-0.15`) and place its contents into a folder named `model` in the root of the project.

## 📦 Installation (from Source)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MeetModi95/The-buds-Project
   cd sonic-voice-studio
   ```

2. **Install dependencies:**
   ```bash
   pip install vosk sounddevice pynput customtkinter numpy Pillow
   ```

3. **Add the Vosk Model:**
   Download the [Vosk English Model](https://alphacephei.com/vosk/models) and extract it to `sonic-voice-studio/model/`.

## 🎮 Usage

Run the main application script:

```bash
python sonic_studio.py
```

*Note: An older monolithic prototype (`buds2.py` / Sonic Voice Studio I) is also included for reference, but `sonic_studio.py` is the main entry point for version II.*

## 🏗️ Building the Executable

To compile the application into a space-optimized standalone `.exe` with instantaneous launch:

```bash
python build.py
```

The build script will:
1. Exclude the massive `model/` folder from inside the executable to save size and boot time.
2. Automatically copy the `model/` folder to the output `dist/` directory.
3. Package the `sonic logo.png` asset and required customtkinter libraries.
4. Exclude large unused Python libraries (like `matplotlib`, `scipy`, `pandas`, `IPython`, etc.).
5. Disable UPX compression to ensure zero-lag instant OS launching.

The compiled executable and its dependent model folder will be found in the `dist/` directory.

## 📄 Documentation

For a detailed breakdown of the application structure and compilation setup, see [ARCHITECTURE.md](ARCHITECTURE.md).

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.
