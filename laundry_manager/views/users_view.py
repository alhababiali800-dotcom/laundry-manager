from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QFormLayout, QDialogButtonBox, QFrame, QLineEdit,
    QComboBox, QMessageBox, QTableWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt
from models.all_models import UserModel, ActivityModel
from views.base_view import DataTable, make_btn, confirm_delete, colored_item, page_title, dialog_title, h_separator
from utils.i18n import tr


class UserDialog(QDialog):
    def __init__(self, parent, user, record=None):
        super().__init__(parent)
        self.current_user = user
        self.record = record
        self.setWindowTitle(tr("edit_user") if record else tr("new_user"))
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.lbl_title = dialog_title(tr("edit_user") if self.record else tr("new_user"))
        layout.addWidget(self.lbl_title)
        layout.addWidget(h_separator())

        form = QFormLayout()
        form.setSpacing(12)
        self.inp_username = QLineEdit()
        self.inp_username.setMinimumHeight(38)
        self.inp_fullname = QLineEdit()
        self.inp_fullname.setMinimumHeight(38)
        self.inp_email = QLineEdit()
        self.inp_email.setMinimumHeight(38)
        self.inp_phone = QLineEdit()
        self.inp_phone.setMinimumHeight(38)
        self.inp_password = QLineEdit()
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setMinimumHeight(38)
        self.cmb_role = QComboBox()
        for r in ['admin', 'manager', 'staff']:
            self.cmb_role.addItem(tr(r), r)
        self.cmb_role.setMinimumHeight(38)
        self.chk_active = QCheckBox(tr("active"))
        self.chk_active.setChecked(True)

        form.addRow(tr("username") + " *", self.inp_username)
        form.addRow(tr("full_name") + " *", self.inp_fullname)
        form.addRow(tr("email"), self.inp_email)
        form.addRow(tr("phone"), self.inp_phone)
        pw_label = tr("new_password") if self.record else tr("password") + " *"
        form.addRow(pw_label, self.inp_password)
        form.addRow(tr("role"), self.cmb_role)
        form.addRow("", self.chk_active)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("btn_secondary")
        layout.addWidget(btns)

        if self.record:
            self.inp_username.setText(self.record.get('username', ''))
            self.inp_fullname.setText(self.record.get('full_name', ''))
            self.inp_email.setText(self.record.get('email', '') or '')
            self.inp_phone.setText(self.record.get('phone', '') or '')
            idx = self.cmb_role.findData(self.record.get('role', 'staff'))
            if idx >= 0:
                self.cmb_role.setCurrentIndex(idx)
            self.chk_active.setChecked(bool(self.record.get('is_active', 1)))
            self.inp_username.setEnabled(False)

    def _save(self):
        username = self.inp_username.text().strip()
        fullname = self.inp_fullname.text().strip()
        if not username or not fullname:
            QMessageBox.warning(self, tr("error"), tr("username_fullname_required"))
            return
        if not self.record and not self.inp_password.text():
            QMessageBox.warning(self, tr("error"), tr("password_required_new"))
            return

        if self.record:
            UserModel.update(self.record['id'], fullname, self.cmb_role.currentData(),
                             self.inp_email.text().strip(), self.inp_phone.text().strip(),
                             int(self.chk_active.isChecked()))
            if self.inp_password.text():
                UserModel.change_password(self.record['id'], self.inp_password.text())
            ActivityModel.log(self.current_user['id'], self.current_user['username'], 'UPDATE', 'user', self.record['id'], f"Updated {username}")
        else:
            uid = UserModel.create(username, self.inp_password.text(), fullname,
                                   self.cmb_role.currentData(),
                                   self.inp_email.text().strip(), self.inp_phone.text().strip())
            ActivityModel.log(self.current_user['id'], self.current_user['username'], 'CREATE', 'user', uid, f"Created {username}")
        self.accept()


class UsersView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("user_management"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.btn_add = make_btn(f"+ {tr('new_user')}", "btn_primary")
        self.btn_add.clicked.connect(self._add)
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        self.table = DataTable([tr("username"), tr("full_name"), tr("email"), tr("phone"), tr("role"), tr("active"), tr("actions")])
        self.table.setColumnWidth(6, 140)
        self.table.horizontalHeader().setSectionResizeMode(6, self.table.horizontalHeader().ResizeMode.Fixed)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("user_management"))
        self.btn_add.setText(f"+ {tr('new_user')}")
        self.table.setHorizontalHeaderLabels([tr("username"), tr("full_name"), tr("email"), tr("phone"), tr("role"), tr("active"), tr("actions")])
        self.refresh()

    def refresh(self):
        users = UserModel.get_all()
        self.table.setRowCount(len(users))
        for r, u in enumerate(users):
            self.table.setItem(r, 0, QTableWidgetItem(u.get('username', '')))
            self.table.setItem(r, 1, QTableWidgetItem(u.get('full_name', '')))
            self.table.setItem(r, 2, QTableWidgetItem(u.get('email', '') or '—'))
            self.table.setItem(r, 3, QTableWidgetItem(u.get('phone', '') or '—'))
            role = u.get('role', 'staff')
            self.table.setItem(r, 4, colored_item(tr(role), role))
            active_text = f"✅ {tr('yes')}" if u.get('is_active') else f"❌ {tr('no')}"
            self.table.setItem(r, 5, QTableWidgetItem(active_text))

            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)
            be = QPushButton(f"✏ {tr('edit')}")
            be.setObjectName("btn_secondary")
            be.setFixedHeight(28)
            be.setCursor(Qt.CursorShape.PointingHandCursor)
            be.clicked.connect(lambda _, row=u: self._edit(row))
            al.addWidget(be)
            # Can't delete yourself
            if u['id'] != self.user['id']:
                bd = QPushButton("🗑")
                bd.setObjectName("btn_danger")
                bd.setFixedHeight(28)
                bd.setFixedWidth(32)
                bd.setCursor(Qt.CursorShape.PointingHandCursor)
                bd.clicked.connect(lambda _, uid=u['id'], n=u['username']: self._delete(uid, n))
                al.addWidget(bd)
            self.table.setCellWidget(r, 6, actions)
            self.table.setRowHeight(r, 44)

    def _add(self):
        if UserDialog(self, self.user).exec():
            self.refresh()

    def _edit(self, record):
        if UserDialog(self, self.user, record).exec():
            self.refresh()

    def _delete(self, uid, name):
        if confirm_delete(self, f'user "{name}"'):
            UserModel.delete(uid)
            self.refresh()
