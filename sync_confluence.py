import sqlite3
from main import fetch_all_reports


def update_database_from_confluence(parent_id):
    """
    Synchronize incidents from Confluence with the SQLite database.
    """
    # Fetch all reports from Confluence
    reports = fetch_all_reports(parent_id)

    # Connect to the SQLite database
    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    # Iterate through the fetched reports and update the database
    for report in reports:
        cursor.execute("""
        INSERT INTO incidencias (title, content)
        VALUES (?, ?)
        ON CONFLICT(title) DO UPDATE SET
            content = excluded.content,
            last_updated = CURRENT_TIMESTAMP
        """, (report['title'], report['content']))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"{len(reports)} incidencias sincronizadas con la base de datos.")


if __name__ == "__main__":
    # Replace this with your actual Confluence parent page ID
    PARENT_PAGE_ID = "9251782674"
    update_database_from_confluence(PARENT_PAGE_ID)
