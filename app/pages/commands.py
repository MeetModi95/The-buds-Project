"""
SONIC VOICE STUDIO — Commands Page
Voice command ↔ action mapping editor with add/remove/edit capabilities.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Sizes
from app.components.command_row import CommandRow


class CommandsPage(ctk.CTkFrame):
    """Page for managing voice command → action mappings."""

    def __init__(self, parent, app_state, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._app = app_state
        self._command_rows = []
        self._build()

    def _build(self):
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_LG, Sizes.PAD_SM))

        title = ctk.CTkLabel(header, text="VOICE COMMANDS",
                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TITLE_SIZE, weight="bold"),
                              text_color=Colors.TEXT_PRIMARY)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Map voice phrases to keyboard actions",
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                 text_color=Colors.TEXT_SECONDARY)
        subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        # --- Add Command Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        btn_frame.pack(fill="x", padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_SM))

        self._add_btn = ctk.CTkButton(btn_frame, text="＋  Add Command",
                                       width=160, height=36,
                                       fg_color=Colors.ACCENT,
                                       hover_color=Colors.ACCENT_HOVER,
                                       text_color="#FFFFFF",
                                       font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                                       corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                       command=self._add_command)
        self._add_btn.pack(side="left")

        self._keybind_btn = ctk.CTkButton(btn_frame, text="+  Add Keybind",
                                           width=140, height=36,
                                           fg_color=Colors.BG_CARD,
                                           hover_color=Colors.BG_HOVER,
                                           text_color=Colors.TEXT_PRIMARY,
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                                           corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                           border_width=1,
                                           border_color=Colors.BORDER,
                                           command=self._add_keybind_command)
        self._keybind_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        self._app_btn = ctk.CTkButton(btn_frame, text="+  Add App",
                                      width=120, height=36,
                                      fg_color=Colors.BG_CARD,
                                      hover_color=Colors.BG_HOVER,
                                      text_color=Colors.TEXT_PRIMARY,
                                      font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                                      corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                      border_width=1,
                                      border_color=Colors.BORDER,
                                      command=self._add_app_command)
        self._app_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        self._save_btn = ctk.CTkButton(btn_frame, text="💾  Save Changes",
                                        width=140, height=36,
                                        fg_color=Colors.BG_CARD,
                                        hover_color=Colors.BG_HOVER,
                                        text_color=Colors.ACCENT,
                                        font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                                        corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                        border_width=1,
                                        border_color=Colors.BORDER,
                                        command=self._save_changes)
        self._save_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        # --- Column Headers ---
        col_header = ctk.CTkFrame(self, fg_color="transparent", height=28)
        col_header.pack(fill="x", padx=Sizes.PAD_LG + 12, pady=(Sizes.PAD_SM, 4))

        headers = [("", 50), ("PHRASE", 160), ("TYPE", 120), ("ACTION", 160)]
        for text, width in headers:
            lbl = ctk.CTkLabel(col_header, text=text, width=width, anchor="w",
                                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TINY_SIZE, weight="bold"),
                                text_color=Colors.TEXT_DISABLED)
            lbl.pack(side="left", padx=4)

        # --- Scrollable Command List ---
        self._scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                      scrollbar_button_color=Colors.BORDER_SUBTLE,
                                                      scrollbar_button_hover_color=Colors.ACCENT_DIM)
        self._scroll_frame.pack(fill="both", expand=True, padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_LG))

        # --- Status bar ---
        self._status_label = ctk.CTkLabel(self, text="",
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                           text_color=Colors.ACCENT, anchor="w")
        self._status_label.pack(fill="x", padx=Sizes.PAD_LG + 4, pady=(0, Sizes.PAD_SM))

    def load_commands(self, commands):
        """Load a list of command dicts into the UI."""
        # Clear existing rows
        for row in self._command_rows:
            row.destroy()
        self._command_rows.clear()

        for i, cmd in enumerate(commands):
            self._create_row(i, cmd)

        self._status_label.configure(text=f"{len(commands)} commands loaded")

    def _create_row(self, index, cmd_data):
        """Create a CommandRow widget for a command."""
        row = CommandRow(self._scroll_frame,
                         index=index,
                         phrase=cmd_data.get('phrase', ''),
                         action_type=cmd_data.get('action_type', 'media_key'),
                         action_value=cmd_data.get('action_value', ''),
                         enabled=cmd_data.get('enabled', True),
                         on_change=self._on_row_change,
                         on_delete=self._on_row_delete)
        row.pack(fill="x", pady=3)
        self._command_rows.append(row)

    def _add_command(self):
        """Add a new media-key command row."""
        index = len(self._command_rows)
        cmd_data = {'phrase': '', 'action_type': 'media_key', 'action_value': 'media_play_pause', 'enabled': True}
        self._create_row(index, cmd_data)
        self._status_label.configure(text=f"New command added — {len(self._command_rows)} total")

    def _add_keybind_command(self):
        """Add a new key-combo command row."""
        index = len(self._command_rows)
        cmd_data = {'phrase': '', 'action_type': 'key_combo', 'action_value': 'ctrl+shift+n', 'enabled': True}
        self._create_row(index, cmd_data)
        self._status_label.configure(text="Type a phrase, then enter a key combo like ctrl+shift+n")

    def _add_app_command(self):
        """Add a new app-launch command row."""
        index = len(self._command_rows)
        cmd_data = {'phrase': '', 'action_type': 'open_app', 'action_value': 'chrome', 'enabled': True}
        self._create_row(index, cmd_data)
        self._status_label.configure(text="Type a phrase, then paste an app path or use Browse")

    def _on_row_change(self, index, data):
        """Called when a command row is edited."""
        self._status_label.configure(text="Unsaved command changes")

    def _on_row_delete(self, index):
        """Remove a command row."""
        if 0 <= index < len(self._command_rows):
            row = self._command_rows.pop(index)
            row.destroy()
            # Re-index remaining rows
            for i, r in enumerate(self._command_rows):
                r._index = i
            self._status_label.configure(text=f"Command removed — {len(self._command_rows)} total")

    def _save_changes(self):
        """Collect all command data and push to the app's command processor."""
        commands = [row.get_data() for row in self._command_rows]
        # Filter out empty phrases
        commands = [c for c in commands if c['phrase'].strip()]

        if hasattr(self._app, 'save_commands'):
            self._app.save_commands(commands)
            self._status_label.configure(text=f"✓ {len(commands)} commands saved successfully")
        else:
            self._status_label.configure(text="Save function not available")

    def get_all_commands(self):
        """Return all current command data."""
        return [row.get_data() for row in self._command_rows if row.get_data()['phrase'].strip()]
