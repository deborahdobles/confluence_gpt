import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# PostgreSQL connection details
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")


def setup_database():
    """
    Configures the PostgreSQL database and creates the 'incidencias' table if it does not exist.
    Also preloads some test data for verification.
    """
    try:
        conn = psycopg2.connect(
            host=PGHOST,
            port=PGPORT,
            database=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
        )
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidencias (
            id SERIAL PRIMARY KEY,
            title TEXT UNIQUE,
            content TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Insert test data
        cursor.execute("""
        INSERT INTO incidencias (title, content)
        VALUES
            ('Test Incident 1', 'This is a test incident related to core functionality.'),
            ('Core Issue Example', 'Another test case with the keyword core in the content.')
        ON CONFLICT (title) DO NOTHING
        """)

        conn.commit()
        print("Database set up with test data.")
    except Exception as e:
        print(f"Database setup failed: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    setup_database()