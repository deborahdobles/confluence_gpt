from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import openai
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# PostgreSQL connection details
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5432")
PGDATABASE = os.getenv("PGDATABASE", "railway")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "PKUuNurNJXrquDGWfIyBEFhwLURkPBDw")

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            host=PGHOST,
            port=PGPORT,
            database=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise


def search_incidents_in_db(keyword):
    """
    Searches for incidents related to the given keyword in the PostgreSQL database.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query database
        query = """
        SELECT title, content FROM incidencias
        WHERE title ILIKE %s OR content ILIKE %s
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))

        results = cursor.fetchall()
        print(f"Results from DB for keyword '{keyword}': {results}")
        return results
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint to search incidents by keyword.
    """
    data = request.json
    keyword = data.get('keyword', '')

    if not keyword:
        return jsonify({"error": "Debe proporcionar una palabra clave."}), 400

    # Search incidents in the database
    incidents = search_incidents_in_db(keyword)
    print(f"Incidents found: {incidents}")  # Debugging

    # Check if incidents were found
    if not incidents:
        response_message = f"No se encontraron incidencias relacionadas con la palabra clave '{keyword}'."
        print(f"Response sent to client: {response_message}")
        return jsonify({"response": response_message})

    # Construct a response
    response_message = {
        "incidencias": [
            {"titulo": incident["title"], "contenido": incident["content"]} for incident in incidents
        ]
    }

    # Send response back
    print(f"Response sent to client: {response_message}")
    return jsonify(response_message)


if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=8000)