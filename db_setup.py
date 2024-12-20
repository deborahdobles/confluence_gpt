import sqlite3

def setup_database():
    """
    Configures the SQLite database and creates the 'incidencias' table if it does not exist.
    Also preloads some test data for verification.
    """
    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        content TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert test data
    cursor.execute("""
    INSERT OR IGNORE INTO incidencias (title, content)
    VALUES
        ('Test Incident 1', 'This is a test incident related to core functionality.'),
        ('Core Issue Example', 'Another test case with the keyword core in the content.')
    """)

    conn.commit()
    conn.close()
    print("Database set up with test data.")

if __name__ == "__main__":
    setup_database()