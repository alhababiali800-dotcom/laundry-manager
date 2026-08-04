import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDialog, QFrame, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDoubleSpinBox, QDateTimeEdit, QScrollArea, QGridLayout,
    QFormLayout, QSizePolicy, QSplitter,
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
from database.connection import Database
from models.all_models import OrderModel, CustomerModel, CompanyModel, ItemTypeModel, ActivityModel
from views.base_view import (
    DataTable, SearchBar, make_btn, colored_item, table_item,
    page_title, muted_label, dialog_title, h_separator, field_label, value_label, status_chip,
)
from utils.theme import (
    TEXT_PRIMARY, TEXT_BODY, TEXT_LABEL, PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED,
    BORDER, BORDER_INPUT, BG_APP, BG_CARD, BG_SUBTLE, DANGER,
)
from utils.i18n import tr


# ════════════════════════ PRODUCT CARD ═══════════════════════
class ProductCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type
        self.setObjectName("product_card")
        self.setFixedSize(155, 190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame#product_card {{
                background: {BG_CARD};
                border: 1.5px solid {BORDER};
                border-radius: 12px;
            }}
            QFrame#product_card:hover {{
                border: 2px solid {PRIMARY};
                background: {BG_SUBTLE};
            }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(135, 90)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_path = self.item_type.get('image_path')
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path)
            self.img_lbl.setPixmap(pix.scaled(125, 85,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            self.img_lbl.setText("👕")
            self.img_lbl.setStyleSheet("font-size: 36px;")
        layout.addWidget(self.img_lbl)

        name_lbl = QLabel(self.item_type['name'])
        name_lbl.setStyleSheet(f"font-weight: bold; color: {TEXT_PRIMARY}; font-size: 12px;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        price_lbl = QLabel(f"RM {self.item_type['wash_price']:.2f}")
        price_lbl.setStyleSheet(f"color: {PRIMARY}; font-weight: bold; font-size: 12px;")
        price_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_lbl)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.item_type)


# ════════════════════════ NEW ORDER DIALOG ════════════════════
class NewOrderDialog(QDialog):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.selected_items = []
        self.setWindowTitle(tr("new_order"))
        self.setModal(True)
        # Open maximised-ish so nothing is ever clipped
        self.resize(1150, 800)
        self.setMinimumSize(860, 600)
        self._build()

    # ──────────────────────────────────────────────────────────
    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT: catalog ─────────────────────────────────────
        left = QWidget()
        left.setStyleSheet(f"background:{BG_CARD};")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 16, 16, 16)
        lv.setSpacing(10)
        lv.addWidget(page_title(tr("catalog_title")))

        cat_scroll = QScrollArea()
        cat_scroll.setWidgetResizable(True)
        cat_scroll.setFrameShape(QFrame.Shape.NoFrame)
        cat_scroll.setStyleSheet("background:transparent; border:none;")
        cat_inner = QWidget()
        cat_inner.setStyleSheet("background:transparent;")
        self.catalog_grid = QGridLayout(cat_inner)
        self.catalog_grid.setSpacing(10)
        self.catalog_grid.setContentsMargins(2, 2, 2, 2)
        self._load_catalog()
        cat_scroll.setWidget(cat_inner)
        lv.addWidget(cat_scroll)
        root.addWidget(left, 3)

        # ── RIGHT: order summary ──────────────────────────────
        # Use QFrame with objectName so stylesheet applies correctly to
        # the background (plain QWidget ignores background-color in dialogs).
        right = QFrame()
        right.setObjectName("orderSummaryPanel")
        right.setAutoFillBackground(True)   # <-- critical for background colour
        right.setStyleSheet(f"""
            QFrame#orderSummaryPanel {{
                background: {BG_APP};
                border-left: 1.5px solid {BORDER};
            }}
            QFrame#orderSummaryPanel QLabel {{
                color: {TEXT_PRIMARY};
                background: transparent;
            }}
            QFrame#orderSummaryPanel QComboBox,
            QFrame#orderSummaryPanel QDateTimeEdit,
            QFrame#orderSummaryPanel QDoubleSpinBox {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_INPUT};
                border-radius: 8px;
                padding: 6px 10px;
                min-height: 32px;
            }}
            QFrame#orderSummaryPanel QComboBox:focus,
            QFrame#orderSummaryPanel QDateTimeEdit:focus,
            QFrame#orderSummaryPanel QDoubleSpinBox:focus {{
                border-color: {PRIMARY};
            }}
            QFrame#orderSummaryPanel QComboBox QAbstractItemView {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                selection-background-color: #1e3a5f;
            }}
        """)
        right.setMinimumWidth(340)
        right.setMaximumWidth(430)

        # Outer layout: scrollable content + fixed button bar at bottom
        right_outer = QVBoxLayout(right)
        right_outer.setContentsMargins(0, 0, 0, 0)
        right_outer.setSpacing(0)

        # Scrollable area for all fields (so nothing ever gets hidden)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setObjectName("orderSummaryInner")
        inner.setStyleSheet("background: transparent;")
        rv = QVBoxLayout(inner)
        rv.setContentsMargins(16, 16, 16, 8)
        rv.setSpacing(6)

        # ── Title
        title_lbl = QLabel(tr("order_details"))
        title_lbl.setStyleSheet(
            f"font-size:16px; font-weight:bold; color:{TEXT_PRIMARY};")
        rv.addWidget(title_lbl)

        sep0 = QFrame()
        sep0.setFrameShape(QFrame.Shape.HLine)
        sep0.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
        rv.addWidget(sep0)
        rv.addSpacing(4)

        # ── Customer
        lbl_cust = QLabel(tr("customer_individual"))
        lbl_cust.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_cust)
        self.cmb_customer = QComboBox()
        self.cmb_customer.addItem(tr("select_customer"), None)
        for c in CustomerModel.get_all():
            self.cmb_customer.addItem(c['name'], c['id'])
        rv.addWidget(self.cmb_customer)

        # ── Company
        lbl_comp = QLabel(tr("or_company"))
        lbl_comp.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_comp)
        self.cmb_company = QComboBox()
        self.cmb_company.addItem(tr("select_company"), None)
        for c in CompanyModel.get_all():
            self.cmb_company.addItem(c['name'], c['id'])
        rv.addWidget(self.cmb_company)

        # ── Items table
        lbl_items = QLabel(tr("items"))
        lbl_items.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_items)

        self.tbl_items = QTableWidget(0, 4)
        self.tbl_items.setHorizontalHeaderLabels(
            [tr("items"), tr("qty"), tr("total"), ""])
        hh = self.tbl_items.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.tbl_items.setColumnWidth(1, 44)
        self.tbl_items.setColumnWidth(2, 76)
        self.tbl_items.setColumnWidth(3, 32)
        self.tbl_items.verticalHeader().setVisible(False)
        self.tbl_items.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_items.setFixedHeight(160)
        self.tbl_items.setAlternatingRowColors(True)
        self.tbl_items.setStyleSheet(f"""
            QTableWidget {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER};
                border-radius: 8px;
                gridline-color: {BG_APP};
                alternate-background-color: {BG_SUBTLE};
            }}
            QTableWidget::item {{
                color: {TEXT_PRIMARY};
                padding: 4px 6px;
            }}
            QHeaderView::section {{
                background: #0c1f3d;
                color: #e8f0fb;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 6px;
                border: none;
            }}
        """)
        rv.addWidget(self.tbl_items)

        # ── Payment method
        lbl_pay = QLabel(tr("payment_method"))
        lbl_pay.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_pay)
        self.cmb_payment = QComboBox()
        for p in ['on_delivery', 'at_order', 'deferred']:
            self.cmb_payment.addItem(tr(p), p)
        rv.addWidget(self.cmb_payment)

        # ── Expected pickup
        lbl_dt = QLabel(tr("expected_pickup"))
        lbl_dt.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_dt)
        self.dt_delivery = QDateTimeEdit(QDateTime.currentDateTime().addDays(2))
        self.dt_delivery.setCalendarPopup(True)
        rv.addWidget(self.dt_delivery)

        # ── Discount
        lbl_disc = QLabel(tr("discount_rm"))
        lbl_disc.setStyleSheet(f"font-size:11px; font-weight:600; color:{TEXT_LABEL};")
        rv.addWidget(lbl_disc)
        self.inp_discount = QDoubleSpinBox()
        self.inp_discount.setPrefix("RM ")
        self.inp_discount.valueChanged.connect(self._refresh_table)
        rv.addWidget(self.inp_discount)

        rv.addSpacing(6)

        # ── Total
        self.lbl_total = QLabel(f"{tr('total')}: RM 0.00")
        self.lbl_total.setStyleSheet(
            f"font-size:15px; font-weight:bold; color:{PRIMARY}; padding:4px 0;")
        rv.addWidget(self.lbl_total)

        rv.addStretch()
        scroll.setWidget(inner)
        right_outer.addWidget(scroll, 1)

        # ── Fixed button bar — always visible at bottom
        btn_bar = QFrame()
        btn_bar.setObjectName("btnBar")
        btn_bar.setStyleSheet(f"""
            QFrame#btnBar {{
                background: {BG_SUBTLE};
                border-top: 1.5px solid {BORDER};
            }}
        """)
        btn_bar.setFixedHeight(62)
        bl = QHBoxLayout(btn_bar)
        bl.setContentsMargins(16, 10, 16, 10)
        bl.setSpacing(10)

        btn_cancel = QPushButton(tr("cancel"))
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setMinimumWidth(90)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{ background:{BG_CARD}; color:{TEXT_BODY};
                border:1.5px solid {BORDER_INPUT}; border-radius:8px;
                font-size:13px; }}
            QPushButton:hover {{ background:{BG_SUBTLE}; border-color:{PRIMARY}; color:{PRIMARY}; }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton(tr("create_order"))
        btn_save.setMinimumHeight(38)
        btn_save.setMinimumWidth(130)
        btn_save.setStyleSheet(f"""
            QPushButton {{ background:{PRIMARY}; color:#ffffff;
                border:none; border-radius:8px; font-size:13px; font-weight:bold; }}
            QPushButton:hover {{ background:{PRIMARY_HOVER}; }}
            QPushButton:pressed {{ background:{PRIMARY_PRESSED}; }}
        """)
        btn_save.clicked.connect(self._save)

        bl.addWidget(btn_cancel)
        bl.addStretch()
        bl.addWidget(btn_save)

        right_outer.addWidget(btn_bar)
        root.addWidget(right)

    # ──────────────────────────────────────────────────────────
    def _load_catalog(self):
        items = ItemTypeModel.get_all()
        for i, it in enumerate(items):
            card = ProductCard(it)
            card.clicked.connect(self._add_item)
            self.catalog_grid.addWidget(card, i // 4, i % 4)

    def _add_item(self, it):
        service = 'wash'
        price   = it['wash_price']
        for existing in self.selected_items:
            if existing['item_type_id'] == it['id'] and existing['service_type'] == service:
                existing['quantity'] += 1
                existing['total_price'] = existing['quantity'] * existing['unit_price']
                self._refresh_table()
                return
        self.selected_items.append({
            'item_type_id': it['id'], 'item_name': it['name'],
            'service_type': service, 'quantity': 1,
            'unit_price': price, 'total_price': price,
        })
        self._refresh_table()

    def _refresh_table(self):
        self.tbl_items.setRowCount(len(self.selected_items))
        total = 0.0
        for r, it in enumerate(self.selected_items):
            bg = QColor(BG_CARD) if r % 2 == 0 else QColor(BG_SUBTLE)
            fg = QColor(TEXT_PRIMARY)

            def cell(text, center=False):
                item = QTableWidgetItem(text)
                item.setForeground(fg)
                item.setBackground(bg)
                if center:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                return item

            self.tbl_items.setItem(r, 0, cell(
                f"{it['item_name']} ({tr(it['service_type'])})"))
            self.tbl_items.setItem(r, 1, cell(str(it['quantity']), center=True))
            self.tbl_items.setItem(r, 2, cell(f"RM {it['total_price']:.2f}"))

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(26, 26)
            del_btn.setStyleSheet(
                "QPushButton{color:#dc2626;border:none;font-weight:bold;"
                "font-size:13px;background:transparent;}"
                "QPushButton:hover{color:#991b1b;}")
            del_btn.clicked.connect(lambda _, idx=r: self._remove(idx))
            self.tbl_items.setCellWidget(r, 3, del_btn)
            self.tbl_items.setRowHeight(r, 34)
            total += it['total_price']

        disc = self.inp_discount.value()
        self.lbl_total.setText(
            f"{tr('total')}: RM {max(0.0, total - disc):.2f}")

    def _remove(self, idx):
        self.selected_items.pop(idx)
        self._refresh_table()

    def _save(self):
        if not self.selected_items:
            QMessageBox.warning(self, tr("error"), "Please add at least one item.")
            return
        cust_id = self.cmb_customer.currentData()
        comp_id = self.cmb_company.currentData()
        if not cust_id and not comp_id:
            QMessageBox.warning(self, tr("error"), "Please select a customer or company.")
            return

        try:
            oid, order_number = OrderModel.create(
                customer_id=cust_id,
                company_id=comp_id,
                items=self.selected_items,
                payment_method=self.cmb_payment.currentData(),
                discount=self.inp_discount.value(),
                notes="",
                created_by=self.user['id'],
                expected_delivery=self.dt_delivery.dateTime().toString(
                    "yyyy-MM-dd HH:mm:ss"),
            )
        except Exception as e:
            QMessageBox.critical(self, tr("error"), f"Failed to save order:\n{e}")
            return

        ActivityModel.log(self.user['id'], self.user['username'],
                          'CREATE', 'order', oid, f"Created {order_number}")

        # Show invoice immediately after saving
        try:
            from views.invoices_view import InvoiceDetailDialog
            from models.all_models import InvoiceModel
            inv_row = Database.fetchone(
                "SELECT id FROM invoices WHERE order_id=?", (oid,))
            if inv_row:
                inv = InvoiceModel.get_by_id(inv_row['id'])
                if inv:
                    InvoiceDetailDialog(self.parent(), self.user, inv).exec()
        except Exception:
            pass  # invoice preview is optional — don't block order creation

        self.accept()


# ════════════════════════ ORDERS VIEW ════════════════════════
class OrdersView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._all_orders = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_orders"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.search = SearchBar(tr("search_orders_ph"))
        self.search.textChanged.connect(self._filter)
        h.addWidget(self.search)
        self.cmb_status = QComboBox()
        self.cmb_status.setMinimumHeight(36)
        self.cmb_status.setMinimumWidth(130)
        for s in ['all', 'received', 'processing', 'ready', 'delivered', 'cancelled']:
            self.cmb_status.addItem(
                tr(s if s == 'all' else f"status_{s}"), s)
        self.cmb_status.currentTextChanged.connect(self.refresh)
        h.addWidget(self.cmb_status)
        self.btn_new = make_btn(f"+ {tr('new_order')}", "btn_primary")
        self.btn_new.clicked.connect(self._new_order)
        h.addWidget(self.btn_new)
        layout.addLayout(h)

        self.lbl_count = muted_label("")
        layout.addWidget(self.lbl_count)

        self.table = DataTable([
            tr("col_order"), tr("col_customer"), tr("expected_pickup"),
            tr("col_status"), tr("payment_method"), tr("total"),
            tr("paid"), tr("col_date"), tr("actions"),
        ])
        self.table.setColumnWidth(8, 140)
        self.table.horizontalHeader().setSectionResizeMode(
            8, self.table.horizontalHeader().ResizeMode.Fixed)
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_orders"))
        self.search.setPlaceholderText(f"🔍  {tr('search_orders_ph')}")
        self.btn_new.setText(f"+ {tr('new_order')}")
        self.table.setHorizontalHeaderLabels([
            tr("col_order"), tr("col_customer"), tr("expected_pickup"),
            tr("col_status"), tr("payment_method"), tr("total"),
            tr("paid"), tr("col_date"), tr("actions"),
        ])
        self.refresh()

    def refresh(self):
        status_f = (self.cmb_status.currentData()
                    if hasattr(self, 'cmb_status') else 'all')
        self._all_orders = OrderModel.get_all(status_filter=status_f)
        self._render(self._all_orders)

    def _filter(self, q):
        if not q.strip():
            self.refresh()
            return
        q = q.lower()
        filtered = [o for o in self._all_orders if
                    q in (o.get('order_number') or '').lower() or
                    q in (o.get('customer_name') or '').lower() or
                    q in (o.get('company_name') or '').lower()]
        self._render(filtered)

    def _render(self, orders):
        self.table.setRowCount(len(orders))
        self.lbl_count.setText(tr("count_orders", count=len(orders)))
        for r, o in enumerate(orders):
            self.table.setItem(r, 0, table_item(o.get('order_number', '')))
            name = o.get('customer_name') or o.get('company_name') or '—'
            self.table.setItem(r, 1, table_item(name))
            d = o.get('expected_delivery')
            self.table.setItem(r, 2, table_item(str(d)[:16] if d else '—'))
            status = o.get('status', '')
            self.table.setItem(r, 3, colored_item(tr(f"status_{status}"), status))
            ps = o.get('payment_status', '')
            self.table.setItem(r, 4, colored_item(tr(f"status_{ps}"), ps))
            self.table.setItem(r, 5, table_item(
                f"RM {o.get('total_amount', 0):.2f}"))
            self.table.setItem(r, 6, table_item(
                f"RM {o.get('paid_amount', 0):.2f}"))
            self.table.setItem(r, 7, table_item(
                str(o.get('created_at', ''))[:10]))

            act = QWidget()
            al = QHBoxLayout(act)
            al.setContentsMargins(4, 2, 4, 2)
            btn = QPushButton(f"👁 {tr('edit')}")
            btn.setObjectName("btn_secondary")
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _, row=o: self._open(row))
            al.addWidget(btn)
            self.table.setCellWidget(r, 8, act)
            self.table.setRowHeight(r, 44)

    def _new_order(self):
        if NewOrderDialog(self, self.user).exec():
            self.refresh()

    def _open(self, order):
        if OrderDetailDialog(self, self.user, order).exec():
            self.refresh()

    def _open_selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(self._all_orders):
            self._open(self._all_orders[row])


# ════════════════════════ ORDER DETAIL DIALOG ════════════════
class OrderDetailDialog(QDialog):
    def __init__(self, parent, user, order):
        super().__init__(parent)
        self.user  = user
        self.order = order
        self.setWindowTitle(
            f"{tr('nav_orders')} — {order.get('order_number', '')}")
        self.resize(860, 580)
        self.setMinimumSize(700, 480)
        self.setModal(True)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left: order details ───────────────────────────────
        left = QWidget()
        left.setStyleSheet(f"background:{BG_CARD};")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(20, 20, 20, 20)
        lv.setSpacing(10)

        lv.addWidget(dialog_title(tr("order_details")))
        lv.addWidget(h_separator())

        info = QFormLayout()
        info.setSpacing(8)
        info.addRow(field_label(tr("col_order") + ":"),
                    value_label(self.order.get('order_number', '')))
        name = self.order.get('customer_name') or self.order.get('company_name') or '—'
        info.addRow(field_label(tr("col_customer") + ":"), value_label(name))
        info.addRow(field_label(tr("col_status") + ":"),
                    status_chip(tr(f"status_{self.order['status']}"), PRIMARY))
        info.addRow(field_label(tr("total") + ":"),
                    value_label(f"RM {self.order.get('total_amount', 0):.2f}"))
        lv.addLayout(info)

        lv.addWidget(field_label(tr("items") + ":"))
        tbl = QTableWidget()
        tbl.setColumnCount(3)
        tbl.setHorizontalHeaderLabels([tr("items"), tr("qty"), tr("total")])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        items = OrderModel.get_items(self.order['id'])
        tbl.setRowCount(len(items))
        for r, it in enumerate(items):
            tbl.setItem(r, 0, table_item(it.get('item_name', '')))
            tbl.setItem(r, 1, table_item(
                str(it.get('quantity', 0)), align_center=True))
            tbl.setItem(r, 2, table_item(
                f"RM {it.get('total_price', 0):.2f}"))
        lv.addWidget(tbl)

        lv.addWidget(h_separator())

        # Status change buttons
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addWidget(field_label(tr("col_status") + ":"))
        for s in ['processing', 'ready', 'delivered', 'cancelled']:
            if s != self.order['status']:
                b = make_btn(tr(f"status_{s}"), "btn_secondary")
                b.setMinimumHeight(34)
                b.clicked.connect(lambda _, st=s: self._update_status(st))
                status_row.addWidget(b)
        status_row.addStretch()
        lv.addLayout(status_row)

        lv.addStretch()
        root.addWidget(left, 1)

        # ── Right: invoice preview ────────────────────────────
        right = QFrame()
        right.setFixedWidth(300)
        right.setStyleSheet(
            f"background:{BG_SUBTLE}; border-left:1.5px solid {BORDER};")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(20, 20, 20, 20)
        rv.setSpacing(10)

        lbl = QLabel(tr("invoice_preview"))
        lbl.setStyleSheet(
            f"font-weight:bold; color:{PRIMARY}; font-size:15px;")
        rv.addWidget(lbl)
        rv.addWidget(h_separator())

        icon = QLabel("🧾")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size:56px; padding:20px 0;")
        rv.addWidget(icon)

        msg = QLabel("Invoice is ready for viewing.")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:13px;")
        rv.addWidget(msg)

        rv.addStretch()

        btn_inv = make_btn(tr("view_invoice"), "btn_primary")
        btn_inv.setMinimumHeight(42)
        btn_inv.clicked.connect(self._view_invoice)
        rv.addWidget(btn_inv)

        root.addWidget(right)

    def _update_status(self, status):
        OrderModel.update_status(self.order['id'], status)
        ActivityModel.log(self.user['id'], self.user['username'],
                          'UPDATE', 'order', self.order['id'],
                          f"Status -> {status}")
        self.accept()

    def _view_invoice(self):
        from views.invoices_view import InvoiceDetailDialog
        from models.all_models import InvoiceModel
        row = Database.fetchone(
            "SELECT id FROM invoices WHERE order_id=?", (self.order['id'],))
        if row:
            inv = InvoiceModel.get_by_id(row['id'])
            if inv:
                InvoiceDetailDialog(self, self.user, inv).exec()
                return
        QMessageBox.warning(self, tr("error"), "No invoice found for this order.")