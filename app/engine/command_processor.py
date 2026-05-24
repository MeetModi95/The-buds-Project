"""
SONIC VOICE STUDIO — Command Processor
Maps recognized voice phrases to keyboard/media/app launch actions.
Supports media keys, single key taps, key combos, URLs, and app paths.
"""

import json
import os
import shutil
import subprocess
import time
import copy
import webbrowser
from pynput.keyboard import Key, Controller, KeyCode


class CommandProcessor:
    """Processes recognized voice text and executes mapped keyboard actions."""

    # Map of action_value strings → pynput Key objects for media keys
    MEDIA_KEY_MAP = {
        'media_play_pause': Key.media_play_pause,
        'media_next': Key.media_next,
        'media_previous': Key.media_previous,
        'media_volume_up': Key.media_volume_up,
        'media_volume_down': Key.media_volume_down,
        'media_volume_mute': Key.media_volume_mute,
    }

    # Map for modifier keys
    MODIFIER_MAP = {
        'ctrl': Key.ctrl_l,
        'control': Key.ctrl_l,
        'shift': Key.shift_l,
        'alt': Key.alt_l,
        'win': Key.cmd,
        'super': Key.cmd,
        'tab': Key.tab,
        'enter': Key.enter,
        'return': Key.enter,
        'escape': Key.esc,
        'esc': Key.esc,
        'space': Key.space,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'home': Key.home,
        'end': Key.end,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
        'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
        'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
    }

    def __init__(self):
        self.keyboard = Controller()
        self._commands = []
        self._cooldown_seconds = 0.5
        self._last_command_time = 0
        self._profile_name = "Default"
        self._on_command_executed = None  # Callback: (phrase, action_value) -> None

    # --- Profile Loading ---

    def load_profile(self, filepath):
        """Load a command profile from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._profile_name = data.get('name', 'Unnamed')
        self._commands = data.get('commands', [])
        audio_settings = data.get('audio', {})
        self._cooldown_seconds = audio_settings.get('cooldown_seconds', 0.5)
        return data

    def save_profile(self, filepath, audio_settings=None):
        """Save the current command set to a JSON file."""
        data = {
            'name': self._profile_name,
            'commands': self._commands,
            'audio': audio_settings or {
                'gate_level': 0.8,
                'confidence_threshold': 0.5,
                'cooldown_seconds': self._cooldown_seconds,
                'input_device': None
            }
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # --- Command Management ---

    @property
    def commands(self):
        return copy.deepcopy(self._commands)

    @property
    def profile_name(self):
        return self._profile_name

    @profile_name.setter
    def profile_name(self, value):
        self._profile_name = value

    @property
    def cooldown(self):
        return self._cooldown_seconds

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown_seconds = max(0.0, float(value))

    def set_on_command_executed(self, callback):
        """Set a callback invoked when a command fires: callback(phrase, action_value)"""
        self._on_command_executed = callback

    def add_command(self, phrase, action_type, action_value, enabled=True):
        """Add a new voice command mapping."""
        self._commands.append({
            'phrase': phrase.strip().lower(),
            'action_type': action_type,
            'action_value': action_value,
            'enabled': enabled
        })

    def remove_command(self, index):
        """Remove a command by index."""
        if 0 <= index < len(self._commands):
            self._commands.pop(index)

    def update_command(self, index, phrase=None, action_type=None, action_value=None, enabled=None):
        """Update fields of an existing command."""
        if 0 <= index < len(self._commands):
            cmd = self._commands[index]
            if phrase is not None:
                cmd['phrase'] = phrase.strip().lower()
            if action_type is not None:
                cmd['action_type'] = action_type
            if action_value is not None:
                cmd['action_value'] = action_value
            if enabled is not None:
                cmd['enabled'] = enabled

    def get_grammar_list(self):
        """Build the Vosk grammar JSON string from active commands."""
        phrases = [cmd['phrase'] for cmd in self._commands if cmd.get('enabled', True)]
        phrases.append('[unk]')
        return json.dumps(phrases)

    # --- Command Execution ---

    def process(self, text):
        """
        Match recognized text against command list and execute.
        Returns (matched_phrase, action_value) or None if no match / cooldown.
        """
        now = time.time()
        if now - self._last_command_time < self._cooldown_seconds:
            return None

        cleaned = text.strip().lower()
        for cmd in self._commands:
            if not cmd.get('enabled', True):
                continue
            if cmd['phrase'] in cleaned:
                action_type = cmd['action_type']
                action_value = cmd['action_value']
                self._execute_action(action_type, action_value)
                self._last_command_time = now
                if self._on_command_executed:
                    self._on_command_executed(cmd['phrase'], action_value)
                return (cmd['phrase'], action_value)
        return None

    def _execute_action(self, action_type, action_value):
        """Execute a single action based on type."""
        if action_type == 'media_key':
            key = self.MEDIA_KEY_MAP.get(action_value)
            if key:
                self.keyboard.press(key)
                self.keyboard.release(key)

        elif action_type == 'key_combo':
            # Format: "ctrl+shift+n" or "alt+f4"
            keys = self._parse_key_combo(action_value)
            if keys:
                for k in keys:
                    self.keyboard.press(k)
                for k in reversed(keys):
                    self.keyboard.release(k)

        elif action_type == 'key_tap':
            # Single key press, e.g. "a", "enter", "f5"
            key = self._resolve_single_key(action_value)
            if key:
                self.keyboard.press(key)
                self.keyboard.release(key)

        elif action_type == 'open_app':
            self._open_app(action_value)

        elif action_type == 'open_url':
            webbrowser.open(action_value)

    def _open_app(self, app_target):
        """
        Launch an app by executable name, full path, folder, document, or alias.
        Executables are started with shell=False; paths use Windows association.
        """
        target = app_target.strip().strip('"')
        if not target:
            return

        if target.startswith(("http://", "https://")):
            webbrowser.open(target)
            return

        aliases = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "edge": "msedge.exe",
            "microsoft edge": "msedge.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "explorer": "explorer.exe",
        }
        lookup_target = aliases.get(target.lower(), target)

        if os.path.exists(lookup_target):
            os.startfile(lookup_target)
            return

        resolved = shutil.which(lookup_target)
        if not resolved and lookup_target.lower() == "chrome.exe":
            resolved = self._find_common_chrome_path()

        if resolved:
            subprocess.Popen([resolved], shell=False)
            return

        os.startfile(lookup_target)

    def _find_common_chrome_path(self):
        """Return a common Chrome install path if it exists."""
        candidates = [
            os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LocalAppData", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return None

    def _parse_key_combo(self, combo_str):
        """Parse 'ctrl+shift+n' into a list of pynput keys."""
        parts = [p.strip().lower() for p in combo_str.split('+')]
        keys = []
        for part in parts:
            key = self._resolve_single_key(part)
            if key:
                keys.append(key)
        return keys

    def _resolve_single_key(self, key_str):
        """Resolve a key string to a pynput Key or KeyCode."""
        key_str = key_str.strip().lower()
        if key_str in self.MODIFIER_MAP:
            return self.MODIFIER_MAP[key_str]
        if len(key_str) == 1:
            return KeyCode.from_char(key_str)
        return None
