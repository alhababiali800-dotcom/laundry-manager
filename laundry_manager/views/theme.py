"""
Unified color palette — improved contrast and visual hierarchy.
"""

# Brand / navy (deeper, richer blues)
NAVY_DARK  = "#0c1f3d"   # was #0f2744 — slightly deeper for sidebar top
NAVY_MID   = "#17325a"   # was #1e3a5f
NAVY_SLATE = "#0f172a"

# Primary action (buttons, focus, active nav) — kept recognisable blue
PRIMARY         = "#2563eb"
PRIMARY_HOVER   = "#1d4ed8"
PRIMARY_PRESSED = "#1e40af"

# Surfaces — slightly warmer whites for less clinical feel
BG_APP    = "#eef2f7"   # was #f1f5f9 — slightly more blue-grey
BG_CARD   = "#ffffff"
BG_SUBTLE = "#f4f7fb"   # was #f8fafc

# Borders — a touch stronger so cards read clearly
BORDER       = "#d1dae6"  # was #e2e8f0
BORDER_INPUT = "#b0bfcf"  # was #cbd5e1

# Text — improved contrast (WCAG AA compliant on white + card)
TEXT_PRIMARY     = "#0a0f1e"   # was #0f172a — nearly black, max contrast
TEXT_BODY        = "#1a2740"   # was #1e293b — dark navy-grey
TEXT_LABEL       = "#243347"   # was #334155 — labels slightly darker
TEXT_MUTED       = "#52657a"   # was #64748b — still readable muted
TEXT_PLACEHOLDER = "#8fa3b8"   # was #94a3b8
TEXT_ON_DARK     = "#f0f6ff"   # was #f8fafc — warm white on navy
TEXT_ON_DARK_MUTED = "#b8cce0" # was #cbd5e1 — softer muted on dark

# Sidebar (richer gradient for more premium feel)
SIDEBAR_GRADIENT = (
    "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0c1f3d, stop:0.6 #17325a, stop:1 #1e4070)"
)

# Semantic colours — stronger, clearer
SUCCESS  = "#15803d"   # darker green — better contrast on white
WARNING  = "#b45309"   # darker amber
DANGER   = "#c81e1e"   # was #dc2626 — slightly deeper red
INFO_BG  = "#dbeafe"   # kept — used for selected rows

# Header row (table headers) — richer navy
HEADER_BG = "#0c1f3d"
HEADER_FG = "#e8f0fb"

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
