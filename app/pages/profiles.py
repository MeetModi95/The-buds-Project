"""
SONIC VOICE STUDIO — Profiles Page
Profile management — create, switch, rename, delete, duplicate, import/export.
"""

import customtkinter as ctk
import json
import os
from app.theme import Colors, Fonts, Sizes


class ProfileCard(ctk.CTkFrame):
    """A visual card representing a single profile."""

    def __init__(self, parent, profile_name, is_active=False,
                 on_select=None, on_delete=None, on_duplicate=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                         border_width=2 if is_active else 1,
                         border_color=Colors.ACCENT if is_active else Colors.BORDER,
                         height=100, cursor="hand2", **kwargs)
        self.pack_propagate(False)
        self._name = profile_name
        self._is_active = is_active
        self._on_select = on_select
        self._on_delete = on_delete
        self._on_duplicate = on_duplicate

        # Profile icon/initial
        initial = profile_name[0].upper() if profile_name else "?"
        icon_lbl = ctk.CTkLabel(self, text=initial, width=40, height=40,
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=18, weight="bold"),
                                 text_color="#FFFFFF" if is_active else Colors.TEXT_SECONDARY,
                                 fg_color=Colors.ACCENT if is_active else Colors.BG_INPUT,
                                 corner_radius=20)
        icon_lbl.pack(side="left", padx=(16, 12), pady=16)

        # Info section
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=16)

        name_lbl = ctk.CTkLabel(info_frame, text=profile_name,
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.SUBHEADING_SIZE, weight="bold"),
                                 text_color=Colors.TEXT_PRIMARY if is_active else Colors.TEXT_SECONDARY,
                                 anchor="w")
        name_lbl.pack(fill="x")

        status_text = "● Active" if is_active else "○ Inactive"
        status_color = Colors.ACCENT if is_active else Colors.TEXT_DISABLED
        status_lbl = ctk.CTkLabel(info_frame, text=status_text,
                                   font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                   text_color=status_color, anchor="w")
        status_lbl.pack(fill="x")

        # Action buttons
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(side="right", padx=(0, 12), pady=16)

        if not is_active:
            select_btn = ctk.CTkButton(actions_frame, text="Activate", width=72, height=30,
                                        fg_color=Colors.ACCENT, hover_color=Colors.ACCENT_HOVER,
                                        text_color="#FFFFFF",
                                        font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                        corner_radius=Sizes.BUTTON_CORNER_RADIUS - 4,
                                        command=lambda: self._on_select(self._name) if self._on_select else None)
            select_btn.pack(side="left", padx=3)

        dup_btn = ctk.CTkButton(actions_frame, text="⧉", width=30, height=30,
                                 fg_color=Colors.BG_INPUT, hover_color=Colors.BG_HOVER,
                                 text_color=Colors.TEXT_SECONDARY,
                                 border_width=1, border_color=Colors.BORDER,
                                 font=ctk.CTkFont(size=14),
                                 corner_radius=Sizes.BUTTON_CORNER_RADIUS - 4,
                                 command=lambda: self._on_duplicate(self._name) if self._on_duplicate else None)
        dup_btn.pack(side="left", padx=3)

        if not is_active:
            del_btn = ctk.CTkButton(actions_frame, text="✕", width=30, height=30,
                                     fg_color=Colors.BG_INPUT, hover_color=Colors.DANGER,
                                     text_color=Colors.TEXT_SECONDARY,
                                     border_width=1, border_color=Colors.BORDER,
                                     font=ctk.CTkFont(size=14),
                                     corner_radius=Sizes.BUTTON_CORNER_RADIUS - 4,
                                     command=lambda: self._on_delete(self._name) if self._on_delete else None)
            del_btn.pack(side="left", padx=3)

        # Click-to-select on the whole card
        for widget in [self, icon_lbl, info_frame, name_lbl, status_lbl]:
            widget.bind("<Button-1>", lambda e: self._on_select(self._name) if self._on_select and not self._is_active else None)


class ProfilesPage(ctk.CTkFrame):
    """Profile management page."""

    def __init__(self, parent, app_state, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._app = app_state
        self._profile_cards = []
        self._build()

    def _build(self):
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_LG, Sizes.PAD_SM))

        title = ctk.CTkLabel(header, text="PROFILES",
                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TITLE_SIZE, weight="bold"),
                              text_color=Colors.TEXT_PRIMARY)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Manage command profiles",
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                 text_color=Colors.TEXT_SECONDARY)
        subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        # --- Action Buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        btn_frame.pack(fill="x", padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_MD))

        self._new_btn = ctk.CTkButton(btn_frame, text="＋  New Profile",
                                       width=140, height=36,
                                       fg_color=Colors.ACCENT,
                                       hover_color=Colors.ACCENT_HOVER,
                                       text_color="#FFFFFF",
                                       font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"),
                                       corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                       command=self._create_profile)
        self._new_btn.pack(side="left")

        self._import_btn = ctk.CTkButton(btn_frame, text="📥  Import",
                                          width=100, height=36,
                                          fg_color=Colors.BG_CARD,
                                          hover_color=Colors.BG_HOVER,
                                          text_color=Colors.TEXT_SECONDARY,
                                          border_width=1, border_color=Colors.BORDER,
                                          font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                          corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                          command=self._import_profile)
        self._import_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        self._export_btn = ctk.CTkButton(btn_frame, text="📤  Export",
                                          width=100, height=36,
                                          fg_color=Colors.BG_CARD,
                                          hover_color=Colors.BG_HOVER,
                                          text_color=Colors.TEXT_SECONDARY,
                                          border_width=1, border_color=Colors.BORDER,
                                          font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                          corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                          command=self._export_profile)
        self._export_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        # --- Profile List ---
        self._scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                      scrollbar_button_color=Colors.BORDER_SUBTLE,
                                                      scrollbar_button_hover_color=Colors.ACCENT_DIM)
        self._scroll_frame.pack(fill="both", expand=True, padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_LG))

        # --- Status ---
        self._status_label = ctk.CTkLabel(self, text="",
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE),
                                           text_color=Colors.ACCENT, anchor="w")
        self._status_label.pack(fill="x", padx=Sizes.PAD_LG + 4, pady=(0, Sizes.PAD_SM))

    def refresh_profiles(self, profile_list, active_profile_name):
        """Rebuild the profile cards from a list of profile names."""
        for card in self._profile_cards:
            card.destroy()
        self._profile_cards.clear()

        for name in profile_list:
            is_active = (name == active_profile_name)
            card = ProfileCard(self._scroll_frame, profile_name=name,
                               is_active=is_active,
                               on_select=self._select_profile,
                               on_delete=self._delete_profile,
                               on_duplicate=self._duplicate_profile)
            card.pack(fill="x", pady=4)
            self._profile_cards.append(card)

        self._status_label.configure(text=f"{len(profile_list)} profiles loaded")

    def _select_profile(self, name):
        if hasattr(self._app, 'switch_profile'):
            self._app.switch_profile(name)

    def _delete_profile(self, name):
        if hasattr(self._app, 'delete_profile'):
            self._app.delete_profile(name)

    def _duplicate_profile(self, name):
        if hasattr(self._app, 'duplicate_profile'):
            self._app.duplicate_profile(name)

    def _create_profile(self):
        """Open a dialog to create a new profile."""
        dialog = ctk.CTkInputDialog(text="Enter profile name:", title="New Profile")
        name = dialog.get_input()
        if name and name.strip():
            if hasattr(self._app, 'create_profile'):
                self._app.create_profile(name.strip())

    def _import_profile(self):
        """Import a profile from a JSON file."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            if hasattr(self._app, 'import_profile'):
                self._app.import_profile(filepath)

    def _export_profile(self):
        """Export the active profile to a JSON file."""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Export Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            if hasattr(self._app, 'export_profile'):
                self._app.export_profile(filepath)
