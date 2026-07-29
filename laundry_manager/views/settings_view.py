from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QFrame, QMessageBox, QTabWidget,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from models.all_models import UserModel
from database.connection import DB_PATH
from utils.branding import BUSINESS_NAME, get_logo_path
from utils.theme import NAVY_DARK, BG_SUBTLE
from views.base_view import page_title, muted_label, value_label, h_separator
from utils.i18n import tr


class SettingsView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.lbl_title = page_title(tr("nav_settings"))
        layout.addWidget(self.lbl_title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_password_tab(), f"🔒  {tr('tab_password')}")
        self.tabs.addTab(self._build_about_tab(), f"ℹ️  {tr('tab_about')}")
        layout.addWidget(self.tabs)
        layout.addStretch()

    def _build_password_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.lbl_pw_title = page_title(tr("tab_password"))
        layout.addWidget(self.lbl_pw_title)
        layout.addWidget(h_separator())

        self.form_pw = QFormLayout()
        self.form_pw.setSpacing(14)
        self.form_pw.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_current = QLineEdit()
        self.inp_current.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_current.setMinimumHeight(38)
        self.inp_current.setMaximumWidth(340)

        self.inp_new = QLineEdit()
        self.inp_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_new.setMinimumHeight(38)
        self.inp_new.setMaximumWidth(340)

        self.inp_confirm = QLineEdit()
        self.inp_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_confirm.setMinimumHeight(38)
        self.inp_confirm.setMaximumWidth(340)

        self.form_pw.addRow(tr("current_password") + ":", self.inp_current)
        self.form_pw.addRow(tr("new_password") + ":", self.inp_new)
        self.form_pw.addRow(tr("confirm_password") + ":", self.inp_confirm)
        layout.addLayout(self.form_pw)

        self.btn_update_pw = QPushButton(tr("update_password"))
        self.btn_update_pw.setObjectName("btn_primary")
        self.btn_update_pw.setFixedWidth(180)
        self.btn_update_pw.setMinimumHeight(40)
        self.btn_update_pw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update_pw.clicked.connect(self._change_password)
        layout.addWidget(self.btn_update_pw)
        layout.addStretch()
        return widget

    def _change_password(self):
        current = self.inp_current.text()
        new_pw = self.inp_new.text()
        confirm = self.inp_confirm.text()

        if not current or not new_pw or not confirm:
            QMessageBox.warning(self, tr("error"), tr("all_fields_required"))
            return
        if new_pw != confirm:
            QMessageBox.warning(self, tr("error"), tr("passwords_mismatch"))
            return
        if len(new_pw) < 6:
            QMessageBox.warning(self, tr("error"), tr("password_too_short"))
            return

        user = UserModel.verify_password(self.user['username'], current)
        if not user:
            QMessageBox.warning(self, tr("error"), tr("current_password_incorrect"))
            return

        UserModel.change_password(self.user['id'], new_pw)
        QMessageBox.information(self, tr("success"), tr("password_updated_success"))
        self.inp_current.clear()
        self.inp_new.clear()
        self.inp_confirm.clear()

    def _build_about_tab(self):
        widget = QWidget()
        self.about_layout = QVBoxLayout(widget)
        self.about_layout.setContentsMargins(24, 24, 24, 24)
        self.about_layout.setSpacing(16)
        self.about_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        if get_logo_path():
            self.logo_lbl = QLabel()
            from PyQt6.QtGui import QPixmap
            pix = QPixmap(str(get_logo_path()))
            self.logo_lbl.setPixmap(pix.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
            self.about_layout.addWidget(self.logo_lbl)
        self.lbl_about_name = value_label(BUSINESS_NAME)
        self.lbl_about_name.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {NAVY_DARK};")
        self.about_layout.addWidget(self.lbl_about_name)

        self.lbl_version = muted_label(f"{tr('version')} 1.0.0  —  Laundry Management System")
        self.about_layout.addWidget(self.lbl_version)
        self.about_layout.addWidget(h_separator())

        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.about_layout.addWidget(self.info_container)

        self._refresh_about_info()

        self.lbl_note = QLabel(tr("software_note"))
        self.lbl_note.setObjectName("muted_text")
        self.lbl_note.setStyleSheet(
            f"color:#64748b;font-size:12px;background:{BG_SUBTLE};"
            "border-radius:10px;padding:12px 16px;border:1px solid #e2e8f0;"
        )
        self.lbl_note.setWordWrap(True)
        self.about_layout.addWidget(self.lbl_note)
        self.about_layout.addStretch()
        return widget

    def _refresh_about_info(self):
        # Clear existing info layout
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Deep clear layout if needed
                pass

        info_lines = [
            (tr("built_with"), "Python + PyQt6"),
            (tr("database"), "SQLite (no server required)"),
            (tr("db_location"), DB_PATH),
            (tr("logged_in_as"), f"{self.user.get('full_name', '')}  ({self.user.get('role', '')})"),
        ]
        for label, val in info_lines:
            row = QHBoxLayout()
            l1 = muted_label(f"{label}:")
            l1.setFixedWidth(140)
            l2 = value_label(val)
            l2.setWordWrap(True)
            row.addWidget(l1)
            row.addWidget(l2)
            row.addStretch()
            self.info_layout.addLayout(row)

    def retranslate(self):
        self.lbl_title.setText(tr("nav_settings"))
        self.tabs.setTabText(0, f"🔒  {tr('tab_password')}")
        self.tabs.setTabText(1, f"ℹ️  {tr('tab_about')}")
        self.lbl_pw_title.setText(tr("tab_password"))
        
        # Update form labels
        self.form_pw.labelForField(self.inp_current).setText(tr("current_password") + ":")
        self.form_pw.labelForField(self.inp_new).setText(tr("new_password") + ":")
        self.form_pw.labelForField(self.inp_confirm).setText(tr("confirm_password") + ":")
        
        self.btn_update_pw.setText(tr("update_password"))
        self.lbl_version.setText(f"{tr('version')} 1.0.0  —  Laundry Management System")
        self._refresh_about_info()
        self.lbl_note.setText(tr("software_note"))
        
        from utils.i18n import get_lang
        if get_lang() == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.form_pw.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.form_pw.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

    def refresh(self):
        pass
