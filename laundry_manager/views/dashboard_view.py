from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QTableWidget, QHeaderView, QScrollArea,
    QLineEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from models.all_models import OrderModel, CustomerModel, ActivityModel
from datetime import datetime
from utils.i18n import tr, format_date, status_label
from utils.theme import PRIMARY, BORDER, BG_CARD, TEXT_PRIMARY, TEXT_LABEL, TEXT_MUTED
from views.base_view import table_item, muted_label, page_heading, field_label, make_btn
from views.widgets.lang_toggle import LanguageToggle


class DashboardView(QWidget):
    def __init__(self, user, navigate_fn=None):
        super().__init__()
        self.user = user
        self.navigate = navigate_fn
        self._qa_buttons = []
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)

        header = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(4)
        self.lbl_welcome = muted_label(tr("welcome_back"))
        self.lbl_welcome.setStyleSheet(f"font-size: 14px; color: {TEXT_MUTED};")
        self.lbl_date = page_heading(format_date(datetime.now()))
        left.addWidget(self.lbl_welcome)
        left.addWidget(self.lbl_date)
        header.addLayout(left)
        header.addStretch()

        right = QHBoxLayout()
        right.setSpacing(12)
        self.lang_toggle = LanguageToggle()
        right.addWidget(self.lang_toggle)
        header.addLayout(right)
        layout.addLayout(header)

        # Stats
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        layout.addLayout(self.stats_grid)

        # Quick Actions & Quick Customer
        middle_row = QHBoxLayout()
        middle_row.setSpacing(20)

        # Left: Quick Actions
        qa_col = QVBoxLayout()
        self.lbl_qa = page_heading(tr("quick_actions"))
        self.lbl_qa.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY};")
        qa_col.addWidget(self.lbl_qa)
        
        qa_grid = QGridLayout()
        qa_grid.setSpacing(10)
        quick_actions = [
            ("qa_new_order", "#dbeafe", PRIMARY, "📦", "orders"),
            ("qa_add_customer", "#dcfce7", "#16a34a", "👤", "customers"),
            ("qa_new_contract", "#f3e8ff", "#7c3aed", "📋", "contracts"),
            ("qa_view_invoices", "#fef9c3", "#ca8a04", "🧾", "invoices"),
        ]
        for i, (key, bg, fg, icon, page) in enumerate(quick_actions):
            btn = QPushButton()
            btn.setMinimumHeight(56)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("qa_key", key)
            btn.setProperty("qa_bg", bg)
            btn.setProperty("qa_fg", fg)
            self._style_qa_btn(btn, bg, fg, icon, tr(key))
            btn.clicked.connect(lambda _, p=page: self._go(p))
            qa_grid.addWidget(btn, i // 2, i % 2)
            self._qa_buttons.append(btn)
        qa_col.addLayout(qa_grid)
        middle_row.addLayout(qa_col, 1)

        # Right: Quick Customer Entry
        qc_card = QFrame()
        qc_card.setObjectName("qc_card")
        qc_card.setStyleSheet(f"QFrame#qc_card{{background:{BG_CARD}; border:1px solid {BORDER}; border-radius:14px;}}")
        qcl = QVBoxLayout(qc_card)
        qcl.setContentsMargins(20, 16, 20, 16)
        self.lbl_qc = page_heading(tr("new_customer"))
        self.lbl_qc.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {TEXT_PRIMARY};")
        qcl.addWidget(self.lbl_qc)
        
        form = QFormLayout()
        form.setSpacing(8)
        self.qc_name = QLineEdit(); self.qc_name.setPlaceholderText(tr("name"))
        self.qc_phone = QLineEdit(); self.qc_phone.setPlaceholderText(tr("phone"))
        form.addRow(field_label(tr("name")), self.qc_name)
        form.addRow(field_label(tr("phone")), self.qc_phone)
        qcl.addLayout(form)
        
        self.btn_qc_save = make_btn(tr("save"), "btn_primary")
        self.btn_qc_save.clicked.connect(self._quick_customer_save)
        qcl.addWidget(self.btn_qc_save)
        middle_row.addWidget(qc_card, 1)
        
        layout.addLayout(middle_row)

        self.lbl_recent = page_heading(tr("recent_orders"))
        self.lbl_recent.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(self.lbl_recent)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels([
            tr("col_order"), tr("col_customer"), tr("col_status"),
            tr("col_amount"), tr("col_date"),
        ])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl.setMaximumHeight(280)
        self.tbl.setShowGrid(False)
        layout.addWidget(self.tbl)
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.refresh()

    def _style_qa_btn(self, btn, bg, fg, icon, text):
        btn.setText(f"  {icon}  {text}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 14px 20px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {bg};
                border: 1px solid {fg};
            }}
        """)

    def _go(self, page):
        if self.navigate:
            self.navigate(page)

    def _quick_customer_save(self):
        name = self.qc_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("error"), tr("customer_name_required"))
            return
        cid = CustomerModel.create(name=name, phone=self.qc_phone.text().strip(), email='', address='', customer_type='individual', company_id=None, notes='')
        ActivityModel.log(self.user['id'], self.user['username'], 'CREATE', 'customer', cid, f"Quick created {name}")
        QMessageBox.information(self, tr("success"), tr("success"))
        self.qc_name.clear()
        self.qc_phone.clear()

    def retranslate(self):
        self.lbl_welcome.setText(tr("welcome_back"))
        self.lbl_date.setText(format_date(datetime.now()))
        self.lbl_qa.setText(tr("quick_actions"))
        self.lbl_qc.setText(tr("new_customer"))
        self.btn_qc_save.setText(tr("save"))
        self.lbl_recent.setText(tr("recent_orders"))
        self.tbl.setHorizontalHeaderLabels([
            tr("col_order"), tr("col_customer"), tr("col_status"),
            tr("col_amount"), tr("col_date"),
        ])
        self.lang_toggle.retranslate()
        for btn in self._qa_buttons:
            key = btn.property("qa_key")
            bg = btn.property("qa_bg")
            fg = btn.property("qa_fg")
            icons = {
                "qa_new_order": "📦", "qa_add_customer": "👤",
                "qa_new_contract": "📋", "qa_view_invoices": "🧾",
            }
            self._style_qa_btn(btn, bg, fg, icons.get(key, ""), tr(key))
        
        from utils.i18n import get_lang
        if get_lang() == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            
        self.refresh()

    def refresh(self):
        self._load_stats()
        self._load_recent()

    def _load_stats(self):
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        statuses = OrderModel.count_by_status()
        cards = [
            ("📦", str(OrderModel.count_today()), tr("stat_today_orders"), tr("stat_today_sub"), PRIMARY, "#eff6ff"),
            ("⏳", str(statuses.get("processing", 0)), tr("stat_in_progress"), tr("stat_in_progress_sub"), "#f59e0b", "#fffbeb"),
            ("✅", str(statuses.get("ready", 0)), tr("stat_ready"), tr("stat_ready_sub"), "#22c55e", "#f0fdf4"),
            ("💰", f"RM {OrderModel.revenue_month():.0f}", tr("stat_revenue"), tr("stat_revenue_sub"), "#1e3a5f", "#f1f5f9"),
        ]
        for i, (icon, val, title, sub, accent, bg) in enumerate(cards):
            card = QFrame()
            card.setObjectName("stat_card")
            card.setStyleSheet(f"QFrame#stat_card {{ background: {bg}; border: 1px solid {BORDER}; border-radius: 14px; }}")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 18, 20, 18)
            cl.setSpacing(16)

            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(48, 48)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"background: {accent}; color: white; font-size: 22px; border-radius: 12px;")
            cl.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            val_lbl = QLabel(val)
            val_lbl.setObjectName("page_heading")
            val_lbl.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {TEXT_PRIMARY};")
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {TEXT_LABEL};")
            sub_lbl = muted_label(sub)
            text_col.addWidget(val_lbl)
            text_col.addWidget(title_lbl)
            text_col.addWidget(sub_lbl)
            cl.addLayout(text_col, 1)

            card.setMinimumHeight(100)
            self.stats_grid.addWidget(card, 0, i)

    def _load_recent(self):
        STATUS_BG = {
            "received": "#dbeafe", "processing": "#fef9c3",
            "ready": "#dcfce7", "delivered": "#f1f5f9", "cancelled": "#fee2e2",
        }
        orders = OrderModel.get_all()[:8]
        self.tbl.setRowCount(len(orders))
        for r, o in enumerate(orders):
            self.tbl.setItem(r, 0, table_item(o.get("order_number", "")))
            name = o.get("customer_name") or o.get("company_name") or "—"
            self.tbl.setItem(r, 1, table_item(name))
            status = o.get("status", "")
            st_item = table_item(status_label(status), align_center=True)
            st_item.setBackground(QColor(STATUS_BG.get(status, "#f1f5f9")))
            self.tbl.setItem(r, 2, st_item)
            self.tbl.setItem(r, 3, table_item(f"RM {o.get('total_amount', 0):.2f}"))
            self.tbl.setItem(r, 4, table_item(str(o.get("created_at", ""))[:10]))
            self.tbl.setRowHeight(r, 42)
