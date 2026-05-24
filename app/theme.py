"""
SONIC VOICE STUDIO - Design Token System
Centralized color palette, fonts, and styling constants for a premium
Apple Music–inspired purple glassmorphism interface.
"""


class Colors:
    """Application color palette (Apple Music–style purple glassmorphism)."""

    # Backgrounds — deep indigo-black foundation with purple undertones.
    BG_ROOT = "#0D0B1A"
    BG_SIDEBAR = "#1A1232"
    BG_PANEL = "#15102A"
    BG_CARD = "#241B42"
    BG_INPUT = "#1E1538"
    BG_HOVER = "#3B2D60"
    BG_SCRIM = "#0A0816"

    # Accent — vibrant purple core with fuchsia and lilac complements.
    ACCENT = "#A855F7"
    ACCENT_HOVER = "#C084FC"
    ACCENT_DIM = "#7C3AED"
    ACCENT_GLOW = "#D946EF"
    ACCENT_PINK = "#F472B6"
    ACCENT_MINT = "#34D399"
    ACCENT_GOLD = "#FBBF24"

    # Danger / destructive actions
    DANGER = "#EF4444"
    DANGER_HOVER = "#F87171"

    # Warning
    WARNING = "#F59E0B"

    # Text
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#D4C5F0"
    TEXT_DISABLED = "#8B7DAF"
    TEXT_ACCENT = ACCENT

    # Borders & dividers (purple-tinted specular edges)
    BORDER = "#6D28D9"
    BORDER_SUBTLE = "#4C1D95"
    DIVIDER = "#2E1B5E"

    # Status indicators
    STATUS_ONLINE = "#34D399"
    STATUS_OFFLINE = "#8B7DAF"
    STATUS_ERROR = "#EF4444"
    STATUS_LISTENING = "#A855F7"

    # Sidebar active styling
    SIDEBAR_ACTIVE_BG = "#3B1F6E"
    SIDEBAR_ACTIVE_BAR = ACCENT


class Fonts:
    """Font configurations. Uses Segoe UI (Windows) with fallback."""

    FAMILY = "Segoe UI"

    # Size tiers
    TITLE_SIZE = 20
    HEADING_SIZE = 15
    SUBHEADING_SIZE = 13
    BODY_SIZE = 12
    CAPTION_SIZE = 10
    TINY_SIZE = 9

    # Weights
    BOLD = "bold"
    NORMAL = "normal"


class Sizes:
    """Layout dimensions and spacing."""

    # Window
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 700
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600

    # Sidebar
    SIDEBAR_WIDTH = 220
    SIDEBAR_ICON_SIZE = 20
    SIDEBAR_ITEM_HEIGHT = 44

    # Cards & panels
    CARD_CORNER_RADIUS = 20
    PANEL_CORNER_RADIUS = 24
    BUTTON_CORNER_RADIUS = 16
    INPUT_CORNER_RADIUS = 14

    # Spacing
    PAD_XS = 4
    PAD_SM = 8
    PAD_MD = 16
    PAD_LG = 24
    PAD_XL = 32

    # Slider
    SLIDER_HEIGHT = 16
    SLIDER_WIDTH = 200


class AppConfig:
    """Application metadata."""

    APP_NAME = "SONIC VOICE STUDIO"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Sonic Labs"
    WINDOW_TITLE = "SONIC VOICE STUDIO II"
