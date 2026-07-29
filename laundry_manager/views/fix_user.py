import sqlite3, bcrypt, os

db = os.path.join(os.environ['APPDATA'], 'InternationalLaundries', 'laundry.db')
conn = sqlite3.connect(db)

# ── اعرض كل المستخدمين الحاليين ──
print("=" * 50)
print("Current users:")
for r in conn.execute("SELECT id, username, full_name, role, is_active FROM users").fetchall():
    print(f"  ID={r[0]}  user={r[1]}  name={r[2]}  role={r[3]}  active={r[4]}")
print("=" * 50)

# ── اختر: أي مستخدم تريد تصليحه ──
username = input("\nEnter username to fix (e.g. admin): ").strip()
new_role = input("New role (admin / mana"
                 "ger / staff): ").strip()
new_pass = input("New password (press Enter to keep current): ").strip()

# Update role
conn.execute("UPDATE users SET role=?, is_active=1 WHERE username=?", (new_role, username))

# Update password if provided
if new_pass:
    pw_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
    conn.execute("UPDATE users SET password_hash=? WHERE username=?", (pw_hash, username))

conn.commit()
print(f"\n✅ Done! '{username}' is now role='{new_role}'")
conn.close()