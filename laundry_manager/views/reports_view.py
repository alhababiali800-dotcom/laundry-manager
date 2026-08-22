from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFontMetrics, QPainter, QPen
from database.connection import Database
from utils.theme import BG_CARD, BORDER, TEXT_PRIMARY, TEXT_MUTED, PRIMARY
from views.base_view import page_title, muted_label, value_label
from utils.i18n import tr


class BarChart(QFrame):
    """Small dependency-free chart for report data."""
    def __init__(self, color="#2563eb", parent=None):
        super().__init__(parent)
        self.values = []
        self.color = QColor(color)
        self.setMinimumHeight(230)
        self.setStyleSheet(
            f"background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;"
        )

    def set_data(self, values):
        self.values = values
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(38, 16, -18, -34)
        if not self.values:
            painter.setPen(QColor(TEXT_MUTED))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, tr("no_report_data"))
            return
        maximum = max(value for _, value in self.values) or 1
        bar_width = max(14, min(52, rect.width() // (len(self.values) * 2)))
        gap = rect.width() / len(self.values)
        painter.setPen(QPen(QColor(BORDER), 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())
        painter.setPen(QColor(TEXT_MUTED))
        metrics = QFontMetrics(painter.font())
        for index, (label, value) in enumerate(self.values):
            height = int((value / maximum) * max(1, rect.height() - 24))
            x = int(rect.left() + gap * index + (gap - bar_width) / 2)
            y = rect.bottom() - height
            painter.fillRect(x, y, bar_width, height, self.color)
            shown_label = metrics.elidedText(str(label), Qt.TextElideMode.ElideRight, int(gap - 4))
            painter.drawText(int(rect.left() + gap * index), rect.bottom() + 5,
                             int(gap), 18, Qt.AlignmentFlag.AlignHCenter, shown_label)
            painter.drawText(x, max(0, y - 18), bar_width, 16,
                             Qt.AlignmentFlag.AlignHCenter, f"{value:,.0f}")


class ReportsView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self.lbl_title = page_title(tr("reports_title"))
        layout.addWidget(self.lbl_title)

        # Summary cards
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        self._refresh_stats()
        layout.addLayout(self.stats_grid)

        # Top customers
        self.lbl_top_cust = self._section(tr("top_customers"))
        layout.addWidget(self.lbl_top_cust)
        self.tbl_top_cust = self._make_table([tr("col_customer"), tr("nav_orders"), tr("total")])
        layout.addWidget(self.tbl_top_cust)

        # Monthly revenue
        self.lbl_monthly_rev = self._section(tr("monthly_revenue"))
        layout.addWidget(self.lbl_monthly_rev)
        self.tbl_monthly_rev = self._make_table([tr("month"), tr("nav_orders"), tr("stat_revenue")])
        layout.addWidget(self.tbl_monthly_rev)
        self.monthly_chart = BarChart("#2563eb")
        layout.addWidget(self.monthly_chart)

        # Popular items
        self.lbl_popular = self._section(tr("popular_items"))
        layout.addWidget(self.lbl_popular)
        self.tbl_popular = self._make_table([tr("items"), tr("times_ordered"), tr("stat_revenue")])
        layout.addWidget(self.tbl_popular)
        self.items_chart = BarChart("#15803d")
        layout.addWidget(self.items_chart)
        
        layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("reports_title"))
        self._refresh_stats()
        self.lbl_top_cust.setText(tr("top_customers"))
        self.tbl_top_cust.setHorizontalHeaderLabels([tr("col_customer"), tr("nav_orders"), tr("total")])
        self.lbl_monthly_rev.setText(tr("monthly_revenue"))
        self.tbl_monthly_rev.setHorizontalHeaderLabels([tr("month"), tr("nav_orders"), tr("stat_revenue")])
        self.lbl_popular.setText(tr("popular_items"))
        self.tbl_popular.setHorizontalHeaderLabels([tr("items"), tr("times_ordered"), tr("stat_revenue")])
        self.refresh()

    def refresh(self):
        # Top customers
        rows = Database.fetchall("""
            SELECT c.name, COUNT(o.id) as cnt, COALESCE(SUM(o.total_amount),0) as total
            FROM orders o JOIN customers c ON o.customer_id=c.id
            GROUP BY c.id ORDER BY cnt DESC LIMIT 10
        """)
        self.tbl_top_cust.setRowCount(len(rows))
        for r, row in enumerate(rows):
            self.tbl_top_cust.setItem(r, 0, QTableWidgetItem(row['name']))
            self.tbl_top_cust.setItem(r, 1, QTableWidgetItem(str(row['cnt'])))
            self.tbl_top_cust.setItem(r, 2, QTableWidgetItem(f"RM {row['total']:.2f}"))
            self.tbl_top_cust.setRowHeight(r, 38)
        self.tbl_top_cust.setMaximumHeight(280)

        # Monthly revenue
        rows2 = Database.fetchall("""
            SELECT strftime('%Y-%m', created_at) as month,
                   COUNT(*) as cnt,
                   COALESCE(SUM(total_amount),0) as total
            FROM orders
            GROUP BY month ORDER BY month DESC LIMIT 6
        """)
        self.tbl_monthly_rev.setRowCount(len(rows2))
        for r, row in enumerate(rows2):
            self.tbl_monthly_rev.setItem(r, 0, QTableWidgetItem(row['month']))
            self.tbl_monthly_rev.setItem(r, 1, QTableWidgetItem(str(row['cnt'])))
            self.tbl_monthly_rev.setItem(r, 2, QTableWidgetItem(f"RM {row['total']:.2f}"))
            self.tbl_monthly_rev.setRowHeight(r, 38)
        self.tbl_monthly_rev.setMaximumHeight(220)
        self.monthly_chart.set_data([(row['month'], float(row['total'])) for row in reversed(rows2)])

        # Popular items
        rows3 = Database.fetchall("""
            SELECT item_name, COUNT(*) as cnt, SUM(total_price) as total
            FROM order_items GROUP BY item_name ORDER BY cnt DESC LIMIT 10
        """)
        self.tbl_popular.setRowCount(len(rows3))
        for r, row in enumerate(rows3):
            self.tbl_popular.setItem(r, 0, QTableWidgetItem(row['item_name']))
            self.tbl_popular.setItem(r, 1, QTableWidgetItem(str(row['cnt'])))
            self.tbl_popular.setItem(r, 2, QTableWidgetItem(f"RM {row['total']:.2f}"))
            self.tbl_popular.setRowHeight(r, 38)
        self.tbl_popular.setMaximumHeight(280)
        self.items_chart.set_data([(row['item_name'], float(row['cnt'])) for row in rows3])

    def _refresh_stats(self):
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        stats = self._get_stats()
        card_data = [
            ("📦", tr("total_orders"), str(stats.get('total_orders', 0)), "#6366f1"),
            ("✅", tr("status_delivered"), str(stats.get('delivered', 0)), "#22c55e"),
            ("⏳", tr("stat_in_progress"), str(stats.get('active', 0)), "#f59e0b"),
            ("💰", tr("total_revenue"), f"RM {stats.get('revenue', 0):.2f}", "#0ea5e9"),
            ("🧾", tr("nav_invoices"), str(stats.get('invoices', 0)), "#8b5cf6"),
            ("👥", tr("nav_customers"), str(stats.get('customers', 0)), "#ec4899"),
        ]
        for i, (icon, label, val, color) in enumerate(card_data):
            card = QFrame()
            card.setObjectName("stat_card")
            card.setStyleSheet(
                f"QFrame#stat_card{{background:{BG_CARD};border:1px solid {BORDER};"
                f"border-radius:14px;border-left:4px solid {color};}}"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.addWidget(self._icon_lbl(icon))
            v = value_label(val)
            v.setStyleSheet(f"font-size:24px;font-weight:bold;color:{TEXT_PRIMARY};")
            cl.addWidget(v)
            l = muted_label(label)
            cl.addWidget(l)
            card.setMinimumHeight(110)
            self.stats_grid.addWidget(card, i // 3, i % 3)

    def _get_stats(self):
        from models.all_models import OrderModel, CustomerModel, InvoiceModel
        s = OrderModel.count_by_status()
        return {
            'total_orders': sum(s.values()),
            'delivered': s.get('delivered', 0),
            'active': s.get('received', 0) + s.get('processing', 0),
            'revenue': OrderModel.revenue_month(),
            'invoices': InvoiceModel.count_unpaid(),
            'customers': CustomerModel.count(),
        }

    def _icon_lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size:22px;")
        return l

    def _section(self, text):
        l = page_title(text)
        l.setStyleSheet(f"font-size:15px;font-weight:bold;color:{TEXT_PRIMARY};")
        return l

    def _make_table(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setShowGrid(False)
        return t
