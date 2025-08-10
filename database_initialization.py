import sqlite3

def init_db():
    conn = sqlite3.connect('data/expenses.db')
    c = conn.cursor()

    # Create tables according to data.txt schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS payment_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date DATE NOT NULL,
            amount REAL NOT NULL,
            name TEXT,
            category_id INTEGER,
            payment_type_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (payment_type_id) REFERENCES payment_types(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
