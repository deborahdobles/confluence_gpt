import sqlite3


def setup_database():
    """
    Configura la base de datos SQLite y crea la tabla incidencias si no existe.
    """
    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE,
        content TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    print("Base de datos configurada correctamente.")


if __name__ == "__main__":
    setup_database()
