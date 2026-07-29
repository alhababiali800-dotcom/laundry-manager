from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from models.all_models import UserModel, ActivityModel
from utils.branding import get_logo_path
from utils.i18n import tr, lang_bus, register_listener, unregister_listener
from views.widgets.lang_toggle import LanguageToggle
from views.styles import LOGIN_STYLE


class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{tr('app_title')} — {tr('login_title')}")
        self.setFixedSize(920, 560)
        self._drag_pos = None
        self._labels = {}
        self._build_ui()
        register_listener(self._on_language_changed)

    def closeEvent(self, event):
        unregister_listener(self._on_language_changed)
        super().closeEvent(event)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def _build_ui(self):
        self.setObjectName("login_root")
        self.setStyleSheet(LOGIN_STYLE)

        root = QHBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Left branding panel ─────────────────────────────
        brand = QFrame()
        brand.setObjectName("brand_panel")
        brand.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(36, 40, 36, 40)
        bl.setSpacing(16)

        logo_row = QHBoxLayout()
        self._logo_lbl = QLabel()
        logo_path = get_logo_path()
        if logo_path:
            pix = QPixmap(str(logo_path))
            self._logo_lbl.setPixmap(
                pix.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._logo_lbl.setText("🧺")
            self._logo_lbl.setStyleSheet("font-size: 48px;")
        logo_row.addWidget(self._logo_lbl)
        logo_row.addStretch()
        bl.addLayout(logo_row)

        self._labels["brand_title"] = QLabel(tr("app_title"))
        self._labels["brand_title"].setObjectName("brand_title")
        self._labels["brand_title"].setWordWrap(True)
        bl.addWidget(self._labels["brand_title"])

        self._labels["brand_sub"] = QLabel(tr("app_tagline"))
        self._labels["brand_sub"].setObjectName("brand_sub")
        self._labels["brand_sub"].setWordWrap(True)
        bl.addWidget(self._labels["brand_sub"])
        bl.addStretch()

        # ── Right login card ────────────────────────────────
        card_wrap = QVBoxLayout()
        card_wrap.setSpacing(12)

        top_row = QHBoxLayout()
        top_row.addStretch()
        self.lang_toggle = LanguageToggle()
        top_row.addWidget(self.lang_toggle)
        card_wrap.addLayout(top_row)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(400)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 36, 36, 36)
        cl.setSpacing(0)

        self._labels["welcome"] = QLabel(tr("login_title"))
        self._labels["welcome"].setObjectName("welcome")
        cl.addWidget(self._labels["welcome"])
        cl.addSpacing(6)

        self._labels["sub"] = QLabel(tr("login_sub"))
        self._labels["sub"].setObjectName("sub_text")
        self._labels["sub"].setWordWrap(True)
        cl.addWidget(self._labels["sub"])
        cl.addSpacing(28)

        self._labels["lbl_u"] = QLabel(tr("username"))
        self._labels["lbl_u"].setObjectName("field_label")
        cl.addWidget(self._labels["lbl_u"])
        cl.addSpacing(6)
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText(tr("username_ph"))
        self.input_username.setMinimumHeight(46)
        cl.addWidget(self.input_username)
        cl.addSpacing(16)

        self._labels["lbl_p"] = QLabel(tr("password"))
        self._labels["lbl_p"].setObjectName("field_label")
        cl.addWidget(self._labels["lbl_p"])
        cl.addSpacing(6)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText(tr("password_ph"))
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setMinimumHeight(46)
        self.input_password.returnPressed.connect(self._do_login)
        cl.addWidget(self.input_password)
        cl.addSpacing(12)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error_msg")
        self.lbl_error.hide()
        self.lbl_error.setWordWrap(True)
        cl.addWidget(self.lbl_error)
        cl.addSpacing(16)

        self.btn_login = QPushButton(tr("sign_in"))
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setMinimumHeight(48)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self._do_login)
        cl.addWidget(self.btn_login)
        cl.addSpacing(16)

        self._labels["hint"] = QLabel(tr("login_hint"))
        self._labels["hint"].setObjectName("hint")
        self._labels["hint"].setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._labels["hint"])

        card_wrap.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        card_wrap.addStretch()

        root.addWidget(brand, 1)
        root.addLayout(card_wrap, 1)

        self.input_username.setFocus()

    def _on_language_changed(self, lang: str):
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(f"{tr('app_title')} — {tr('login_title')}")
        self._labels["brand_title"].setText(tr("app_title"))
        self._labels["brand_sub"].setText(tr("app_tagline"))
        self._labels["welcome"].setText(tr("login_title"))
        self._labels["sub"].setText(tr("login_sub"))
        self._labels["lbl_u"].setText(tr("username"))
        self._labels["lbl_p"].setText(tr("password"))
        self.input_username.setPlaceholderText(tr("username_ph"))
        self.input_password.setPlaceholderText(tr("password_ph"))
        self._labels["hint"].setText(tr("login_hint"))
        if not self.btn_login.isEnabled() or self.btn_login.text() != tr("signing_in"):
            self.btn_login.setText(tr("sign_in"))
        self.lang_toggle.retranslate()

    def _do_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not username or not password:
            self._show_error(tr("login_error_empty"))
            return

        self.btn_login.setText(tr("signing_in"))
        self.btn_login.setEnabled(False)

        user = UserModel.verify_password(username, password)

        self.btn_login.setText(tr("sign_in"))
        self.btn_login.setEnabled(True)

        if user:
            ActivityModel.log(user['id'], user['username'], 'LOGIN', description='User logged in')
            self.login_successful.emit(user)
        else:
            self._show_error(tr("login_error_invalid"))
            self.input_password.clear()
            self.input_password.setFocus()

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self.lbl_error.show()
