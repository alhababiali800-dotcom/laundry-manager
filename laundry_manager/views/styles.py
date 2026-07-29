"""Global Qt stylesheet — improved contrast and colour palette."""
from utils.theme import (
    NAVY_DARK, NAVY_MID, PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED,
    BG_APP, BG_CARD, BG_SUBTLE, BORDER, BORDER_INPUT,
    TEXT_PRIMARY, TEXT_BODY, TEXT_LABEL, TEXT_MUTED, TEXT_PLACEHOLDER,
    TEXT_ON_DARK, TEXT_ON_DARK_MUTED, SIDEBAR_GRADIENT,
    SUCCESS, WARNING, DANGER, INFO_BG,
)

APP_STYLE = f"""
* {{
    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
    font-size: 13px;
}}

QWidget {{
    color: {TEXT_BODY};
}}

QMainWindow, QWidget#central {{
    background: {BG_APP};
}}

QLabel {{
    color: {TEXT_BODY};
}}

/* ═══ SIDEBAR ═══ */
QWidget#sidebar {{
    background: {SIDEBAR_GRADIENT};
    min-width: 260px;
    max-width: 260px;
}}

QWidget#sidebar QLabel#logo_title {{
    color: {TEXT_ON_DARK};
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}

QWidget#sidebar QLabel#logo_sub {{
    color: {TEXT_ON_DARK_MUTED};
    font-size: 11px;
}}

QFrame#sidebar_sep {{
    background: rgba(255, 255, 255, 0.15);
    max-height: 1px;
    border: none;
}}

QWidget#sidebar QLabel#nav_section {{
    color: #7fa8cc;
    font-size: 10px;
    font-weight: bold;
    padding: 8px 20px 4px 20px;
    letter-spacing: 1.5px;
}}

QWidget#sidebar QPushButton#nav_btn {{
    background: transparent;
    color: {TEXT_ON_DARK_MUTED};
    border: none;
    padding: 10px 14px 10px 18px;
    text-align: left;
    font-size: 13px;
    border-radius: 10px;
    margin: 2px 10px;
}}

QWidget#sidebar QPushButton#nav_btn:hover {{
    background: rgba(255, 255, 255, 0.10);
    color: {TEXT_ON_DARK};
}}

QWidget#sidebar QPushButton#nav_btn[active=true] {{
    background: {PRIMARY};
    color: #ffffff;
    font-weight: bold;
}}

QPushButton#btn_logout_icon {{
    background: rgba(255, 255, 255, 0.08);
    color: {TEXT_ON_DARK_MUTED};
    border: none;
    border-radius: 8px;
    font-size: 16px;
}}

QPushButton#btn_logout_icon:hover {{
    background: rgba(220, 38, 38, 0.40);
    color: #fca5a5;
}}

/* ═══ CONTENT ═══ */
QWidget#content_area {{
    background: {BG_APP};
}}

QFrame#content_card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
}}

QStackedWidget#page_stack {{
    background: transparent;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

/* ═══ PAGE TYPOGRAPHY ═══ */
QLabel#page_heading {{
    font-size: 26px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QLabel#page_subheading {{
    font-size: 14px;
    color: {TEXT_MUTED};
}}

QLabel#section_title {{
    font-size: 20px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QLabel#section_sub {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

QLabel#field_label {{
    color: {TEXT_LABEL};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#muted_text {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

QLabel#value_text {{
    font-weight: bold;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QFrame#separator {{
    background: {BORDER};
    max-height: 1px;
    border: none;
}}

QFrame#separator_accent {{
    background: {PRIMARY};
    max-height: 2px;
    border: none;
}}

/* ═══ TABLE ═══ */
QTableWidget {{
    background: {BG_CARD};
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: #dbeafe;
    selection-color: {TEXT_PRIMARY};
    outline: none;
    color: {TEXT_BODY};
    alternate-background-color: {BG_SUBTLE};
}}

QTableWidget::item {{
    padding: 10px 14px;
    color: {TEXT_BODY};
    border-bottom: 1px solid {BG_APP};
}}

QTableWidget::item:selected {{
    background: #dbeafe;
    color: {TEXT_PRIMARY};
}}

QTableWidget::item:hover {{
    background: #eff6ff;
    color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background: #0c1f3d;
    color: #e8f0fb;
    font-size: 11px;
    font-weight: bold;
    padding: 11px 14px;
    border: none;
    border-right: 1px solid rgba(255,255,255,0.08);
    letter-spacing: 0.3px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 8px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 8px;
    border-right: none;
}}

/* ═══ BUTTONS ═══ */
QPushButton#btn_primary {{
    background: {PRIMARY};
    color: #ffffff;
    border: none;
    padding: 9px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: bold;
    min-width: 90px;
}}
QPushButton#btn_primary:hover   {{ background: {PRIMARY_HOVER}; }}
QPushButton#btn_primary:pressed {{ background: {PRIMARY_PRESSED}; }}
QPushButton#btn_primary:disabled {{
    background: #93c5fd;
    color: #f0f6ff;
}}

QPushButton#btn_secondary {{
    background: {BG_CARD};
    color: {TEXT_BODY};
    border: 1.5px solid {BORDER_INPUT};
    padding: 9px 20px;
    border-radius: 10px;
    font-size: 13px;
    min-width: 90px;
}}
QPushButton#btn_secondary:hover {{
    background: #eff6ff;
    border-color: {PRIMARY};
    color: {PRIMARY};
}}

QPushButton#btn_danger {{
    background: {DANGER};
    color: #ffffff;
    border: none;
    padding: 9px 20px;
    border-radius: 10px;
    font-size: 13px;
}}
QPushButton#btn_danger:hover {{ background: #991b1b; }}

QPushButton#btn_success {{
    background: {SUCCESS};
    color: #ffffff;
    border: none;
    padding: 9px 20px;
    border-radius: 10px;
    font-size: 13px;
}}
QPushButton#btn_success:hover {{ background: #166534; }}

QPushButton#btn_warning {{
    background: {WARNING};
    color: #ffffff;
    border: none;
    padding: 9px 20px;
    border-radius: 10px;
    font-size: 13px;
}}
QPushButton#btn_warning:hover {{ background: #92400e; }}

/* ═══ FORMS ═══ */
QLineEdit, QTextEdit, QDateEdit, QDateTimeEdit, QTimeEdit,
QSpinBox, QDoubleSpinBox {{
    border: 1.5px solid {BORDER_INPUT};
    border-radius: 10px;
    padding: 8px 12px;
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    selection-background-color: {PRIMARY};
    selection-color: #ffffff;
}}

QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QDateTimeEdit:focus,
QTimeEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {PRIMARY};
    background: #fafcff;
}}

QLineEdit::placeholder {{
    color: {TEXT_PLACEHOLDER};
}}

QComboBox {{
    border: 1.5px solid {BORDER_INPUT};
    border-radius: 10px;
    padding: 8px 32px 8px 12px;
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    min-height: 20px;
}}

QComboBox:focus {{
    border-color: {PRIMARY};
}}

QComboBox:disabled {{
    background: {BG_APP};
    color: {TEXT_MUTED};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1.5px solid {BORDER_INPUT};
    selection-background-color: #dbeafe;
    selection-color: {TEXT_PRIMARY};
    outline: none;
    padding: 4px;
    border-radius: 8px;
}}

QComboBox QAbstractItemView::item {{
    color: {TEXT_PRIMARY};
    background-color: {BG_CARD};
    padding: 8px 12px;
    min-height: 28px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: #eff6ff;
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: #dbeafe;
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {BG_APP};
    border: 1px solid {BORDER_INPUT};
    width: 18px;
    border-radius: 4px;
}}

QDateEdit::drop-down, QDateTimeEdit::drop-down {{
    background: {BG_APP};
    border: none;
    width: 24px;
}}

/* ═══ DIALOG ═══ */
QDialog {{
    background: {BG_APP};
    color: {TEXT_BODY};
}}

QDialog QWidget {{
    background: transparent;
    color: {TEXT_BODY};
}}

QDialog QFrame {{
    background: {BG_CARD};
    color: {TEXT_BODY};
}}

QDialog QLabel {{
    color: {TEXT_BODY};
    background: transparent;
}}

QDialog QLabel#dialog_title {{
    font-size: 17px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QDialog QLabel#field_label {{
    color: {TEXT_LABEL};
    background: transparent;
}}

QDialog QLabel#value_text {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}

QDialog QLabel#muted_text {{
    color: {TEXT_MUTED};
    background: transparent;
}}

QDialog QLineEdit,
QDialog QTextEdit,
QDialog QComboBox,
QDialog QDateEdit,
QDialog QDateTimeEdit,
QDialog QTimeEdit,
QDialog QSpinBox,
QDialog QDoubleSpinBox {{
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1.5px solid {BORDER_INPUT};
}}

QDialog QLineEdit:focus,
QDialog QTextEdit:focus,
QDialog QComboBox:focus,
QDialog QDateEdit:focus,
QDialog QDateTimeEdit:focus,
QDialog QTimeEdit:focus,
QDialog QSpinBox:focus,
QDialog QDoubleSpinBox:focus {{
    background: #fafcff;
    border-color: {PRIMARY};
}}

QDialog QTableWidget {{
    background: {BG_CARD};
    color: {TEXT_BODY};
    alternate-background-color: {BG_SUBTLE};
    selection-background-color: #dbeafe;
    selection-color: {TEXT_PRIMARY};
}}

QDialog QTableWidget::item {{
    background: transparent;
    color: {TEXT_BODY};
}}

QDialog QHeaderView::section {{
    background: #0c1f3d;
    color: #e8f0fb;
}}

QDialogButtonBox QPushButton {{
    min-width: 88px;
    min-height: 36px;
    border-radius: 10px;
}}

/* ═══ SEARCH ═══ */
QLineEdit#search_input {{
    border: 1.5px solid {BORDER_INPUT};
    border-radius: 20px;
    padding: 8px 16px;
    background: {BG_CARD};
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QLineEdit#search_input:focus {{
    border-color: {PRIMARY};
    background: #fafcff;
}}

/* ═══ CARDS ═══ */
QFrame#stat_card, QFrame#card {{
    background: {BG_CARD};
    border: 1.5px solid {BORDER};
    border-radius: 14px;
}}

/* ═══ CHECKBOX / TABS ═══ */
QCheckBox {{
    color: {TEXT_BODY};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid {BORDER_INPUT};
    border-radius: 4px;
    background: {BG_CARD};
}}
QCheckBox::indicator:checked {{
    background: {PRIMARY};
    border-color: {PRIMARY};
}}

QTabWidget::pane {{
    border: 1.5px solid {BORDER};
    border-radius: 10px;
    background: {BG_CARD};
}}
QTabBar::tab {{
    background: {BG_APP};
    color: {TEXT_MUTED};
    padding: 9px 22px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    background: {BG_CARD};
    color: {PRIMARY};
    border-bottom: 2px solid {PRIMARY};
    font-weight: bold;
}}
QTabBar::tab:hover {{
    background: {BG_SUBTLE};
    color: {TEXT_PRIMARY};
}}

/* ═══ SCROLLBAR ═══ */
QScrollBar:vertical {{
    background: {BG_SUBTLE};
    width: 7px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_INPUT};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QScrollBar:horizontal {{
    background: {BG_SUBTLE};
    height: 7px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_INPUT};
    border-radius: 4px;
}}

/* ═══ MESSAGE BOX ═══ */
QMessageBox {{
    background: {BG_CARD};
    color: {TEXT_BODY};
}}
QMessageBox QLabel {{
    color: {TEXT_BODY};
    font-size: 13px;
}}
QMessageBox QPushButton {{
    background: {PRIMARY};
    color: #ffffff;
    border: none;
    padding: 8px 20px;
    border-radius: 10px;
    min-width: 80px;
}}
QMessageBox QPushButton:hover {{ background: {PRIMARY_HOVER}; }}
"""


LOGIN_STYLE = f"""
    QWidget#login_root {{
        background: {BG_APP};
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    QFrame#brand_panel {{
        background: {SIDEBAR_GRADIENT};
        border-radius: 16px;
    }}
    QLabel#brand_title {{
        color: {TEXT_ON_DARK};
        font-size: 22px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}
    QLabel#brand_sub {{
        color: {TEXT_ON_DARK_MUTED};
        font-size: 13px;
    }}
    QFrame#login_card {{
        background: {BG_CARD};
        border: 1.5px solid {BORDER};
        border-radius: 16px;
    }}
    QLabel#welcome {{
        color: {TEXT_PRIMARY};
        font-size: 24px;
        font-weight: bold;
    }}
    QLabel#sub_text {{
        color: {TEXT_MUTED};
        font-size: 13px;
    }}
    QLabel#field_label {{
        color: {TEXT_LABEL};
        font-size: 12px;
        font-weight: 600;
    }}
    QLineEdit {{
        border: 1.5px solid {BORDER_INPUT};
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 14px;
        color: {TEXT_PRIMARY};
        background: {BG_CARD};
        selection-background-color: {PRIMARY};
        selection-color: #ffffff;
    }}
    QLineEdit:focus {{
        border-color: {PRIMARY};
        background: #fafcff;
    }}
    QLineEdit::placeholder {{
        color: {TEXT_PLACEHOLDER};
    }}
    QPushButton#btn_login {{
        background: {PRIMARY};
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton#btn_login:hover {{ background: {PRIMARY_HOVER}; }}
    QPushButton#btn_login:pressed {{ background: {PRIMARY_PRESSED}; }}
    QPushButton#btn_login:disabled {{
        background: #93c5fd;
        color: #f0f6ff;
    }}
    QLabel#error_msg {{
        color: #991b1b;
        font-size: 12px;
        background: #fee2e2;
        border: 1px solid #fca5a5;
        border-radius: 8px;
        padding: 10px 12px;
    }}
    QLabel#hint {{
        color: {TEXT_MUTED};
        font-size: 11px;
    }}
"""


def status_badge(status: str) -> str:
    mapping = {
        'received':   'badge_blue',   'processing': 'badge_yellow',
        'ready':      'badge_green',  'delivered':  'badge_gray',
        'cancelled':  'badge_red',    'active':     'badge_green',
        'expired':    'badge_red',    'paid':       'badge_green',
        'partial':    'badge_yellow', 'unpaid':     'badge_red',
        'pending':    'badge_yellow', 'admin':      'badge_blue',
        'manager':    'badge_yellow', 'staff':      'badge_gray',
    }
    return mapping.get(status, 'badge_gray')
