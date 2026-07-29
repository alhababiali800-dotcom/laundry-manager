from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QDialog, QFormLayout,
    QDialogButtonBox, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from models.all_models import CustomerModel, CompanyModel, ActivityModel
from views.base_view import (
    DataTable, SearchBar, confirm_delete, make_btn, colored_item, center_item,
    page_title, muted_label, dialog_title, h_separator,
)


from utils.i18n import tr

class CustomerDialog(QDialog):
    def __init__(self, parent, user, record=None):
        super().__init__(parent)
        self.user = user
        self.record = record
        self.setWindowTitle(tr("edit_customer") if record else tr("new_customer"))
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.lbl_title = dialog_title(tr("edit_customer") if self.record else tr("new_customer"))
        layout.addWidget(self.lbl_title)
        layout.addWidget(h_separator())

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText(tr("name"))
        self.inp_name.setMinimumHeight(38)
        form.addRow(tr("name") + " *", self.inp_name)

        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("+60 ...")
        self.inp_phone.setMinimumHeight(38)
        form.addRow(tr("phone"), self.inp_phone)

        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("email@example.com")
        self.inp_email.setMinimumHeight(38)
        form.addRow(tr("email"), self.inp_email)

        self.inp_address = QLineEdit()
        self.inp_address.setPlaceholderText(tr("address"))
        self.inp_address.setMinimumHeight(38)
        form.addRow(tr("address"), self.inp_address)

        self.cmb_type = QComboBox()
        self.cmb_type.addItem(tr("individual"), "individual")
        self.cmb_type.addItem(tr("company"), "company")
        self.cmb_type.setMinimumHeight(38)
        form.addRow(tr("type"), self.cmb_type)

        self.cmb_company = QComboBox()
        self.cmb_company.addItem(f"— {tr('none')} —", None)
        for c in CompanyModel.get_all():
            self.cmb_company.addItem(c['name'], c['id'])
        self.cmb_company.setMinimumHeight(38)
        form.addRow(tr("company"), self.cmb_company)

        self.inp_notes = QTextEdit()
        self.inp_notes.setPlaceholderText(tr("notes_ph"))
        self.inp_notes.setMaximumHeight(80)
        form.addRow(tr("notes"), self.inp_notes)

        layout.addLayout(form)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("btn_secondary")
        btns.button(QDialogButtonBox.StandardButton.Save).setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btns)

        if self.record:
            self.inp_name.setText(self.record.get('name', ''))
            self.inp_phone.setText(self.record.get('phone', ''))
            self.inp_email.setText(self.record.get('email', ''))
            self.inp_address.setText(self.record.get('address', ''))
            idx = self.cmb_type.findText(self.record.get('customer_type', 'individual'))
            if idx >= 0: self.cmb_type.setCurrentIndex(idx)
            if self.record.get('company_id'):
                for i in range(self.cmb_company.count()):
                    if self.cmb_company.itemData(i) == self.record['company_id']:
                        self.cmb_company.setCurrentIndex(i)
                        break
            self.inp_notes.setPlainText(self.record.get('notes', '') or '')

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("error") if "error" in tr("error") else "Error", tr("customer_name_required"))
            return
        data = {
            'name': name,
            'phone': self.inp_phone.text().strip(),
            'email': self.inp_email.text().strip(),
            'address': self.inp_address.text().strip(),
            'customer_type': self.cmb_type.currentData(),
            'company_id': self.cmb_company.currentData(),
            'notes': self.inp_notes.toPlainText().strip(),
        }
        if self.record:
            CustomerModel.update(self.record['id'], **data)
            ActivityModel.log(self.user['id'], self.user['username'],
                              'UPDATE', 'customer', self.record['id'], f"Updated {name}")
        else:
            cid = CustomerModel.create(**data)
            ActivityModel.log(self.user['id'], self.user['username'],
                              'CREATE', 'customer', cid, f"Created {name}")
        self.accept()


class CustomersView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header row
        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_customers"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.search = SearchBar(tr("search_customers_ph"))
        self.search.textChanged.connect(self._filter)
        h.addWidget(self.search)
        self.btn_add = make_btn(f"+ {tr('new_customer')}", "btn_primary")
        self.btn_add.clicked.connect(self._add)
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        # Count label
        self.lbl_count = muted_label("")
        layout.addWidget(self.lbl_count)

        # Table
        self.table = DataTable([tr("name"), tr("phone"), tr("email"), tr("type"), tr("company"), tr("actions")])
        self.table.horizontalHeader().setSectionResizeMode(5, self.table.horizontalHeader().ResizeMode.Fixed)
        self.table.setColumnWidth(5, 140)
        self.table.doubleClicked.connect(self._edit_selected)
        layout.addWidget(self.table)

        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_customers"))
        self.search.setPlaceholderText(f"🔍  {tr('search_customers_ph')}")
        self.btn_add.setText(f"+ {tr('new_customer')}")
        self.table.setHorizontalHeaderLabels([tr("name"), tr("phone"), tr("email"), tr("type"), tr("company"), tr("actions")])
        self.refresh()

    def refresh(self):
        self._load(CustomerModel.get_all())

    def _filter(self, q):
        if q.strip():
            self._load(CustomerModel.search(q))
        else:
            self.refresh()

    def _load(self, customers):
        self.table.setRowCount(len(customers))
        self.lbl_count.setText(tr("count_customers", count=len(customers)))
        for r, c in enumerate(customers):
            self.table.setItem(r, 0, self._item(c['name']))
            self.table.setItem(r, 1, self._item(c.get('phone', '') or '—'))
            self.table.setItem(r, 2, self._item(c.get('email', '') or '—'))
            ctype = c.get('customer_type','individual')
            self.table.setItem(r, 3, colored_item(tr(ctype), ctype))
            self.table.setItem(r, 4, self._item(c.get('company_name', '') or '—'))
            # Actions
            actions = QWidget()
            row_layout = QHBoxLayout(actions)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(4)
            btn_e = QPushButton(f"✏ {tr('edit')}")
            btn_e.setObjectName("btn_secondary")
            btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_e.setFixedHeight(28)
            btn_e.clicked.connect(lambda _, row=c: self._edit(row))
            btn_d = QPushButton("🗑")
            btn_d.setObjectName("btn_danger")
            btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_d.setFixedHeight(28)
            btn_d.setFixedWidth(32)
            btn_d.clicked.connect(lambda _, cid=c['id'], n=c['name']: self._delete(cid, n))
            row_layout.addWidget(btn_e)
            row_layout.addWidget(btn_d)
            self.table.setCellWidget(r, 5, actions)
            self.table.setRowHeight(r, 44)

    def _item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))

    def _add(self):
        dlg = CustomerDialog(self, self.user)
        if dlg.exec():
            self.refresh()

    def _edit(self, record):
        dlg = CustomerDialog(self, self.user, record)
        if dlg.exec():
            self.refresh()

    def _edit_selected(self):
        row = self.table.currentRow()
        if row < 0: return
        name = self.table.item(row, 0).text()
        customers = CustomerModel.get_all()
        for c in customers:
            if c['name'] == name:
                self._edit(c)
                return

    def _delete(self, cid, name):
        if confirm_delete(self, f'"{name}"'):
            CustomerModel.delete(cid)
            ActivityModel.log(self.user['id'], self.user['username'],
                              'DELETE', 'customer', cid, f"Deleted {name}")
            self.refresh()
