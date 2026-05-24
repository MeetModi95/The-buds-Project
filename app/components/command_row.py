"""
SONIC VOICE STUDIO — Command Row Component
An editable row displaying a voice command mapping with controls.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Sizes


class CommandRow(ctk.CTkFrame):
    """
    A single row in the command mapping table.
    Shows: [Enable Toggle] | Phrase | Action Type | Action Value | [Delete]
    """

    ACTION_TYPES = ["media_key", "key_combo", "key_tap", "open_app", "open_url"]
    MEDIA_KEYS = [
        "media_play_pause", "media_next", "media_previous",
        "media_volume_up", "media_volume_down", "media_volume_mute"
    ]

    def __init__(self, parent, index, phrase="", action_type="media_key",
                 action_value="", enabled=True,
                 on_change=None, on_delete=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                         border_width=1, border_color=Colors.BORDER,
                         height=52, **kwargs)
        self.pack_propagate(False)
        self._index = index
        self._on_change = on_change
        self._on_delete = on_delete

        # --- Enable toggle ---
        self._enabled_var = ctk.StringVar(value="on" if enabled else "off")
        self._toggle = ctk.CTkSwitch(self, text="", width=36,
                                      variable=self._enabled_var,
                                      onvalue="on", offvalue="off",
                                      command=self._emit_change,
                                      progress_color=Colors.ACCENT,
                                      button_color=Colors.ACCENT_HOVER,
                                      fg_color=Colors.BORDER_SUBTLE)
        self._toggle.pack(side="left", padx=(12, 8), pady=10)

        # --- Phrase entry ---
        self._phrase_entry = ctk.CTkEntry(self, width=160, height=32,
                                           fg_color=Colors.BG_INPUT,
                                           text_color=Colors.TEXT_PRIMARY,
                                           border_color=Colors.BORDER,
                                           border_width=1,
                                           corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                           placeholder_text="voice phrase...")
        self._phrase_entry.insert(0, phrase)
        self._phrase_entry.pack(side="left", padx=4, pady=10)
        self._phrase_entry.bind("<FocusOut>", lambda e: self._emit_change())

        # --- Action type dropdown ---
        self._type_var = ctk.StringVar(value=action_type)
        self._type_menu = ctk.CTkOptionMenu(self, values=self.ACTION_TYPES,
                                             variable=self._type_var,
                                             width=120, height=32,
                                             fg_color=Colors.BG_INPUT,
                                             button_color=Colors.BORDER_SUBTLE,
                                             button_hover_color=Colors.BG_HOVER,
                                             text_color=Colors.TEXT_PRIMARY,
                                             dropdown_fg_color=Colors.BG_CARD,
                                             dropdown_hover_color=Colors.BG_HOVER,
                                             dropdown_text_color=Colors.TEXT_PRIMARY,
                                             font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                             corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                             command=self._on_type_change)
        self._type_menu.pack(side="left", padx=4, pady=10)

        # --- Action value ---
        self._media_var = ctk.StringVar(
            value=action_value if action_value in self.MEDIA_KEYS else self.MEDIA_KEYS[0]
        )
        self._value_entry = ctk.CTkEntry(self, width=160, height=32,
                                          fg_color=Colors.BG_INPUT,
                                          text_color=Colors.TEXT_PRIMARY,
                                          border_color=Colors.BORDER,
                                          border_width=1,
                                          corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                          font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                          placeholder_text="action value...")
        self._value_entry.insert(0, action_value)
        self._value_entry.bind("<FocusOut>", lambda e: self._emit_change())

        self._media_dropdown = ctk.CTkOptionMenu(self, values=self.MEDIA_KEYS,
                                                  variable=self._media_var,
                                                  width=160, height=32,
                                                  fg_color=Colors.BG_INPUT,
                                                  button_color=Colors.BORDER_SUBTLE,
                                                  button_hover_color=Colors.BG_HOVER,
                                                  text_color=Colors.TEXT_PRIMARY,
                                                  dropdown_fg_color=Colors.BG_CARD,
                                                  dropdown_hover_color=Colors.BG_HOVER,
                                                  dropdown_text_color=Colors.TEXT_PRIMARY,
                                                  font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                                  corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                                  command=lambda _value: self._emit_change())

        self._browse_btn = ctk.CTkButton(self, text="Browse", width=72, height=32,
                                          fg_color=Colors.BG_INPUT,
                                          hover_color=Colors.BG_HOVER,
                                          text_color=Colors.TEXT_SECONDARY,
                                          border_width=1,
                                          border_color=Colors.BORDER,
                                          font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                          corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                          command=self._browse_app_path)

        if action_type == "media_key":
            self._show_media_dropdown(action_value)
        else:
            self._show_value_entry()

        # --- Delete button ---
        self._delete_btn = ctk.CTkButton(self, text="✕", width=32, height=32,
                                          fg_color=Colors.BG_INPUT,
                                          hover_color=Colors.DANGER,
                                          text_color=Colors.TEXT_SECONDARY,
                                          font=ctk.CTkFont(size=14),
                                          corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                          command=self._handle_delete)
        self._delete_btn.pack(side="right", padx=(4, 12), pady=10)

    def _on_type_change(self, new_type):
        if new_type == "media_key":
            current_val = self._value_entry.get()
            if current_val not in self.MEDIA_KEYS:
                current_val = self.MEDIA_KEYS[0]
            self._show_media_dropdown(current_val)
            self._value_entry.delete(0, "end")
            self._value_entry.insert(0, current_val)
        else:
            self._show_value_entry()
        self._emit_change()

    def _show_media_dropdown(self, current_value):
        """Show a helper dropdown for media keys."""
        self._value_entry.pack_forget()
        self._browse_btn.pack_forget()
        if current_value in self.MEDIA_KEYS:
            self._media_var.set(current_value)
        else:
            self._media_var.set(self.MEDIA_KEYS[0])
        self._media_dropdown.pack(side="left", padx=4, pady=10, fill="x", expand=True)

    def _show_value_entry(self):
        """Show a free-form action value entry."""
        self._media_dropdown.pack_forget()
        self._browse_btn.pack_forget()
        placeholders = {
            "key_combo": "ctrl+shift+n",
            "key_tap": "enter",
            "open_app": "chrome or C:\\Path\\app.exe",
            "open_url": "https://example.com",
        }
        self._value_entry.configure(
            placeholder_text=placeholders.get(self._type_var.get(), "action value...")
        )
        self._value_entry.pack(side="left", padx=4, pady=10, fill="x", expand=True)
        if self._type_var.get() == "open_app":
            self._browse_btn.pack(side="left", padx=(4, 0), pady=10)

    def _browse_app_path(self):
        """Let the user choose an app/file path for an open_app command."""
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            title="Select app, shortcut, or file",
            filetypes=[
                ("Applications and shortcuts", "*.exe *.lnk *.bat *.cmd"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._value_entry.delete(0, "end")
            self._value_entry.insert(0, path)
            self._emit_change()

    def _handle_delete(self):
        if self._on_delete:
            self._on_delete(self._index)

    def _emit_change(self):
        if self._on_change:
            self._on_change(self._index, self.get_data())

    def get_data(self):
        action_value = self._media_var.get() if self._type_var.get() == "media_key" else self._value_entry.get().strip()
        return {
            'phrase': self._phrase_entry.get().strip().lower(),
            'action_type': self._type_var.get(),
            'action_value': action_value,
            'enabled': self._enabled_var.get() == "on"
        }
