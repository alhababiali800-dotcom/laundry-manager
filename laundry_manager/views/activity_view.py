# activity_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidgetItem, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from models.all_models import ActivityModel
from views.base_view import DataTable, make_btn, page_title, muted_label
from utils.i18n import tr


class ActivityView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("nav_activity"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.btn_refresh = make_btn(f"↻ {tr('refresh')}", "btn_secondary")
        self.btn_refresh.clicked.connect(self.refresh)
        h.addWidget(self.btn_refresh)
        layout.addLayout(h)

        self.lbl_sub = muted_label(tr("activity_log_sub"))
        layout.addWidget(self.lbl_sub)

        self.table = DataTable(["#", tr("col_user"), tr("col_action") if "col_action" in tr("col_action") else tr("Action"), tr("col_entity"), tr("col_description"), tr("col_datetime")])
        # Update: use explicit keys if they exist, otherwise fallback
        self.table.setHorizontalHeaderLabels([
            "#", tr("col_user"), tr("col_status"), tr("col_entity"), tr("col_description"), tr("col_datetime")
        ])
        
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Fixed)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("nav_activity"))
        self.btn_refresh.setText(f"↻ {tr('refresh')}")
        self.lbl_sub.setText(tr("activity_log_sub"))
        self.table.setHorizontalHeaderLabels([
            "#", tr("col_user"), tr("col_status"), tr("col_entity"), tr("col_description"), tr("col_datetime")
        ])
        self.refresh()

    def refresh(self):
        logs = ActivityModel.get_all(limit=200)
        self.table.setRowCount(len(logs))
        ACTION_COLORS = {
            'CREATE': '#dcfce7', 'UPDATE': '#dbeafe',
            'DELETE': '#fee2e2', 'LOGIN': '#fef9c3',
            'LOGOUT': '#f1f5f9', 'PAYMENT': '#e0f2fe',
        }
        from PyQt6.QtGui import QColor
        for r, log in enumerate(logs):
            self.table.setItem(r, 0, QTableWidgetItem(str(log.get('id', ''))))
            self.table.setItem(r, 1, QTableWidgetItem(log.get('username', '') or '—'))

            action = log.get('action', '')
            action_key = f"{action.lower()}_action"
            display_action = tr(action_key) if action_key in tr(action_key) else action
            action_item = QTableWidgetItem(display_action)
            action_item.setBackground(QColor(ACTION_COLORS.get(action, '#f8fafc')))
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r, 2, action_item)

            entity = f"{log.get('entity_type','')} #{log.get('entity_id','')}" if log.get('entity_id') else log.get('entity_type','') or '—'
            self.table.setItem(r, 3, QTableWidgetItem(entity))
            self.table.setItem(r, 4, QTableWidgetItem(log.get('description', '') or '—'))
            self.table.setItem(r, 5, QTableWidgetItem(str(log.get('created_at', ''))[:19]))
            self.table.setRowHeight(r, 38)
