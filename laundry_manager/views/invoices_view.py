import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDialog, QFrame, QTableWidgetItem, QMessageBox,
    QScrollArea, QFormLayout, QTableWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from models.all_models import InvoiceModel, OrderModel
from views.base_view import (
    DataTable, make_btn, colored_item, table_item,
    page_title, muted_label, field_label, value_label, status_chip, h_separator,
)
from utils.branding import get_logo_path, BUSINESS_NAME
from utils.theme import PRIMARY, NAVY_DARK, TEXT_MUTED
from utils.i18n import tr
from utils.pdf_generator import generate_invoice_pdf


class InvoiceDetailDialog(QDialog):
    def __init__(self, parent, user, invoice):
        super().__init__(parent)
        self.user = user
        self.invoice = invoice
        self.setWindowTitle(f"{tr('nav_invoices')} — {invoice.get('invoice_number','')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scrollable Preview Area (Simulating Google Docs/PDF preview)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: #525659;") # PDF Viewer gray background
        
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(40, 40, 40, 40)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # The "Paper"
        paper = QFrame()
        paper.setFixedWidth(450)
        paper.setStyleSheet("background: white; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);")
        paper_layout = QVBoxLayout(paper)
        paper_layout.setContentsMargins(30, 30, 30, 30)
        paper_layout.setSpacing(15)

        # Receipt Content (Cashier Style)
        header = QVBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_logo_path()
        if logo_path:
            logo_lbl = QLabel()
            pix = QPixmap(str(logo_path))
            logo_lbl.setPixmap(pix.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            header.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        biz_name = QLabel(BUSINESS_NAME.upper())
        biz_name.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        header.addWidget(biz_name, alignment=Qt.AlignmentFlag.AlignCenter)
        header.addWidget(QLabel(tr("app_tagline")), alignment=Qt.AlignmentFlag.AlignCenter)
        paper_layout.addLayout(header)
        
        paper_layout.addWidget(h_separator())
        
        # Details
        details = QFormLayout()
        details.setSpacing(8)
        details.addRow(field_label(tr("invoice_number") + ":"), value_label(self.invoice.get('invoice_number', '')))
        details.addRow(field_label(tr("col_date") + ":"), value_label(str(self.invoice.get('issued_date', ''))[:10]))
        details.addRow(field_label(tr("col_customer") + ":"), value_label(self.invoice.get('customer_name') or self.invoice.get('company_name') or 'Guest'))
        paper_layout.addLayout(details)
        
        paper_layout.addWidget(h_separator())

        # Items Table
        if self.invoice.get('order_id'):
            tbl = QTableWidget()
            tbl.setColumnCount(3)
            tbl.setHorizontalHeaderLabels([tr("items"), tr("qty"), tr("total")])
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tbl.verticalHeader().setVisible(False)
            tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            tbl.setShowGrid(False)
            tbl.setStyleSheet("QTableWidget { border: none; background: white; }")
            
            items = OrderModel.get_items(self.invoice['order_id'])
            tbl.setRowCount(len(items))
            for r, it in enumerate(items):
                tbl.setItem(r, 0, table_item(it.get('item_name', '')))
                tbl.setItem(r, 1, table_item(str(it.get('quantity', 0)), align_center=True))
                tbl.setItem(r, 2, table_item(f"{it.get('total_price', 0):.2f}"))
                tbl.setRowHeight(r, 30)
            
            # Adjust height to content
            tbl.setFixedHeight(len(items) * 30 + 30)
            paper_layout.addWidget(tbl)

        paper_layout.addWidget(h_separator())

        # Totals
        totals = QFormLayout()
        totals.setSpacing(8)
        total_lbl = value_label(f"RM {self.invoice.get('total_amount', 0):.2f}")
        total_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        totals.addRow(field_label(tr("total").upper() + ":"), total_lbl)
        paper_layout.addLayout(totals)
        
        paper_layout.addStretch()
        paper_layout.addWidget(QLabel("THANK YOU!"), alignment=Qt.AlignmentFlag.AlignCenter)

        preview_layout.addWidget(paper)
        scroll.setWidget(preview_container)
        layout.addWidget(scroll)

        # Bottom Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background: #323639; border-top: 1px solid #444;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(20, 10, 20, 10)
        tl.setSpacing(15)

        btn_print = make_btn(f"🖨 {tr('print_invoice')}", "btn_primary")
        btn_print.clicked.connect(self._print)
        
        btn_pdf = make_btn(f"📄 {tr('download_pdf') if 'download_pdf' in tr('download_pdf') else 'PDF'}", "btn_secondary")
        btn_pdf.clicked.connect(self._save_pdf)
        
        btn_send = make_btn(f"✉ {tr('send') if 'send' in tr('send') else 'Send'}", "btn_secondary")
        # btn_send.clicked.connect(self._send)

        tl.addWidget(btn_print)
        tl.addWidget(btn_pdf)
        tl.addWidget(btn_send)
        tl.addStretch()
        
        btn_close = QPushButton(tr("close"))
        btn_close.setObjectName("btn_secondary")
        btn_close.setStyleSheet("background: transparent; color: white; border: 1px solid #666;")
        btn_close.clicked.connect(self.accept)
        tl.addWidget(btn_close)
        
        layout.addWidget(toolbar)

    def _get_pdf_path(self):
        order_items = []
        order = None
        if self.invoice.get('order_id'):
            order_items = OrderModel.get_items(self.invoice['order_id'])
            order = OrderModel.get_by_id(self.invoice['order_id'])
        return generate_invoice_pdf(self.invoice, order_items, order)

    def _print(self):
        try:
            path = self._get_pdf_path()
            if path and os.path.exists(path):
                os.startfile(path) if os.name == 'nt' else subprocess.run(['xdg-open', path])
            else:
                QMessageBox.warning(self, tr("error"), "Generated file not found.")
        except Exception as e:
            import logging
            logging.error(f"Print failed: {e}")
            QMessageBox.warning(self, tr("error"), f"Could not open print preview: {str(e)}")

    def _save_pdf(self):
        from PyQt6.QtWidgets import QFileDialog
        try:
            path = self._get_pdf_path()
            if not path or not os.path.exists(path):
                raise FileNotFoundError("Generated PDF path not found.")
            
            save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"Invoice_{self.invoice['invoice_number']}.pdf", "PDF Files (*.pdf)")
            if save_path:
                import shutil
                shutil.copy2(path, save_path)
                QMessageBox.information(self, tr("success"), f"PDF Saved to {save_path}")
        except Exception as e:
            import logging
            logging.error(f"Failed to save PDF: {e}")
            QMessageBox.critical(self, tr("error"), f"Could not save PDF: {str(e)}")


class InvoicesView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._invoices = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_invoices"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.cmb_status = QComboBox()
        self.cmb_status.setMinimumHeight(36)
        self.cmb_status.setMinimumWidth(130)
        for s in ['all', 'unpaid', 'partial', 'paid']:
            self.cmb_status.addItem(tr(s), s)
        self.cmb_status.currentTextChanged.connect(self.refresh)
        h.addWidget(self.cmb_status)
        layout.addLayout(h)

        self.lbl_count = muted_label("")
        layout.addWidget(self.lbl_count)

        self.table = DataTable([tr("invoice_number"), tr("col_customer"), tr("col_order"), tr("total"), tr("paid"), tr("col_status"), tr("issued_date"), tr("actions")])
        self.table.setColumnWidth(7, 100)
        self.table.horizontalHeader().setSectionResizeMode(7, self.table.horizontalHeader().ResizeMode.Fixed)
        self.table.doubleClicked.connect(self._open_selected)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_invoices"))
        self.cmb_status.blockSignals(True)
        current_data = self.cmb_status.currentData()
        self.cmb_status.clear()
        for s in ['all', 'unpaid', 'partial', 'paid']:
            self.cmb_status.addItem(tr(s), s)
        idx = self.cmb_status.findData(current_data)
        if idx >= 0: self.cmb_status.setCurrentIndex(idx)
        self.cmb_status.blockSignals(False)

        self.table.setHorizontalHeaderLabels([tr("invoice_number"), tr("col_customer"), tr("col_order"), tr("total"), tr("paid"), tr("col_status"), tr("issued_date"), tr("actions")])
        self.refresh()

    def refresh(self):
        status_f = self.cmb_status.currentData() if hasattr(self, 'cmb_status') else 'all'
        self._invoices = InvoiceModel.get_all(status_filter=status_f)
        self.lbl_count.setText(tr("count_invoices", count=len(self._invoices)))
        self.table.setRowCount(len(self._invoices))
        for r, inv in enumerate(self._invoices):
            self.table.setItem(r, 0, table_item(inv.get('invoice_number', '')))
            name = inv.get('customer_name') or inv.get('company_name') or '—'
            self.table.setItem(r, 1, table_item(name))
            self.table.setItem(r, 2, table_item(inv.get('order_number', '') or '—'))
            self.table.setItem(r, 3, table_item(f"RM {inv.get('total_amount', 0):.2f}"))
            self.table.setItem(r, 4, table_item(f"RM {inv.get('paid_amount', 0):.2f}"))
            status = inv.get('status', 'unpaid')
            self.table.setItem(r, 5, colored_item(tr(f"status_{status}"), status))
            self.table.setItem(r, 6, table_item(str(inv.get('issued_date', ''))[:10]))

            btn_view = QPushButton(f"👁 {tr('view') if 'view' in tr('view') else 'View'}")
            btn_view.setObjectName("btn_secondary")
            btn_view.setFixedHeight(28)
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.clicked.connect(lambda _, i=inv: self._open(i))
            w = QWidget()
            wl = QHBoxLayout(w)
            wl.setContentsMargins(4, 2, 4, 2)
            wl.addWidget(btn_view)
            self.table.setCellWidget(r, 7, w)
            self.table.setRowHeight(r, 44)

    def _open(self, invoice):
        InvoiceDetailDialog(self, self.user, invoice).exec()

    def _open_selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(self._invoices):
            self._open(self._invoices[row])
