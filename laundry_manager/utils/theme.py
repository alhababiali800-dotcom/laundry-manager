"""Unified light color palette with high-contrast input controls."""

# Brand / navy
NAVY_DARK = "#0c1f3d"
NAVY_MID = "#17325a"
NAVY_SLATE = "#0f172a"

# Primary action (buttons, focus, active nav) — brightened for dark bg contrast
PRIMARY = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
PRIMARY_PRESSED = "#1e40af"

# Surfaces
BG_APP = "#eef2f7"
BG_CARD = "#ffffff"
BG_SUBTLE = "#f4f7fb"

# Borders
BORDER = "#d1dae6"
BORDER_INPUT = "#b0bfcf"

# Text — dark on light surfaces
TEXT_PRIMARY = "#0a0f1e"
TEXT_BODY = "#1a2740"
TEXT_LABEL = "#243347"
TEXT_MUTED = "#52657a"
TEXT_PLACEHOLDER = "#8fa3b8"
TEXT_ON_DARK = "#f0f6ff"
TEXT_ON_DARK_MUTED = "#b8cce0"

# Sidebar
SIDEBAR_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0c1f3d, stop:0.6 #17325a, stop:1 #1e4070)"
)

# Semantic
SUCCESS = "#15803d"
WARNING = "#b45309"
DANGER = "#c81e1e"
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
