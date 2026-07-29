"""Shared helpers used by all content views."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QHeaderView,
    QTableWidgetItem, QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from utils.theme import TEXT_PRIMARY, TEXT_BODY, PRIMARY, BORDER, BG_SUBTLE


STATUS_BG = {
    'received': '#dbeafe', 'processing': '#fef9c3',
    'ready': '#dcfce7', 'delivered': BG_SUBTLE,
    'cancelled': '#fee2e2', 'active': '#dcfce7',
    'expired': '#fee2e2', 'paid': '#dcfce7',
    'partial': '#fef9c3', 'unpaid': '#fee2e2',
    'pending': '#fef9c3', 'admin': '#dbeafe',
    'manager': '#fef9c3', 'staff': BG_SUBTLE,
}


def colored_item(text: str, status_key: str = '') -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setForeground(QColor(TEXT_PRIMARY))
    bg = STATUS_BG.get(status_key, '')
    if bg:
        item.setBackground(QColor(bg))
    return item


def table_item(text: str, align_center: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(QColor(TEXT_BODY))
    if align_center:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def center_item(text: str) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    item.setForeground(QColor(TEXT_BODY))
    return item


def page_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("section_title")
    return lbl


def page_heading(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("page_heading")
    return lbl


def muted_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("muted_text")
    return lbl


def field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("field_label")
    return lbl


def value_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("value_text")
    return lbl


def dialog_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("dialog_title")
    return lbl


def h_separator(accent: bool = False) -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setObjectName("separator_accent" if accent else "separator")
    return sep


def status_chip(text: str, bg_color: str) -> QLabel:
    lbl = QLabel(text.upper() if text else "")
    lbl.setStyleSheet(
        f"background:{bg_color}; color:{TEXT_PRIMARY}; border-radius:6px;"
        "padding:4px 12px; font-size:11px; font-weight:bold;"
    )
    return lbl


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = '', buttons: list = None):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.addWidget(page_title(title))
        if subtitle:
            left.addWidget(muted_label(subtitle))
        layout.addLayout(left)
        layout.addStretch()
        if buttons:
            for btn in buttons:
                layout.addWidget(btn)


class SearchBar(QLineEdit):
    def __init__(self, placeholder=None):
        super().__init__()
        from utils.i18n import tr
        ph = placeholder if placeholder else tr("search_ph")
        self.setPlaceholderText(f"🔍  {ph}")
        self.setObjectName("search_input")
        self.setMinimumWidth(260)
        self.setMinimumHeight(38)


class DataTable(QTableWidget):
    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSortingEnabled(False)

    def set_row_height(self, h=42):
        for r in range(self.rowCount()):
            self.setRowHeight(r, h)


def confirm_delete(parent, name='this record') -> bool:
    from utils.i18n import tr
    reply = QMessageBox.question(
        parent, tr("confirm_delete_title"),
        tr("confirm_delete_msg", name=name),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes


def make_btn(label: str, obj_name: str, min_width=80) -> QPushButton:
    btn = QPushButton(label)
    btn.setObjectName(obj_name)
    btn.setMinimumWidth(min_width)
    btn.setMinimumHeight(38)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn
