from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QDialogButtonBox,
    QFrame, QMessageBox, QComboBox, QDoubleSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from models.all_models import CompanyModel, ContractModel, ActivityModel
from views.base_view import (
    DataTable, SearchBar, confirm_delete, make_btn, colored_item,
    page_title, muted_label, dialog_title, h_separator,
)
from utils.i18n import tr


# ═══════════════════════ COMPANY DIALOG ═══════════════════════
class CompanyDialog(QDialog):
    def __init__(self, parent, user, record=None):
        super().__init__(parent)
        self.user = user
        self.record = record
        self.setWindowTitle(tr("edit_company") if record else tr("new_company"))
        self.setMinimumWidth(460)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.lbl_title = dialog_title(tr("edit_company") if self.record else tr("new_company"))
        layout.addWidget(self.lbl_title)
        layout.addWidget(h_separator())

        form = QFormLayout()
        form.setSpacing(12)
        self.inp_name = QLineEdit()
        self.inp_name.setMinimumHeight(38)
        self.inp_contact = QLineEdit()
        self.inp_contact.setMinimumHeight(38)
        self.inp_phone = QLineEdit()
        self.inp_phone.setMinimumHeight(38)
        self.inp_email = QLineEdit()
        self.inp_email.setMinimumHeight(38)
        self.inp_address = QLineEdit()
        self.inp_address.setMinimumHeight(38)
        self.inp_notes = QTextEdit()
        self.inp_notes.setMaximumHeight(70)

        form.addRow(tr("col_company_name") + " *", self.inp_name)
        form.addRow(tr("col_contact_person"), self.inp_contact)
        form.addRow(tr("phone"), self.inp_phone)
        form.addRow(tr("email"), self.inp_email)
        form.addRow(tr("address"), self.inp_address)
        form.addRow(tr("notes"), self.inp_notes)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("btn_secondary")
        layout.addWidget(btns)

        if self.record:
            self.inp_name.setText(self.record.get('name', ''))
            self.inp_contact.setText(self.record.get('contact_person', '') or '')
            self.inp_phone.setText(self.record.get('phone', '') or '')
            self.inp_email.setText(self.record.get('email', '') or '')
            self.inp_address.setText(self.record.get('address', '') or '')
            self.inp_notes.setPlainText(self.record.get('notes', '') or '')

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("error") if "error" in tr("error") else "Error", tr("company_name_required"))
            return
        data = dict(
            name=name,
            contact_person=self.inp_contact.text().strip(),
            phone=self.inp_phone.text().strip(),
            email=self.inp_email.text().strip(),
            address=self.inp_address.text().strip(),
            notes=self.inp_notes.toPlainText().strip(),
        )
        if self.record:
            CompanyModel.update(self.record['id'], **data)
            ActivityModel.log(self.user['id'], self.user['username'], 'UPDATE', 'company', self.record['id'], f"Updated {name}")
        else:
            cid = CompanyModel.create(**data)
            ActivityModel.log(self.user['id'], self.user['username'], 'CREATE', 'company', cid, f"Created {name}")
        self.accept()


# ═══════════════════════ COMPANIES VIEW ═══════════════════════
class CompaniesView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_companies"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.search = SearchBar(tr("search_companies_ph"))
        self.search.textChanged.connect(self._filter)
        h.addWidget(self.search)
        self.btn_add = make_btn(f"+ {tr('new_company')}", "btn_primary")
        self.btn_add.clicked.connect(self._add)
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        self.lbl_count = muted_label("")
        layout.addWidget(self.lbl_count)

        self.table = DataTable([tr("col_company_name"), tr("col_contact_person"), tr("phone"), tr("email"), tr("actions")])
        self.table.setColumnWidth(4, 140)
        self.table.horizontalHeader().setSectionResizeMode(4, self.table.horizontalHeader().ResizeMode.Fixed)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_companies"))
        self.search.setPlaceholderText(f"🔍  {tr('search_companies_ph')}")
        self.btn_add.setText(f"+ {tr('new_company')}")
        self.table.setHorizontalHeaderLabels([tr("col_company_name"), tr("col_contact_person"), tr("phone"), tr("email"), tr("actions")])
        self.refresh()

    def refresh(self):
        self._load(CompanyModel.get_all())

    def _filter(self, q):
        self._load(CompanyModel.search(q) if q.strip() else CompanyModel.get_all())

    def _load(self, companies):
        from PyQt6.QtWidgets import QTableWidgetItem
        self.table.setRowCount(len(companies))
        self.lbl_count.setText(tr("count_companies", count=len(companies)))
        for r, c in enumerate(companies):
            for col, key in enumerate(['name', 'contact_person', 'phone', 'email']):
                self.table.setItem(r, col, QTableWidgetItem(c.get(key, '') or '—'))
            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)
            be = QPushButton(f"✏ {tr('edit')}")
            be.setObjectName("btn_secondary")
            be.setFixedHeight(28)
            be.setCursor(Qt.CursorShape.PointingHandCursor)
            be.clicked.connect(lambda _, row=c: self._edit(row))
            bd = QPushButton("🗑")
            bd.setObjectName("btn_danger")
            bd.setFixedHeight(28)
            bd.setFixedWidth(32)
            bd.setCursor(Qt.CursorShape.PointingHandCursor)
            bd.clicked.connect(lambda _, cid=c['id'], n=c['name']: self._delete(cid, n))
            al.addWidget(be)
            al.addWidget(bd)
            self.table.setCellWidget(r, 4, actions)
            self.table.setRowHeight(r, 44)

    def _add(self):
        if CompanyDialog(self, self.user).exec():
            self.refresh()

    def _edit(self, record):
        if CompanyDialog(self, self.user, record).exec():
            self.refresh()

    def _delete(self, cid, name):
        if confirm_delete(self, f'"{name}"'):
            CompanyModel.delete(cid)
            ActivityModel.log(self.user['id'], self.user['username'], 'DELETE', 'company', cid, f"Deleted {name}")
            self.refresh()


# ═══════════════════════ CONTRACT DIALOG ═══════════════════════
class ContractDialog(QDialog):
    def __init__(self, parent, user, record=None):
        super().__init__(parent)
        self.user = user
        self.record = record
        self.setWindowTitle(tr("edit_contract") if record else tr("new_contract"))
        self.setMinimumWidth(500)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.lbl_title = dialog_title(tr("edit_contract") if self.record else tr("new_contract"))
        layout.addWidget(self.lbl_title)
        layout.addWidget(h_separator())

        form = QFormLayout()
        form.setSpacing(12)
        self.inp_title = QLineEdit()
        self.inp_title.setMinimumHeight(38)
        self.cmb_company = QComboBox()
        self.cmb_company.setMinimumHeight(38)
        for c in CompanyModel.get_all():
            self.cmb_company.addItem(c['name'], c['id'])
        self.date_start = QDateEdit(QDate.currentDate())
        self.date_start.setCalendarPopup(True)
        self.date_start.setMinimumHeight(38)
        self.date_end = QDateEdit(QDate.currentDate().addYears(1))
        self.date_end.setCalendarPopup(True)
        self.date_end.setMinimumHeight(38)
        self.inp_discount = QDoubleSpinBox()
        self.inp_discount.setRange(0, 100)
        self.inp_discount.setSuffix('%')
        self.inp_discount.setMinimumHeight(38)
        self.inp_limit = QDoubleSpinBox()
        self.inp_limit.setRange(0, 999999)
        self.inp_limit.setPrefix('RM ')
        self.inp_limit.setMinimumHeight(38)
        self.cmb_payment = QComboBox()
        self.cmb_payment.setMinimumHeight(38)
        for p in ['monthly', 'weekly', 'per_order']:
            self.cmb_payment.addItem(tr(p), p)
        self.cmb_status = QComboBox()
        self.cmb_status.setMinimumHeight(38)
        for s in ['active', 'expired', 'cancelled']:
            self.cmb_status.addItem(tr(s) if f"status_{s}" not in tr(f"status_{s}") else tr(f"status_{s}"), s)
        self.inp_notes = QTextEdit()
        self.inp_notes.setMaximumHeight(60)

        form.addRow(tr("col_title") + " *", self.inp_title)
        form.addRow(tr("company") + " *", self.cmb_company)
        form.addRow(tr("start_date"), self.date_start)
        form.addRow(tr("end_date"), self.date_end)
        form.addRow(tr("col_discount"), self.inp_discount)
        form.addRow(tr("monthly_limit"), self.inp_limit)
        form.addRow(tr("payment_terms"), self.cmb_payment)
        form.addRow(tr("col_status"), self.cmb_status)
        form.addRow(tr("notes"), self.inp_notes)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("btn_secondary")
        layout.addWidget(btns)

        if self.record:
            self.inp_title.setText(self.record.get('title', '') or '')
            for i in range(self.cmb_company.count()):
                if self.cmb_company.itemData(i) == self.record.get('company_id'):
                    self.cmb_company.setCurrentIndex(i)
                    break
            if self.record.get('start_date'):
                self.date_start.setDate(QDate.fromString(str(self.record['start_date'])[:10], 'yyyy-MM-dd'))
            if self.record.get('end_date'):
                self.date_end.setDate(QDate.fromString(str(self.record['end_date'])[:10], 'yyyy-MM-dd'))
            self.inp_discount.setValue(self.record.get('discount_percent', 0) or 0)
            self.inp_limit.setValue(self.record.get('monthly_limit', 0) or 0)
            idx_p = self.cmb_payment.findData(self.record.get('payment_terms', 'monthly'))
            if idx_p >= 0:
                self.cmb_payment.setCurrentIndex(idx_p)
            idx_s = self.cmb_status.findData(self.record.get('status', 'active'))
            if idx_s >= 0:
                self.cmb_status.setCurrentIndex(idx_s)
            self.inp_notes.setPlainText(self.record.get('notes', '') or '')

    def _save(self):
        title = self.inp_title.text().strip()
        if not title or self.cmb_company.count() == 0:
            QMessageBox.warning(self, tr("error") if "error" in tr("error") else "Error", tr("contract_title_required"))
            return
        data = dict(
            company_id=self.cmb_company.currentData(),
            title=title,
            start_date=self.date_start.date().toString('yyyy-MM-dd'),
            end_date=self.date_end.date().toString('yyyy-MM-dd'),
            discount_percent=self.inp_discount.value(),
            monthly_limit=self.inp_limit.value(),
            payment_terms=self.cmb_payment.currentData(),
            notes=self.inp_notes.toPlainText().strip(),
        )
        if self.record:
            ContractModel.update(self.record['id'], status=self.cmb_status.currentData(), **data)
            ActivityModel.log(self.user['id'], self.user['username'], 'UPDATE', 'contract', self.record['id'], f"Updated {title}")
        else:
            cid = ContractModel.create(**data)
            ActivityModel.log(self.user['id'], self.user['username'], 'CREATE', 'contract', cid, f"Created {title}")
        self.accept()


# ═══════════════════════ CONTRACTS VIEW ════════════════════════
class ContractsView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_contracts"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.btn_add = make_btn(f"+ {tr('new_contract')}", "btn_primary")
        self.btn_add.clicked.connect(self._add)
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        self.table = DataTable([tr("col_title"), tr("company"), tr("col_start"), tr("col_end"), tr("col_discount"), tr("col_status"), tr("actions")])
        self.table.setColumnWidth(6, 140)
        self.table.horizontalHeader().setSectionResizeMode(6, self.table.horizontalHeader().ResizeMode.Fixed)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_contracts"))
        self.btn_add.setText(f"+ {tr('new_contract')}")
        self.table.setHorizontalHeaderLabels([tr("col_title"), tr("company"), tr("col_start"), tr("col_end"), tr("col_discount"), tr("col_status"), tr("actions")])
        self.refresh()

    def refresh(self):
        self._load(ContractModel.get_all())

    def _load(self, contracts):
        from PyQt6.QtWidgets import QTableWidgetItem
        self.table.setRowCount(len(contracts))
        for r, c in enumerate(contracts):
            self.table.setItem(r, 0, QTableWidgetItem(c.get('title', '') or '—'))
            self.table.setItem(r, 1, QTableWidgetItem(c.get('company_name', '') or '—'))
            self.table.setItem(r, 2, QTableWidgetItem(str(c.get('start_date', ''))[:10]))
            self.table.setItem(r, 3, QTableWidgetItem(str(c.get('end_date', ''))[:10]))
            self.table.setItem(r, 4, QTableWidgetItem(f"{c.get('discount_percent', 0)}%"))
            status = c.get('status', 'active')
            self.table.setItem(r, 5, colored_item(tr(status), status))
            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)
            be = QPushButton(f"✏ {tr('edit')}")
            be.setObjectName("btn_secondary")
            be.setFixedHeight(28)
            be.setCursor(Qt.CursorShape.PointingHandCursor)
            be.clicked.connect(lambda _, row=c: self._edit(row))
            bd = QPushButton("🗑")
            bd.setObjectName("btn_danger")
            bd.setFixedHeight(28)
            bd.setFixedWidth(32)
            bd.setCursor(Qt.CursorShape.PointingHandCursor)
            bd.clicked.connect(lambda _, cid=c['id'], n=c.get('title', ''): self._delete(cid, n))
            al.addWidget(be)
            al.addWidget(bd)
            self.table.setCellWidget(r, 6, actions)
            self.table.setRowHeight(r, 44)

    def _add(self):
        if ContractDialog(self, self.user).exec():
            self.refresh()

    def _edit(self, record):
        if ContractDialog(self, self.user, record).exec():
            self.refresh()

    def _delete(self, cid, name):
        if confirm_delete(self, f'"{name}"'):
            ContractModel.delete(cid)
            ActivityModel.log(self.user['id'], self.user['username'], 'DELETE', 'contract', cid, f"Deleted {name}")
            self.refresh()
