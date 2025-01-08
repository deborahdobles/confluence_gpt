import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# PostgreSQL connection details
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGDATABASE = os.getenv("PGDATABASE", "railway")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "PKUuNurNJXrquDGWfIyBEFhwLURkPBDw")


def setup_database():
    """
    Configures the PostgreSQL database and creates the 'incidencias' table if it does not exist.
    Also preloads some test data for verification.
    """
    conn = None
    try:
        print(f"Connecting to database '{PGDATABASE}' at {PGHOST}:{PGPORT} as user '{PGUSER}'")
        conn = psycopg2.connect(
            host=PGHOST,
            port=PGPORT,
            database=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
        )
        cursor = conn.cursor()

        # Create table if not exists
        print("Creating table 'incidencias' if it does not exist...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidencias (
            id SERIAL PRIMARY KEY,
            title TEXT UNIQUE,
            content TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("Table 'incidencias' is ready.")

        # Insert test data
        print("Inserting test data into 'incidencias' table...")
        cursor.execute("""
        INSERT INTO incidencias (title, content)
        VALUES
            ('Test Incident 1', 'This is a test incident related to core functionality.'),
            ('Core Issue Example', 'Another test case with the keyword core in the content.')
        ON CONFLICT (title) DO NOTHING
        """)
        print("Test data inserted successfully.")

        conn.commit()
        print("Database setup completed successfully.")
    except psycopg2.OperationalError as op_err:
        print(f"Operational error while connecting to the database: {op_err}")
    except psycopg2.Error as db_err:
        print(f"Database error occurred: {db_err}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    setup_database()