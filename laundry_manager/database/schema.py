import bcrypt

from database.connection import Database

def initialize_database():
    db = Database.get()
    cursor = db.cursor()

    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'staff',
        email TEXT,
        phone TEXT,
        is_active INTEGER DEFAULT 1,
        must_change_password INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Item Types (catalog)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        wash_price REAL DEFAULT 0,
        iron_price REAL DEFAULT 0,
        dry_clean_price REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )""")

    # Customers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        customer_type TEXT DEFAULT 'individual',
        company_id INTEGER REFERENCES companies(id),
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Companies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Contracts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER REFERENCES companies(id),
        title TEXT,
        start_date DATE,
        end_date DATE,
        discount_percent REAL DEFAULT 0,
        monthly_limit REAL DEFAULT 0,
        payment_terms TEXT DEFAULT 'monthly',
        status TEXT DEFAULT 'active',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER REFERENCES customers(id),
        company_id INTEGER REFERENCES companies(id),
        status TEXT DEFAULT 'received',
        payment_status TEXT DEFAULT 'pending',
        payment_method TEXT DEFAULT 'on_delivery',
        total_amount REAL DEFAULT 0,
        paid_amount REAL DEFAULT 0,
        discount REAL DEFAULT 0,
        notes TEXT,
        received_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        ready_date DATETIME,
        delivered_date DATETIME,
        created_by INTEGER REFERENCES users(id),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Order Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
        item_type_id INTEGER REFERENCES item_types(id),
        item_name TEXT NOT NULL,
        service_type TEXT DEFAULT 'wash',
        quantity INTEGER DEFAULT 1,
        unit_price REAL DEFAULT 0,
        total_price REAL DEFAULT 0
    )""")

    # Invoices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        customer_id INTEGER REFERENCES customers(id),
        company_id INTEGER REFERENCES companies(id),
        order_id INTEGER REFERENCES orders(id),
        total_amount REAL DEFAULT 0,
        paid_amount REAL DEFAULT 0,
        status TEXT DEFAULT 'unpaid',
        due_date DATE,
        issued_date DATE DEFAULT CURRENT_DATE,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Activity Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        username TEXT,
        action TEXT NOT NULL,
        entity_type TEXT,
        entity_id INTEGER,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    _run_migrations(cursor)
    _create_indexes(cursor)
    db.commit()

    # Seed default admin if no users exist
    count = Database.fetchone("SELECT COUNT(*) as c FROM users")
    if count and count['c'] == 0:
        _seed_default_data()

def _create_indexes(cursor):
    """Create indexes for frequently queried columns to improve performance."""
    indexes = [
        # Users
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
        
        # Customers
        "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)",
        "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)",
        "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
        "CREATE INDEX IF NOT EXISTS idx_customers_company_id ON customers(company_id)",
        
        # Companies
        "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)",
        
        # Orders
        "CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_company_id ON orders(company_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
        "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_orders_created_by ON orders(created_by)",
        
        # Order Items
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_item_type_id ON order_items(item_type_id)",
        
        # Invoices
        "CREATE INDEX IF NOT EXISTS idx_invoices_invoice_number ON invoices(invoice_number)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_order_id ON invoices(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_customer_id ON invoices(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_invoices_company_id ON invoices(company_id)",
        
        # Activity Log
        "CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at)",
        
        # Item Types
        "CREATE INDEX IF NOT EXISTS idx_item_types_name ON item_types(name)",
        "CREATE INDEX IF NOT EXISTS idx_item_types_is_active ON item_types(is_active)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except Exception:
            pass  # Index may already exist

def _run_migrations(cursor):
    """Add columns for databases created before newer releases."""
    cursor.execute("PRAGMA table_info(orders)")
    order_cols = {row[1] for row in cursor.fetchall()}
    for column, definition in [('subtotal_amount', 'REAL DEFAULT 0'), ('tax_rate', 'REAL DEFAULT 0'), ('tax_amount', 'REAL DEFAULT 0')]:
        if column not in order_cols:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {column} {definition}")
    if 'expected_delivery' not in order_cols:
        cursor.execute("ALTER TABLE orders ADD COLUMN expected_delivery DATETIME")
    
    cursor.execute("PRAGMA table_info(invoices)")
    invoice_cols = {row[1] for row in cursor.fetchall()}
    for column, definition in [('subtotal_amount', 'REAL DEFAULT 0'), ('tax_rate', 'REAL DEFAULT 0'), ('tax_amount', 'REAL DEFAULT 0')]:
        if column not in invoice_cols:
            cursor.execute(f"ALTER TABLE invoices ADD COLUMN {column} {definition}")

    cursor.execute("PRAGMA table_info(item_types)")
    item_cols = {row[1] for row in cursor.fetchall()}
    if 'image_path' not in item_cols:
        cursor.execute("ALTER TABLE item_types ADD COLUMN image_path TEXT")

    cursor.execute("PRAGMA table_info(users)")
    user_cols = {row[1] for row in cursor.fetchall()}
    if 'must_change_password' not in user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER DEFAULT 0")

    # Existing installations that still use the documented default password
    # must change it on their next login.
    admin = cursor.execute(
        "SELECT id, password_hash FROM users WHERE username='admin'"
    ).fetchone()
    if admin and bcrypt.checkpw(b'admin123', admin[1].encode()):
        cursor.execute("UPDATE users SET must_change_password=1 WHERE id=?", (admin[0],))


def _seed_default_data():
    # Admin user
    pw = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
    Database.execute(
        "INSERT INTO users (username, password_hash, full_name, role, must_change_password) VALUES (?,?,?,?,?)",
        ('admin', pw, 'System Admin', 'admin', 1)
    )

    # Sample item types
    items = [
        ('Shirt', 2.5, 1.5, 5.0),
        ('Trousers', 3.0, 2.0, 6.0),
        ('Suit Jacket', 5.0, 3.0, 10.0),
        ('Dress', 4.0, 2.5, 8.0),
        ('Abaya', 5.0, 3.0, 9.0),
        ('Bed Sheet', 4.0, 2.0, 0.0),
        ('Blanket', 6.0, 3.0, 0.0),
        ('Towel', 1.5, 1.0, 0.0),
        ('Jacket / Coat', 6.0, 3.5, 12.0),
        ('T-Shirt', 2.0, 1.0, 4.0),
    ]
    for name, w, i, d in items:
        Database.execute(
            "INSERT INTO item_types (name, wash_price, iron_price, dry_clean_price) VALUES (?,?,?,?)",
            (name, w, i, d)
        )

    # Sample company
    Database.execute(
        "INSERT INTO companies (name, contact_person, phone, email) VALUES (?,?,?,?)",
        ('Green Haven Hotel', 'Ali Hassan', '+60123456789', 'ali@greenhaven.com')
    )

    # Sample customer
    Database.execute(
        "INSERT INTO customers (name, phone, email) VALUES (?,?,?)",
        ('Ahmed Abdullah', '+60187654321', 'ahmed@email.com')
    )
