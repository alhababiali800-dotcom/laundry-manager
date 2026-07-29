from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt
from utils.i18n import lang_bus, get_lang, tr
from utils.theme import PRIMARY, BG_CARD, BORDER_INPUT, TEXT_MUTED


class LanguageToggle(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background: transparent; border: none; }")
        self._build()
        lang_bus.changed.connect(lambda _: self._sync())

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn_en = QPushButton(tr("lang_en"))
        self.btn_ar = QPushButton(tr("lang_ar"))
        for btn in (self.btn_en, self.btn_ar):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setMinimumWidth(76)
        self.btn_en.clicked.connect(lambda: lang_bus.set("en"))
        self.btn_ar.clicked.connect(lambda: lang_bus.set("ar"))
        layout.addWidget(self.btn_en)
        layout.addWidget(self.btn_ar)
        self._sync()

    def _sync(self):
        active = get_lang()
        inactive = (
            f"QPushButton {{ background: {BG_CARD}; color: {TEXT_MUTED}; "
            f"border: 1px solid {BORDER_INPUT}; padding: 6px 14px; font-size: 12px; }}"
        )
        active_style = (
            f"QPushButton {{ background: {PRIMARY}; color: #ffffff; border: 1px solid {PRIMARY}; "
            "padding: 6px 14px; font-size: 12px; font-weight: bold; }"
        )
        self.btn_en.setStyleSheet(
            (active_style if active == "en" else inactive)
            + "QPushButton { border-radius: 8px 0 0 8px; }"
        )
        self.btn_ar.setStyleSheet(
            (active_style if active == "ar" else inactive)
            + "QPushButton { border-radius: 0 8px 8px 0; border-left: none; }"
        )

    def retranslate(self):
        self.btn_en.setText(tr("lang_en"))
        self.btn_ar.setText(tr("lang_ar"))
