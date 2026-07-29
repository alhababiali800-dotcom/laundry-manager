"""
Unified color palette — matches the login screen design.
Use these constants in Python when inline styles are unavoidable.
"""

# Brand / navy
NAVY_DARK = "#0f2744"
NAVY_MID = "#1e3a5f"
NAVY_SLATE = "#0f172a"

# Primary action (buttons, focus, active nav)
PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
PRIMARY_PRESSED = "#1e40af"

# Surfaces
BG_APP = "#f1f5f9"
BG_CARD = "#ffffff"
BG_SUBTLE = "#f8fafc"

# Borders
BORDER = "#e2e8f0"
BORDER_INPUT = "#cbd5e1"

# Text
TEXT_PRIMARY = "#0f172a"
TEXT_BODY = "#1e293b"
TEXT_LABEL = "#334155"
TEXT_MUTED = "#64748b"
TEXT_PLACEHOLDER = "#94a3b8"
TEXT_ON_DARK = "#f8fafc"
TEXT_ON_DARK_MUTED = "#cbd5e1"

# Sidebar
SIDEBAR_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f2744, stop:1 #1e3a5f)"
)

# Semantic
SUCCESS = "#16a34a"
WARNING = "#d97706"
DANGER = "#dc2626"
INFO_BG = "#dbeafe"

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
