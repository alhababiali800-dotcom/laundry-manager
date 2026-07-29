"""
Unified color palette — dark mode
"""

# Brand / navy
NAVY_DARK = "#0f2744"
NAVY_MID = "#1e3a5f"
NAVY_SLATE = "#0f172a"

# Primary action (buttons, focus, active nav) — brightened for dark bg contrast
PRIMARY = "#3b82f6"
PRIMARY_HOVER = "#60a5fa"
PRIMARY_PRESSED = "#2563eb"

# Surfaces (dark)
BG_APP = "#0b1220"
BG_CARD = "#151f30"
BG_SUBTLE = "#111a2b"

# Borders
BORDER = "#2a374d"
BORDER_INPUT = "#3d4d68"

# Text (light on dark)
TEXT_PRIMARY = "#f8fafc"
TEXT_BODY = "#e2e8f0"
TEXT_LABEL = "#cbd5e1"
TEXT_MUTED = "#94a3b8"
TEXT_PLACEHOLDER = "#64748b"
TEXT_ON_DARK = "#f8fafc"
TEXT_ON_DARK_MUTED = "#cbd5e1"

# Sidebar
SIDEBAR_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f2744, stop:1 #1e3a5f)"
)

# Semantic
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"
INFO_BG = "#1e3a5f"

# Radius
RADIUS_SM = "8px"
RADIUS_MD = "10px"
RADIUS_LG = "16px"


def page_title_style() -> str:
    return f"font-size: 20px; font-weight: bold; color: {TEXT_PRIMARY};"


def page_subtitle_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 12px;"


def field_label_style() -> str:
    return f"color: {TEXT_LABEL}; font-size: 12px; font-weight: bold;"


def muted_label_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 11px;"


def value_label_style() -> str:
    return f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 13px;"


def separator_style() -> str:
    return f"background: {BORDER}; max-height: 1px;"


def dialog_title_style() -> str:
    return f"font-size: 17px; font-weight: bold; color: {TEXT_PRIMARY};"


def accent_separator_style() -> str:
    return f"background: {PRIMARY}; max-height: 2px;"