# check_and_fix_schema.py
import sqlite3, sys, os

DB = "library.db"

def pragma(conn, q):
    cur = conn.cursor()
    cur.execute(q)
    return cur.fetchall()

def ensure_column(conn, table, column_def, column_name):
    cols = [r[1] for r in pragma(conn, f"PRAGMA table_info({table});")]
    if column_name not in cols:
        print(f"Adding column {column_name} to {table}")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        conn.commit()
    else:
        print(f"{table}.{column_name} exists")

def transactions_has_id_pk(conn):
    try:
        info = pragma(conn, "PRAGMA table_info(transactions);")
        for r in info:
            # r[1] = name, r[5] = pk flag
            if r[1] == "id" and r[5] == 1:
                return True
    except Exception:
        return False
    return False

def migrate_transactions(conn):
    print("Migrating transactions table to ensure id INTEGER PRIMARY KEY AUTOINCREMENT...")
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transactions_new (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      transaction_id TEXT,
      student_id INTEGER,
      student_registration_no TEXT,
      book_id INTEGER,
      borrow_date TEXT,
      due_date TEXT,
      return_date TEXT,
      status TEXT,
      fine_amount REAL DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # copy columns that exist from old table
    try:
        old_cols = [r[1] for r in pragma(conn, "PRAGMA table_info(transactions);")]
        common = [c for c in old_cols if c in ('transaction_id','student_id','student_registration_no','book_id','borrow_date','due_date','return_date','status','fine_amount','created_at')]
        if common:
            cols_sql = ",".join(common)
            conn.execute(f"INSERT INTO transactions_new ({cols_sql}) SELECT {cols_sql} FROM transactions")
            print("Copied data to transactions_new")
    except Exception as e:
        print("No existing transactions data to copy or copy failed:", e)
    # rename/swap
    try:
        conn.execute("ALTER TABLE transactions RENAME TO transactions_old")
    except Exception:
        pass
    conn.execute("ALTER TABLE transactions_new RENAME TO transactions")
    conn.commit()
    print("Migration done. Old table (if any) is transactions_old.")

def main():
    if not os.path.exists(DB):
        print(f"Database file '{DB}' not found. Exiting.")
        sys.exit(1)
    conn = sqlite3.connect(DB)
    try:
        ensure_column(conn, "students", "borrowed_books INTEGER DEFAULT 0", "borrowed_books")
        ensure_column(conn, "students", "fine_amount REAL DEFAULT 0", "fine_amount")
        ensure_column(conn, "books", "available INTEGER DEFAULT 0", "available")
    except Exception as e:
        print("Error ensuring columns:", e)
    # ensure transactions table and id pk
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        if not cur.fetchone():
            print("No transactions table found — creating new one with id PK.")
            migrate_transactions(conn)
        else:
            if not transactions_has_id_pk(conn):
                migrate_transactions(conn)
            else:
                print("transactions table already has id INTEGER PRIMARY KEY.")
    except Exception as e:
        print("Error inspecting/migrating transactions:", e)
    conn.close()
    print("Schema check/auto-fix complete.")

if __name__ == "__main__":
    main()
