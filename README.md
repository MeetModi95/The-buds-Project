# Sonic Voice Studio II

Sonic Voice Studio II is a production-grade, offline voice command control software designed to trigger keyboard and media shortcuts using localized speech recognition. It ensures absolute privacy and minimal latency by running entirely on your local machine using the Vosk speech recognition engine.

## 🚀 Features

- **Offline Speech Recognition**: Powered by the lightweight Vosk ML engine, meaning no audio data is ever sent to the cloud.
- **Modern User Interface**: A sleek, dark-themed dashboard built with `customtkinter`.
- **Modular Architecture**: Clean separation between UI components and backend audio processing, allowing for easy expansion and testing.
- **Customizable Profiles & Commands**: Seamlessly switch between different environments (e.g., Gaming, Productivity) with adjustable sensitivity thresholds.
- **Media Control**: Out-of-the-box support for media playback, next/previous tracks, and volume controls via `pynput`.
- **Standalone Executable**: Easy distribution on Windows via PyInstaller bundling.

## 🛠️ Prerequisites

- **Python 3.8+**
- A working microphone
- The Vosk English Model: Download a Vosk model (e.g., `vosk-model-small-en-us-0.15`) and place its contents into a folder named `model` in the root of the project.

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sonic-voice-studio.git
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

To compile the application into a single standalone `.exe` using PyInstaller:

```bash
python build.py
```

The resulting executable will be found in the `dist/` directory. The build script automatically packages the `customtkinter` assets and attempts to bundle the `model/` directory.

## 📄 Documentation

For a detailed breakdown of the application structure, see [ARCHITECTURE.md](ARCHITECTURE.md).

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.
