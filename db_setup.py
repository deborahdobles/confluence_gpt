import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# PostgreSQL connection details
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def setup_database():
    """
    Configures the PostgreSQL database and creates the 'incidencias' table if it does not exist.
    Also preloads some test data for verification.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
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