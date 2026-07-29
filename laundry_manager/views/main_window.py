from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSizePolicy, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from views.styles import APP_STYLE
from utils.branding import get_logo_path
from utils.i18n import tr, lang_bus, register_listener, unregister_listener
from utils.theme import PRIMARY, TEXT_ON_DARK, TEXT_ON_DARK_MUTED

NAV_ITEMS = [
    ("🏠", "nav_dashboard", "dashboard"),
    ("📦", "nav_orders", "orders"),
    ("👥", "nav_customers", "customers"),
    ("🏢", "nav_companies", "companies"),
    ("📋", "nav_contracts", "contracts"),
    ("🧾", "nav_invoices", "invoices"),
    ("👕", "nav_catalog", "catalog"),
    ("📊", "nav_reports", "reports"),
    ("📝", "nav_activity", "activity"),
    ("👤", "nav_users", "users"),
    ("⚙️", "nav_settings", "settings"),
]

ADMIN_ONLY = {"users", "activity"}


class MainWindow(QMainWindow):
    def __init__(self, user: dict, on_logout=None):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.nav_keys = {}
        self.pages = {}
        self._sidebar_labels = {}

        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(APP_STYLE)

        self._build_ui()
        register_listener(self._on_language_changed)
        self._navigate("dashboard")

    def closeEvent(self, event):
        unregister_listener(self._on_language_changed)
        super().closeEvent(event)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        h = QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._build_sidebar())

        # Content: grey background + white rounded card
        content_outer = QWidget()
        content_outer.setObjectName("content_area")
        col = QVBoxLayout(content_outer)
        col.setContentsMargins(20, 20, 20, 20)
        col.setSpacing(0)

        self.content_card = QFrame()
        self.content_card.setObjectName("content_card")
        card_layout = QVBoxLayout(self.content_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setObjectName("page_stack")
        card_layout.addWidget(self.stack)
        col.addWidget(self.content_card)

        h.addWidget(content_outer, 1)
        self._load_pages()

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo block
        logo = QWidget()
        ll = QVBoxLayout(logo)
        ll.setContentsMargins(20, 24, 20, 16)
        ll.setSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(12)
        logo_path = get_logo_path()
        if logo_path:
            lbl_icon = QLabel()
            pix = QPixmap(str(logo_path))
            lbl_icon.setPixmap(pix.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))
            row.addWidget(lbl_icon)
        else:
            lbl_icon = QLabel("🧺")
            lbl_icon.setStyleSheet("font-size: 32px;")
            row.addWidget(lbl_icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._lbl_app = QLabel(tr("app_title"))
        self._lbl_app.setObjectName("logo_title")
        self._lbl_app.setWordWrap(True)
        text_col.addWidget(self._lbl_app)
        self._lbl_tag = QLabel(tr("app_tagline"))
        self._lbl_tag.setObjectName("logo_sub")
        self._lbl_tag.setWordWrap(True)
        text_col.addWidget(self._lbl_tag)
        row.addLayout(text_col, 1)
        ll.addLayout(row)
        layout.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sidebar_sep")
        layout.addWidget(sep)

        self._lbl_menu = QLabel(tr("main_menu"))
        self._lbl_menu.setObjectName("nav_section")
        layout.addWidget(self._lbl_menu)
        layout.addSpacing(4)

        for icon, key, page in NAV_ITEMS:
            if page in ADMIN_ONLY and self.user.get("role") != "admin":
                continue
            btn = QPushButton(f"  {icon}   {tr(key)}")
            btn.setObjectName("nav_btn")
            btn.setMinimumHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=page: self._navigate(k))
            self.nav_buttons[page] = btn
            self.nav_keys[page] = (icon, key)
            layout.addWidget(btn)

        layout.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebar_sep")
        layout.addWidget(sep2)

        # User footer
        user_row = QWidget()
        ur = QHBoxLayout(user_row)
        ur.setContentsMargins(16, 12, 16, 12)
        ur.setSpacing(10)

        initial = (self.user.get("full_name") or "U")[:1].upper()
        avatar = QLabel(initial)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {PRIMARY};
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            border-radius: 20px;
        """)
        ur.addWidget(avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(0)
        self._lbl_user = QLabel(self.user.get("full_name", "User"))
        self._lbl_user.setStyleSheet(
            f"color: {TEXT_ON_DARK}; font-size: 13px; font-weight: bold;"
        )
        self._lbl_role = QLabel(self.user.get("role", "staff").upper())
        self._lbl_role.setStyleSheet(f"color: {TEXT_ON_DARK_MUTED}; font-size: 10px;")
        name_col.addWidget(self._lbl_user)
        name_col.addWidget(self._lbl_role)
        ur.addLayout(name_col, 1)

        self.btn_logout = QPushButton("⎋")
        self.btn_logout.setObjectName("btn_logout_icon")
        self.btn_logout.setFixedSize(36, 36)
        self.btn_logout.setToolTip(tr("sign_out"))
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(self._logout)
        ur.addWidget(self.btn_logout)

        layout.addWidget(user_row)
        layout.addSpacing(8)
        return sidebar

    def _load_pages(self):
        from views.dashboard_view import DashboardView
        from views.customers_view import CustomersView
        from views.companies_view import CompaniesView, ContractsView
        from views.orders_view import OrdersView
        from views.invoices_view import InvoicesView
        from views.catalog_view import CatalogView
        from views.reports_view import ReportsView
        from views.users_view import UsersView
        from views.activity_view import ActivityView
        from views.settings_view import SettingsView

        self.pages = {
            "dashboard": DashboardView(self.user, navigate_fn=self._navigate),
            "customers": CustomersView(self.user),
            "companies": CompaniesView(self.user),
            "orders": OrdersView(self.user),
            "invoices": InvoicesView(self.user),
            "contracts": ContractsView(self.user),
            "catalog": CatalogView(self.user),
            "reports": ReportsView(self.user),
            "users": UsersView(self.user),
            "activity": ActivityView(self.user),
            "settings": SettingsView(self.user),
        }
        for widget in self.pages.values():
            self.stack.addWidget(widget)

    def _navigate(self, key: str):
        if key not in self.pages:
            return
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.stack.setCurrentWidget(self.pages[key])
        page = self.pages[key]
        if hasattr(page, "refresh"):
            page.refresh()
        if hasattr(page, "retranslate"):
            page.retranslate()

        if key == "orders" and getattr(self, "_open_new_order", False):
            self._open_new_order = False
            page._new_order()

    def _on_language_changed(self, lang: str):
        if lang == 'ar':
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.retranslate()

    def retranslate(self):
        self.setWindowTitle(tr("app_title"))
        self._lbl_app.setText(tr("app_title"))
        self._lbl_tag.setText(tr("app_tagline"))
        self._lbl_menu.setText(tr("main_menu"))
        self.btn_logout.setToolTip(tr("sign_out"))

        for page, btn in self.nav_buttons.items():
            icon, key = self.nav_keys[page]
            btn.setText(f"  {icon}   {tr(key)}")

        for page in self.pages.values():
            if hasattr(page, "retranslate"):
                page.retranslate()

    def _logout(self):
        reply = QMessageBox.question(
            self, tr("sign_out"), tr("sign_out_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from models.all_models import ActivityModel
            ActivityModel.log(self.user["id"], self.user["username"], "LOGOUT")
            self.close()
            if self.on_logout:
                self.on_logout()
