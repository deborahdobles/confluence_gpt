import sqlite3
import requests

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


def fetch_data_and_populate():
    """
    Simula la obtención de datos (puedes reemplazar esto con una solicitud API)
    y los inserta en la base de datos.
    """
    # Simulated data - Replace this with your actual data-fetching logic (e.g., API calls)
    data = [
        {"title": "INC-001", "content": "Contenido de ejemplo para INC-001"},
        {"title": "INC-002", "content": "Contenido de ejemplo para INC-002"},
        {"title": "INC-003", "content": "Contenido de ejemplo para INC-003"},
    ]

    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    for item in data:
        cursor.execute("""
        INSERT OR REPLACE INTO incidencias (title, content)
        VALUES (?, ?)
        """, (item["title"], item["content"]))

    conn.commit()
    conn.close()
    print(f"Se han insertado {len(data)} registros en la base de datos.")


if __name__ == "__main__":
    setup_database()
    fetch_data_and_populate()