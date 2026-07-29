from database.connection import Database
from datetime import datetime
import bcrypt


# ─────────────────────────── USER ────────────────────────────
class UserModel:
    @staticmethod
    def get_all():
        return Database.fetchall("SELECT * FROM users ORDER BY full_name")

    @staticmethod
    def get_by_id(uid):
        return Database.fetchone("SELECT * FROM users WHERE id=?", (uid,))

    @staticmethod
    def get_by_username(username):
        return Database.fetchone("SELECT * FROM users WHERE username=?", (username,))

    @staticmethod
    def verify_password(username, password):
        user = UserModel.get_by_username(username)
        if not user or not user['is_active']:
            return None
        if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
            return user
        return None

    @staticmethod
    def create(username, password, full_name, role='staff', email='', phone=''):
        pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        return Database.lastrowid(
            "INSERT INTO users (username,password_hash,full_name,role,email,phone) VALUES (?,?,?,?,?,?)",
            (username, pw, full_name, role, email, phone)
        )

    @staticmethod
    def update(uid, full_name, role, email, phone, is_active):
        Database.execute(
            "UPDATE users SET full_name=?,role=?,email=?,phone=?,is_active=? WHERE id=?",
            (full_name, role, email, phone, is_active, uid)
        )

    @staticmethod
    def change_password(uid, new_password):
        pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        Database.execute("UPDATE users SET password_hash=? WHERE id=?", (pw, uid))

    @staticmethod
    def delete(uid):
        Database.execute("DELETE FROM users WHERE id=?", (uid,))


# ─────────────────────────── CUSTOMER ────────────────────────
class CustomerModel:
    @staticmethod
    def get_all():
        return Database.fetchall("""
            SELECT c.*, co.name as company_name
            FROM customers c
            LEFT JOIN companies co ON c.company_id = co.id
            ORDER BY c.name
        """)

    @staticmethod
    def get_by_id(cid):
        return Database.fetchone("SELECT * FROM customers WHERE id=?", (cid,))

    @staticmethod
    def search(q):
        q = f"%{q}%"
        return Database.fetchall(
            "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? ORDER BY name",
            (q, q, q)
        )

    @staticmethod
    def create(name, phone, email, address, customer_type, company_id, notes):
        return Database.lastrowid(
            "INSERT INTO customers (name,phone,email,address,customer_type,company_id,notes) VALUES (?,?,?,?,?,?,?)",
            (name, phone, email, address, customer_type, company_id or None, notes)
        )

    @staticmethod
    def update(cid, name, phone, email, address, customer_type, company_id, notes):
        Database.execute(
            "UPDATE customers SET name=?,phone=?,email=?,address=?,customer_type=?,company_id=?,notes=? WHERE id=?",
            (name, phone, email, address, customer_type, company_id or None, notes, cid)
        )

    @staticmethod
    def delete(cid):
        Database.execute("DELETE FROM customers WHERE id=?", (cid,))

    @staticmethod
    def count():
        r = Database.fetchone("SELECT COUNT(*) as c FROM customers")
        return r['c'] if r else 0


# ─────────────────────────── COMPANY ─────────────────────────
class CompanyModel:
    @staticmethod
    def get_all():
        return Database.fetchall("SELECT * FROM companies ORDER BY name")

    @staticmethod
    def get_by_id(cid):
        return Database.fetchone("SELECT * FROM companies WHERE id=?", (cid,))

    @staticmethod
    def search(q):
        q = f"%{q}%"
        return Database.fetchall(
            "SELECT * FROM companies WHERE name LIKE ? OR contact_person LIKE ? ORDER BY name",
            (q, q)
        )

    @staticmethod
    def create(name, contact_person, phone, email, address, notes):
        return Database.lastrowid(
            "INSERT INTO companies (name,contact_person,phone,email,address,notes) VALUES (?,?,?,?,?,?)",
            (name, contact_person, phone, email, address, notes)
        )

    @staticmethod
    def update(cid, name, contact_person, phone, email, address, notes):
        Database.execute(
            "UPDATE companies SET name=?,contact_person=?,phone=?,email=?,address=?,notes=? WHERE id=?",
            (name, contact_person, phone, email, address, notes, cid)
        )

    @staticmethod
    def delete(cid):
        Database.execute("DELETE FROM companies WHERE id=?", (cid,))

    @staticmethod
    def count():
        r = Database.fetchone("SELECT COUNT(*) as c FROM companies")
        return r['c'] if r else 0


# ─────────────────────────── ITEM TYPE ───────────────────────
class ItemTypeModel:
    @staticmethod
    def get_all(active_only=True):
        if active_only:
            return Database.fetchall("SELECT * FROM item_types WHERE is_active=1 ORDER BY name")
        return Database.fetchall("SELECT * FROM item_types ORDER BY name")

    @staticmethod
    def get_by_id(iid):
        return Database.fetchone("SELECT * FROM item_types WHERE id=?", (iid,))

    @staticmethod
    def create(name, wash_price, iron_price, dry_clean_price, image_path=None):
        return Database.lastrowid(
            "INSERT INTO item_types (name,wash_price,iron_price,dry_clean_price,image_path) VALUES (?,?,?,?,?)",
            (name, wash_price, iron_price, dry_clean_price, image_path)
        )

    @staticmethod
    def update(iid, name, wash_price, iron_price, dry_clean_price, is_active, image_path=None):
        Database.execute(
            "UPDATE item_types SET name=?,wash_price=?,iron_price=?,dry_clean_price=?,is_active=?,image_path=? WHERE id=?",
            (name, wash_price, iron_price, dry_clean_price, is_active, image_path, iid)
        )

    @staticmethod
    def delete(iid):
        Database.execute("DELETE FROM item_types WHERE id=?", (iid,))


# ─────────────────────────── ORDER ───────────────────────────
def _gen_order_number():
    now = datetime.now()
    prefix = now.strftime("ORD-%Y%m%d-")
    r = Database.fetchone(
        "SELECT COUNT(*) as c FROM orders WHERE order_number LIKE ?",
        (prefix + '%',)
    )
    seq = (r['c'] if r else 0) + 1
    return f"{prefix}{seq:04d}"


class OrderModel:
    @staticmethod
    def get_all(status_filter=None, search=None):
        sql = """
            SELECT o.*,
                   c.name as customer_name,
                   co.name as company_name,
                   u.full_name as created_by_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN companies co ON o.company_id = co.id
            LEFT JOIN users u ON o.created_by = u.id
        """
        params = []
        where = []
        if status_filter and status_filter != 'all':
            where.append("o.status=?")
            params.append(status_filter)
        if search:
            where.append("(o.order_number LIKE ? OR c.name LIKE ? OR co.name LIKE ?)")
            s = f"%{search}%"
            params += [s, s, s]
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY o.created_at DESC"
        return Database.fetchall(sql, params)

    @staticmethod
    def get_by_id(oid):
        return Database.fetchone("""
            SELECT o.*, c.name as customer_name, co.name as company_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN companies co ON o.company_id = co.id
            WHERE o.id=?
        """, (oid,))

    @staticmethod
    def get_items(oid):
        return Database.fetchall("SELECT * FROM order_items WHERE order_id=?", (oid,))

    @staticmethod
    def create(customer_id, company_id, items, payment_method, discount, notes, created_by,
               expected_delivery=None):
        order_number = _gen_order_number()
        total = sum(it['total_price'] for it in items)
        total_after = total - discount
        oid = Database.lastrowid(
            """INSERT INTO orders
               (order_number,customer_id,company_id,total_amount,discount,payment_method,notes,
                created_by,expected_delivery)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (order_number, customer_id or None, company_id or None,
             total_after, discount, payment_method, notes, created_by, expected_delivery)
        )
        for it in items:
            Database.execute(
                """INSERT INTO order_items (order_id,item_type_id,item_name,service_type,quantity,unit_price,total_price)
                   VALUES (?,?,?,?,?,?,?)""",
                (oid, it.get('item_type_id'), it['item_name'], it['service_type'],
                 it['quantity'], it['unit_price'], it['total_price'])
            )
        # Auto create invoice
        inv_num = f"INV-{order_number[4:]}"
        Database.execute(
            """INSERT INTO invoices (invoice_number,customer_id,company_id,order_id,total_amount,status)
               VALUES (?,?,?,?,?,?)""",
            (inv_num, customer_id or None, company_id or None, oid, total_after, 'unpaid')
        )
        return oid, order_number

    @staticmethod
    def update_status(oid, status):
        now = datetime.now().isoformat()
        if status == 'ready':
            Database.execute("UPDATE orders SET status=?, ready_date=? WHERE id=?", (status, now, oid))
        elif status == 'delivered':
            Database.execute("UPDATE orders SET status=?, delivered_date=? WHERE id=?", (status, now, oid))
        else:
            Database.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))

    @staticmethod
    def record_payment(oid, amount):
        order = OrderModel.get_by_id(oid)
        if not order:
            return
        new_paid = order['paid_amount'] + amount
        status = 'paid' if new_paid >= order['total_amount'] else 'partial'
        Database.execute(
            "UPDATE orders SET paid_amount=?, payment_status=? WHERE id=?",
            (new_paid, status, oid)
        )
        Database.execute(
            "UPDATE invoices SET paid_amount=?, status=? WHERE order_id=?",
            (new_paid, status, oid)
        )

    @staticmethod
    def count_by_status():
        rows = Database.fetchall("SELECT status, COUNT(*) as c FROM orders GROUP BY status")
        return {r['status']: r['c'] for r in rows}

    @staticmethod
    def count_today():
        r = Database.fetchone(
            "SELECT COUNT(*) as c FROM orders WHERE DATE(created_at)=DATE('now')"
        )
        return r['c'] if r else 0

    @staticmethod
    def revenue_today():
        r = Database.fetchone(
            "SELECT COALESCE(SUM(paid_amount),0) as total FROM orders WHERE DATE(created_at)=DATE('now')"
        )
        return r['total'] if r else 0

    @staticmethod
    def revenue_month():
        r = Database.fetchone(
            "SELECT COALESCE(SUM(paid_amount),0) as total FROM orders WHERE strftime('%Y-%m',created_at)=strftime('%Y-%m','now')"
        )
        return r['total'] if r else 0


# ─────────────────────────── INVOICE ─────────────────────────
class InvoiceModel:
    @staticmethod
    def get_all(status_filter=None):
        sql = """
            SELECT i.*, c.name as customer_name, co.name as company_name, o.order_number
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN companies co ON i.company_id = co.id
            LEFT JOIN orders o ON i.order_id = o.id
        """
        if status_filter and status_filter != 'all':
            sql += f" WHERE i.status='{status_filter}'"
        sql += " ORDER BY i.created_at DESC"
        return Database.fetchall(sql)

    @staticmethod
    def get_by_id(iid):
        return Database.fetchone("""
            SELECT i.*, c.name as customer_name, co.name as company_name, o.order_number
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id=c.id
            LEFT JOIN companies co ON i.company_id=co.id
            LEFT JOIN orders o ON i.order_id=o.id
            WHERE i.id=?
        """, (iid,))

    @staticmethod
    def count_unpaid():
        r = Database.fetchone("SELECT COUNT(*) as c FROM invoices WHERE status='unpaid'")
        return r['c'] if r else 0


# ─────────────────────────── CONTRACT ────────────────────────
class ContractModel:
    @staticmethod
    def get_all():
        return Database.fetchall("""
            SELECT ct.*, co.name as company_name
            FROM contracts ct
            LEFT JOIN companies co ON ct.company_id = co.id
            ORDER BY ct.created_at DESC
        """)

    @staticmethod
    def get_by_id(cid):
        return Database.fetchone("""
            SELECT ct.*, co.name as company_name
            FROM contracts ct
            LEFT JOIN companies co ON ct.company_id=co.id
            WHERE ct.id=?
        """, (cid,))

    @staticmethod
    def create(company_id, title, start_date, end_date, discount_percent, monthly_limit, payment_terms, notes):
        return Database.lastrowid(
            """INSERT INTO contracts (company_id,title,start_date,end_date,discount_percent,monthly_limit,payment_terms,notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (company_id, title, start_date, end_date, discount_percent, monthly_limit, payment_terms, notes)
        )

    @staticmethod
    def update(cid, company_id, title, start_date, end_date, discount_percent, monthly_limit, payment_terms, status, notes):
        Database.execute(
            """UPDATE contracts SET company_id=?,title=?,start_date=?,end_date=?,discount_percent=?,
               monthly_limit=?,payment_terms=?,status=?,notes=? WHERE id=?""",
            (company_id, title, start_date, end_date, discount_percent, monthly_limit, payment_terms, status, notes, cid)
        )

    @staticmethod
    def delete(cid):
        Database.execute("DELETE FROM contracts WHERE id=?", (cid,))


# ─────────────────────────── ACTIVITY LOG ────────────────────
class ActivityModel:
    @staticmethod
    def log(user_id, username, action, entity_type='', entity_id=None, description=''):
        Database.execute(
            "INSERT INTO activity_log (user_id,username,action,entity_type,entity_id,description) VALUES (?,?,?,?,?,?)",
            (user_id, username, action, entity_type, entity_id, description)
        )

    @staticmethod
    def get_all(limit=200):
        return Database.fetchall(
            "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT ?", (limit,)
        )
