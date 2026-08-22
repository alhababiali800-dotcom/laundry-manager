# 🧺 International Laundries — Desktop Management System

A full-featured laundry management system built with **Python + PyQt6 + SQLite**.  
Works on any Windows/Mac/Linux computer — **no server, no MySQL needed**.

---

## ⚡ Quick Start (3 steps)

```bash
# 1. Install dependencies
pip install PyQt6 bcrypt reportlab Pillow

# 2. Run the app
python main.py
```

**First login:**

Use username `admin` with password `admin123` only for the first sign-in. The
application requires you to set a new password before granting access.

---

## 📁 Project Structure

```
laundry_manager/
├── main.py                  ← Entry point
├── requirements.txt
├── build_exe.spec           ← PyInstaller config (build .exe)
│
├── database/
│   ├── connection.py        ← SQLite singleton
│   └── schema.py            ← Table creation + seed data
│
├── models/
│   └── all_models.py        ← All CRUD operations
│
├── views/
│   ├── styles.py            ← Global QSS stylesheet
│   ├── login_window.py
│   ├── main_window.py       ← Sidebar + navigation
│   ├── base_view.py         ← Reusable widgets
│   ├── dashboard_view.py
│   ├── customers_view.py
│   ├── companies_view.py    ← Companies + Contracts
│   ├── orders_view.py       ← New order + status + payment
│   ├── invoices_view.py
│   ├── catalog_view.py
│   ├── reports_view.py
│   ├── users_view.py
│   ├── activity_view.py
│   └── settings_view.py
│
└── utils/
    └── pdf_generator.py     ← PDF invoice (reportlab)
```

---

## ✅ Features

| Module        | Features |
|---------------|----------|
| Dashboard     | Stats cards, recent orders |
| Orders        | Create, view, status update, payment recording |
| Customers     | Full CRUD, search, company linking |
| Companies     | Full CRUD |
| Contracts     | Company contracts with discount & limits |
| Invoices      | Auto-created per order, PDF printing |
| Catalog       | Item types with wash/iron/dry-clean prices |
| Reports       | Revenue by month, top customers, popular items |
| Users         | Role-based access (admin/manager/staff) |
| Activity Log  | Tracks every action |
| Settings      | Change password |

---

## 🔨 Build .exe (Windows)

```bash
pip install pyinstaller
pyinstaller build_exe.spec
```

Output: `dist/InternationalLaundries/InternationalLaundries.exe`

---

## 🗄️ Database

SQLite file is stored at:
- **Windows:** `%APPDATA%\InternationalLaundries\laundry.db`
- **Linux/Mac:** `~/.international_laundries/laundry.db`

Back this file up regularly — it contains all your data. Keep this backup in a
secure location because it includes customer and order information.

---

## 📦 Requirements

```
PyQt6>=6.5.0
bcrypt>=4.0.0
reportlab>=4.0.0   (optional — for PDF invoices)
Pillow>=10.0.0     (optional)
```
