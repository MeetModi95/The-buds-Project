"""
SONIC VOICE STUDIO — Main Window
Root application window with sidebar navigation and page management.
Orchestrates the engine, audio manager, command processor, and all UI pages.
"""

import customtkinter as ctk
import os
import sys
import json
import copy
import shutil

from app.theme import Colors, Fonts, Sizes, AppConfig
from app.components.background_canvas import BackgroundCanvas
from app.components.sidebar import Sidebar
from app.pages.dashboard import DashboardPage
from app.pages.commands import CommandsPage
from app.pages.audio import AudioPage
from app.pages.profiles import ProfilesPage
from app.pages.settings import SettingsPage
from app.engine.audio_manager import AudioManager
from app.engine.voice_engine import VoiceEngine
from app.engine.command_processor import CommandProcessor


def _get_base_path():
    """Return the base path for bundled resources (PyInstaller support)."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MainWindow(ctk.CTk):
    """
    Main application window — ties together sidebar, pages, and engine backend.
    """

    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title(AppConfig.WINDOW_TITLE)
        self.geometry(f"{Sizes.WINDOW_WIDTH}x{Sizes.WINDOW_HEIGHT}")
        self.minsize(Sizes.WINDOW_MIN_WIDTH, Sizes.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_ROOT)

        # --- Appearance ---
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # --- Engine Backend ---
        self.audio_manager = AudioManager()
        self.command_processor = CommandProcessor()
        self.voice_engine = VoiceEngine(self.audio_manager)

        # Wire up engine callbacks
        self.voice_engine.on_result = self._on_voice_result
        self.voice_engine.on_status = self._on_engine_status
        self.voice_engine.on_error = self._on_engine_error

        # --- Profile State ---
        _base = _get_base_path()
        self._profiles_dir = os.path.join(_base, "data", "profiles")
        self._default_profile_path = os.path.join(_base, "data", "default_profile.json")
        self._active_profile_name = "Default"
        self._engine_active = False

        # Ensure profiles directory exists
        os.makedirs(self._profiles_dir, exist_ok=True)

        # Copy default profile if no profiles exist
        if not os.listdir(self._profiles_dir):
            default_dest = os.path.join(self._profiles_dir, "Default.json")
            if os.path.exists(self._default_profile_path):
                shutil.copy2(self._default_profile_path, default_dest)

        # --- Build UI ---
        self._build_layout()

        # --- Initialize ---
        self._load_profile("Default")
        self._load_voice_model()

        # Navigate to dashboard
        self._sidebar.set_active_page("dashboard")
        self._show_page("dashboard")

        # Refresh devices on audio page
        self.after(500, lambda: self._pages["audio"]._refresh_devices())

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        """Build the main layout: sidebar + content area."""

        # --- Liquid Gradient Backdrop ---
        self._background = BackgroundCanvas(self)
        self._background.place(x=0, y=0, relwidth=1, relheight=1)
        self._background.tk.call("lower", self._background._w)

        # --- Sidebar ---
        self._sidebar = Sidebar(self,
                                 on_navigate=self._show_page,
                                 on_engine_toggle=self._toggle_engine)
        self._sidebar.pack(side="left", fill="y")

        # --- Content Area ---
        self._content_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0,
                                           border_width=0)
        self._content_frame.pack(side="right", fill="both", expand=True)

        # --- Pages ---
        self._pages = {}
        self._current_page = None

        # Create all pages (they are layered transparently on top of the content frame)
        self._pages["dashboard"] = DashboardPage(self._content_frame, app_state=self)
        self._pages["commands"] = CommandsPage(self._content_frame, app_state=self)
        self._pages["audio"] = AudioPage(self._content_frame, app_state=self)
        self._pages["profiles"] = ProfilesPage(self._content_frame, app_state=self)
        self._pages["settings"] = SettingsPage(self._content_frame, app_state=self)

    def _show_page(self, page_key):
        """Switch the visible page."""
        # Hide current page
        if self._current_page and self._current_page in self._pages:
            self._pages[self._current_page].pack_forget()

        # Show new page
        if page_key in self._pages:
            self._pages[page_key].pack(fill="both", expand=True)
            self._current_page = page_key

            # Page-specific refresh actions
            if page_key == "profiles":
                self._refresh_profiles_page()
            elif page_key == "audio":
                self._pages["audio"].set_engine_active(self._engine_active)

    # --- Engine Control ---

    def _load_voice_model(self):
        """Load the Vosk model."""
        model_path = os.path.join(_get_base_path(), "model")
        # Check if settings page has a custom path
        if "settings" in self._pages:
            try:
                custom_path = self._pages["settings"].get_model_path()
                if custom_path and os.path.exists(custom_path):
                    model_path = custom_path
            except Exception:
                pass

        success = self.voice_engine.load_model(model_path)
        self._sidebar.set_engine_status(False, model_loaded=success)

    def _toggle_engine(self, start: bool):
        """Toggle the voice engine on/off."""
        if start:
            if not self.voice_engine.model_loaded:
                self._on_engine_error("Cannot start: model not loaded.")
                self._sidebar.set_engine_status(False, model_loaded=False)
                return

            # Rebuild grammar from current commands
            grammar = self.command_processor.get_grammar_list()
            self.voice_engine.set_grammar(grammar)
            if self.voice_engine.start():
                self._engine_active = True
                self._sidebar.set_engine_status(True)
                self._pages["dashboard"].set_engine_status(True)
                if self._current_page == "audio":
                    self._pages["audio"].set_engine_active(True)
            else:
                self._engine_active = False
                self._sidebar.set_engine_status(False)
                self._pages["dashboard"].set_engine_status(False)
                if self._current_page == "audio":
                    self._pages["audio"].set_engine_active(False)
        else:
            self.voice_engine.stop()
            self._engine_active = False
            self._sidebar.set_engine_status(False)
            self._pages["dashboard"].set_engine_status(False)
            if self._current_page == "audio":
                self._pages["audio"].set_engine_active(False)

    def _on_voice_result(self, text):
        """Called from engine thread when speech is recognized."""
        self.after(0, self._process_voice_result, text)

    def _process_voice_result(self, text):
        """Process recognized text on the UI thread."""
        result = self.command_processor.process(text)
        if result:
            phrase, action = result
            self._pages["dashboard"].log_command(phrase, action)
        else:
            # Log the unmatched text
            self._pages["dashboard"].log_status(f"Heard: \"{text}\" (no match)")

    def _on_engine_status(self, msg):
        """Status message from engine."""
        self.after(0, lambda: self._pages["dashboard"].log_status(msg))

    def _on_engine_error(self, msg):
        """Error message from engine."""
        self.after(0, lambda: self._pages["dashboard"].log_status(f"⚠ {msg}"))

    # --- Profile Management ---

    def _get_profile_path(self, name):
        return os.path.join(self._profiles_dir, f"{name}.json")

    def _list_profiles(self):
        """List all profile names from the profiles directory."""
        profiles = []
        if os.path.exists(self._profiles_dir):
            for f in os.listdir(self._profiles_dir):
                if f.endswith('.json'):
                    profiles.append(f[:-5])  # strip .json
        if not profiles:
            profiles = ["Default"]
        return sorted(profiles)

    def _load_profile(self, name):
        """Load a profile by name."""
        path = self._get_profile_path(name)
        if not os.path.exists(path):
            # Try default
            if os.path.exists(self._default_profile_path):
                path = self._default_profile_path
            else:
                return

        try:
            data = self.command_processor.load_profile(path)
            self._active_profile_name = name

            # Update commands page
            self._pages["commands"].load_commands(self.command_processor.commands)

            # Update audio page
            audio_settings = data.get('audio', {})
            self._pages["audio"].load_settings(audio_settings)

            # Update dashboard
            self._pages["dashboard"].set_profile_name(name)
            self._pages["dashboard"].log_status(f"Profile loaded: {name}")

            # Rebuild grammar if engine is running
            if self._engine_active:
                grammar = self.command_processor.get_grammar_list()
                self.voice_engine.set_grammar(grammar)

        except Exception as e:
            self._pages["dashboard"].log_status(f"⚠ Failed to load profile: {str(e)}")

    def save_commands(self, commands):
        """Save commands from the commands page to the active profile."""
        # Update the command processor
        self.command_processor._commands = commands
        self.command_processor.profile_name = self._active_profile_name

        # Get audio settings from audio page
        audio_settings = self._pages["audio"].get_settings()

        # Save to file
        path = self._get_profile_path(self._active_profile_name)
        self.command_processor.save_profile(path, audio_settings)

        # Rebuild grammar
        if self._engine_active:
            grammar = self.command_processor.get_grammar_list()
            self.voice_engine.set_grammar(grammar)

        self._pages["dashboard"].log_status(f"Profile saved: {self._active_profile_name}")

    def switch_profile(self, name):
        """Switch to a different profile."""
        was_active = self._engine_active
        if was_active:
            self._toggle_engine(False)

        self._load_profile(name)
        self._refresh_profiles_page()

        if was_active:
            self._toggle_engine(True)

    def create_profile(self, name):
        """Create a new profile with default settings."""
        path = self._get_profile_path(name)
        if os.path.exists(path):
            self._pages["dashboard"].log_status(f"⚠ Profile '{name}' already exists")
            return

        # Copy default profile
        if os.path.exists(self._default_profile_path):
            shutil.copy2(self._default_profile_path, path)
            # Update the name in the copied file
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['name'] = name
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        else:
            # Create minimal profile
            data = {'name': name, 'commands': [], 'audio': {}}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

        self._pages["dashboard"].log_status(f"Profile created: {name}")
        self._refresh_profiles_page()

    def delete_profile(self, name):
        """Delete a profile (can't delete active profile)."""
        if name == self._active_profile_name:
            self._pages["dashboard"].log_status("⚠ Cannot delete active profile")
            return
        path = self._get_profile_path(name)
        if os.path.exists(path):
            os.remove(path)
            self._pages["dashboard"].log_status(f"Profile deleted: {name}")
        self._refresh_profiles_page()

    def duplicate_profile(self, name):
        """Duplicate a profile."""
        src_path = self._get_profile_path(name)
        new_name = f"{name} Copy"
        counter = 1
        while os.path.exists(self._get_profile_path(new_name)):
            counter += 1
            new_name = f"{name} Copy {counter}"

        dest_path = self._get_profile_path(new_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            with open(dest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['name'] = new_name
            with open(dest_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

        self._pages["dashboard"].log_status(f"Profile duplicated: {new_name}")
        self._refresh_profiles_page()

    def import_profile(self, filepath):
        """Import a profile from an external JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            name = data.get('name', os.path.splitext(os.path.basename(filepath))[0])
            dest = self._get_profile_path(name)
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            self._pages["dashboard"].log_status(f"Profile imported: {name}")
            self._refresh_profiles_page()
        except Exception as e:
            self._pages["dashboard"].log_status(f"⚠ Import failed: {str(e)}")

    def export_profile(self, filepath):
        """Export the active profile to a file."""
        src = self._get_profile_path(self._active_profile_name)
        if os.path.exists(src):
            shutil.copy2(src, filepath)
            self._pages["dashboard"].log_status(f"Profile exported: {filepath}")

    def _refresh_profiles_page(self):
        """Refresh the profiles page with current data."""
        profiles = self._list_profiles()
        self._pages["profiles"].refresh_profiles(profiles, self._active_profile_name)

    # --- Window Lifecycle ---

    def _on_close(self):
        """Clean shutdown."""
        if self._engine_active:
            self.voice_engine.stop()
        self.destroy()
