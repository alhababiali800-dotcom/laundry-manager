"""Bilingual UI strings (English / Arabic) with RTL support."""
from __future__ import annotations
import json
import os
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

_current = "ar"
_listeners: list = []

def _config_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home())) / "InternationalLaundries"
    else:
        base = Path.home() / ".international_laundries"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"

def load_saved_language() -> str:
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
        lang = data.get("language", "ar")
        return lang if lang in ("en", "ar") else "ar"
    except (OSError, json.JSONDecodeError, KeyError):
        return "ar"

def init_language():
    global _current
    _current = load_saved_language()
    apply_layout_direction()

def save_language(lang: str) -> None:
    path = _config_path()
    data = {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    data["language"] = lang
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def apply_layout_direction():
    app = QApplication.instance()
    if app:
        if _current == "ar":
            app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

class LanguageBus(QObject):
    changed = pyqtSignal(str)
    def set(self, lang: str) -> None:
        global _current
        if lang not in TRANSLATIONS: return
        if lang == _current: return
        _current = lang
        save_language(lang)
        apply_layout_direction()
        self.changed.emit(lang)
        for cb in list(_listeners):
            try: cb(lang)
            except: pass

lang_bus = LanguageBus()

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "International Laundries",
        "app_tagline": "Professional Garment Care",
        "login_title": "Welcome Back",
        "login_sub": "Please enter your credentials to access your account",
        "username": "Username",
        "password": "Password",
        "username_ph": "Enter username",
        "password_ph": "Enter password",
        "sign_in": "Sign In",
        "signing_in": "Signing In...",
        "login_error_empty": "Please enter username and password",
        "login_error_invalid": "Invalid username or password",
        "login_hint": "Forgot password? Contact Administrator",
        "main_menu": "MAIN MENU",
        "nav_dashboard": "Dashboard",
        "nav_orders": "Orders",
        "nav_customers": "Customers",
        "nav_companies": "Companies",
        "nav_contracts": "Contracts",
        "nav_invoices": "Invoices",
        "nav_catalog": "Catalog",
        "nav_reports": "Reports",
        "nav_activity": "Activity Log",
        "nav_users": "Users",
        "nav_settings": "Settings",
        "welcome_back": "Welcome back,",
        "quick_actions": "Quick Actions",
        "qa_new_order": "New Order",
        "qa_add_customer": "Add Customer",
        "qa_new_contract": "New Contract",
        "qa_view_invoices": "View Invoices",
        "recent_orders": "Recent Orders",
        "stat_today_orders": "Today's Orders",
        "stat_today_sub": "Orders received today",
        "stat_in_progress": "In Progress",
        "stat_in_progress_sub": "Orders being processed",
        "stat_ready": "Ready for Pickup",
        "stat_ready_sub": "Completed orders",
        "stat_revenue": "Monthly Revenue",
        "stat_revenue_sub": "Total paid this month",
        "new_customer": "New Customer",
        "edit_customer": "Edit Customer",
        "name": "Name",
        "phone": "Phone",
        "email": "Email",
        "address": "Address",
        "type": "Type",
        "individual": "Individual",
        "company": "Company",
        "none": "None",
        "notes": "Notes",
        "notes_ph": "Add any special instructions...",
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "actions": "Actions",
        "search_ph": "Search...",
        "search_customers_ph": "Search customers...",
        "search_orders_ph": "Search orders...",
        "count_customers": "{count} Customers total",
        "count_orders": "{count} Orders found",
        "count_invoices": "{count} Invoices total",
        "error": "Error",
        "success": "Success",
        "customer_name_required": "Customer name is required",
        "item_name": "Item Name",
        "wash_price": "Wash Price",
        "iron_price": "Iron Price",
        "dry_clean_price": "Dry Clean Price",
        "active": "Active",
        "active_status": "Active",
        "inactive_status": "Inactive",
        "new_item": "New Item",
        "edit_item": "Edit Item",
        "item_name_required": "Item name is required",
        "catalog_title": "Service Catalog",
        "catalog_sub": "Manage your laundry items and pricing",
        "col_wash_rm": "Wash (RM)",
        "col_iron_rm": "Iron (RM)",
        "col_dry_rm": "Dry Clean (RM)",
        "col_status": "Status",
        "status_received": "Received",
        "status_processing": "Processing",
        "status_ready": "Ready",
        "status_delivered": "Delivered",
        "status_cancelled": "Cancelled",
        "status_paid": "Paid",
        "status_partial": "Partial",
        "status_unpaid": "Unpaid",
        "status_pending": "Pending",
        "col_order": "Order #",
        "col_customer": "Customer",
        "col_amount": "Amount",
        "col_date": "Date",
        "col_user": "User",
        "col_action": "Action",
        "col_entity": "Entity",
        "col_description": "Description",
        "col_datetime": "Date & Time",
        "refresh": "Refresh",
        "activity_log_sub": "System activity and audit trail",
        "expected_pickup": "Expected Pickup",
        "payment_method": "Payment",
        "total": "Total",
        "paid": "Paid",
        "create_order": "Create Order",
        "order_details": "Order Details",
        "select_customer": "Select Customer",
        "select_company": "Select Company",
        "customer_individual": "Individual Customer",
        "or_company": "Or Company/Contract",
        "on_delivery": "Pay on Delivery",
        "at_order": "Pay at Order",
        "deferred": "Deferred/Invoice",
        "discount_rm": "Discount (RM)",
        "items": "Items",
        "qty": "Qty",
        "invoice_number": "Invoice #",
        "issued_date": "Issued Date",
        "print_invoice": "Print Invoice",
        "download_pdf": "Download PDF",
        "invoice_preview": "Invoice Preview",
        "view_invoice": "View Invoice",
        "close": "Close",
        "all": "All",
        "lang_en": "English",
        "lang_ar": "العربية",
        "sign_out": "Sign Out",
        "sign_out_confirm": "Are you sure you want to sign out?",
        "upload": "Upload",
        "view": "View",
        "wash": "Wash",
        "iron": "Iron",
        "dry_clean": "Dry Clean",
        "invoice_ready_msg": "Invoice is ready for viewing and printing",
        "tab_password": "Password",
        "tab_about": "About",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "update_password": "Update Password",
        "version": "Version",
        "built_with": "Built with",
        "database": "Database",
        "db_location": "DB Location",
        "logged_in_as": "Logged in as",
        "software_note": "This software is designed for professional laundry management.",
        "all_fields_required": "All fields are required",
        "passwords_mismatch": "Passwords do not match",
        "password_too_short": "Password too short (min 6 chars)",
        "current_password_incorrect": "Current password incorrect",
        "password_updated_success": "Password updated successfully",
    },
    "ar": {
        "app_title": "المغاسل الدولية",
        "app_tagline": "العناية المهنية بالملابس",
        "login_title": "مرحباً بك مجدداً",
        "login_sub": "يرجى إدخال بيانات الاعتماد للوصول إلى حسابك",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "username_ph": "أدخل اسم المستخدم",
        "password_ph": "أدخل كلمة المرور",
        "sign_in": "تسجيل الدخول",
        "signing_in": "جاري تسجيل الدخول...",
        "login_error_empty": "يرجى إدخال اسم المستخدم وكلمة المرور",
        "login_error_invalid": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "login_hint": "نسيت كلمة المرور؟ اتصل بالمسؤول",
        "main_menu": "القائمة الرئيسية",
        "nav_dashboard": "لوحة التحكم",
        "nav_orders": "الطلبات",
        "nav_customers": "العملاء",
        "nav_companies": "الشركات",
        "nav_contracts": "العقود",
        "nav_invoices": "الفواتير",
        "nav_catalog": "الكتالوج",
        "nav_reports": "التقارير",
        "nav_activity": "سجل النشاطات",
        "nav_users": "المستخدمين",
        "nav_settings": "الإعدادات",
        "welcome_back": "مرحباً بك مجدداً،",
        "quick_actions": "إجراءات سريعة",
        "qa_new_order": "طلب جديد",
        "qa_add_customer": "إضافة عميل",
        "qa_new_contract": "عقد جديد",
        "qa_view_invoices": "عرض الفواتير",
        "recent_orders": "أحدث الطلبات",
        "stat_today_orders": "طلبات اليوم",
        "stat_today_sub": "الطلبات المستلمة اليوم",
        "stat_in_progress": "قيد التنفيذ",
        "stat_in_progress_sub": "طلبات قيد المعالجة",
        "stat_ready": "جاهز للاستلام",
        "stat_ready_sub": "الطلبات المكتملة",
        "stat_revenue": "الإيرادات الشهرية",
        "stat_revenue_sub": "إجمالي المدفوعات هذا الشهر",
        "new_customer": "عميل جديد",
        "edit_customer": "تعديل عميل",
        "name": "الاسم",
        "phone": "الهاتف",
        "email": "البريد الإلكتروني",
        "address": "العنوان",
        "type": "النوع",
        "individual": "فرد",
        "company": "شركة",
        "none": "لا يوجد",
        "notes": "ملاحظات",
        "notes_ph": "أضف أي تعليمات خاصة...",
        "save": "حفظ",
        "cancel": "إلغاء",
        "edit": "تعديل",
        "delete": "حذف",
        "actions": "الإجراءات",
        "search_ph": "بحث...",
        "search_customers_ph": "البحث عن عملاء...",
        "search_orders_ph": "البحث عن طلبات...",
        "count_customers": "إجمالي العملاء: {count}",
        "count_orders": "تم العثور على {count} طلبات",
        "count_invoices": "إجمالي الفواتير: {count}",
        "error": "خطأ",
        "success": "نجاح",
        "customer_name_required": "اسم العميل مطلوب",
        "item_name": "اسم العنصر",
        "wash_price": "سعر الغسيل",
        "iron_price": "سعر الكي",
        "dry_clean_price": "سعر التنظيف الجاف",
        "active": "نشط",
        "active_status": "نشط",
        "inactive_status": "غير نشط",
        "new_item": "عنصر جديد",
        "edit_item": "تعديل عنصر",
        "item_name_required": "اسم العنصر مطلوب",
        "catalog_title": "كتالوج الخدمات",
        "catalog_sub": "إدارة عناصر المغسلة والأسعار",
        "col_wash_rm": "غسيل (ر.س)",
        "col_iron_rm": "كي (ر.س)",
        "col_dry_rm": "تنظيف جاف (ر.س)",
        "col_status": "الحالة",
        "status_received": "تم الاستلام",
        "status_processing": "قيد المعالجة",
        "status_ready": "جاهز",
        "status_delivered": "تم التسليم",
        "status_cancelled": "ملغي",
        "status_paid": "مدفوع",
        "status_partial": "جزئي",
        "status_unpaid": "غير مدفوع",
        "status_pending": "معلق",
        "col_order": "رقم الطلب",
        "col_customer": "العميل",
        "col_amount": "المبلغ",
        "col_date": "التاريخ",
        "col_user": "المستخدم",
        "col_action": "الإجراء",
        "col_entity": "الكيان",
        "col_description": "الوصف",
        "col_datetime": "التاريخ والوقت",
        "refresh": "تحديث",
        "activity_log_sub": "نشاط النظام وسجل التدقيق",
        "expected_pickup": "الاستلام المتوقع",
        "payment_method": "الدفع",
        "total": "الإجمالي",
        "paid": "المدفوع",
        "create_order": "إنشاء طلب",
        "order_details": "تفاصيل الطلب",
        "select_customer": "اختر عميلاً",
        "select_company": "اختر شركة",
        "customer_individual": "عميل فردي",
        "or_company": "أو شركة/عقد",
        "on_delivery": "الدفع عند التسليم",
        "at_order": "الدفع عند الطلب",
        "deferred": "آجل/فاتورة",
        "discount_rm": "الخصم (ر.س)",
        "items": "العناصر",
        "qty": "الكمية",
        "invoice_number": "رقم الفاتورة",
        "issued_date": "تاريخ الإصدار",
        "print_invoice": "طباعة الفاتورة",
        "download_pdf": "تحميل PDF",
        "invoice_preview": "معاينة الفاتورة",
        "view_invoice": "عرض الفاتورة",
        "close": "إغلاق",
        "all": "الكل",
        "lang_en": "English",
        "lang_ar": "العربية",
        "sign_out": "تسجيل الخروج",
        "sign_out_confirm": "هل أنت متأكد من رغبتك في تسجيل الخروج؟",
        "upload": "رفع",
        "view": "عرض",
        "wash": "غسيل",
        "iron": "كي",
        "dry_clean": "تنظيف جاف",
        "invoice_ready_msg": "الفاتورة جاهزة للعرض والطباعة",
        "tab_password": "كلمة المرور",
        "tab_about": "حول البرنامج",
        "current_password": "كلمة المرور الحالية",
        "new_password": "كلمة المرور الجديدة",
        "confirm_password": "تأكيد كلمة المرور",
        "update_password": "تحديث كلمة المرور",
        "version": "الإصدار",
        "built_with": "تم البناء بواسطة",
        "database": "قاعدة البيانات",
        "db_location": "موقع قاعدة البيانات",
        "logged_in_as": "تم تسجيل الدخول باسم",
        "software_note": "تم تصميم هذا البرنامج لإدارة المغاسل الاحترافية.",
        "all_fields_required": "جميع الحقول مطلوبة",
        "passwords_mismatch": "كلمات المرور غير متطابقة",
        "password_too_short": "كلمة المرور قصيرة جداً (6 أحرف كحد أدنى)",
        "current_password_incorrect": "كلمة المرور الحالية غير صحيحة",
        "password_updated_success": "تم تحديث كلمة المرور بنجاح",
    }
}
def get_lang() -> str:
    """الحصول على اللغة الحالية"""
    return _current

def language() -> str:
    """الحصول على اللغة الحالية (اسم بديل)"""
    return _current

def tr(key: str, **kwargs) -> str:
    s = TRANSLATIONS.get(_current, {}).get(key, TRANSLATIONS['en'].get(key, key))
    if kwargs:
        try: return s.format(**kwargs)
        except: return s
    return s

def register_listener(cb):
    if cb not in _listeners: _listeners.append(cb)

def unregister_listener(cb):
    if cb in _listeners: _listeners.remove(cb)

def format_date(dt):
    if not dt: return ""
    return dt.strftime("%Y-%m-%d")

def status_label(status: str) -> str:
    return tr(f"status_{status}")
