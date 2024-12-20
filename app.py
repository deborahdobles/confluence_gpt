from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import openai


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

DB_FILE = "incidencias.db"

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def search_incidents_in_db(keyword):
    """
    Searches for incidents related to the given keyword in the database.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Query database
        cursor.execute("""
        SELECT title, content FROM incidencias
        WHERE title LIKE ? OR content LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))

        results = cursor.fetchall()
        print(f"Using database file: {os.path.abspath(DB_FILE)}")
        print(f"Results from DB for keyword '{keyword}': {results}")

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        results = []

    except Exception as e:
        print(f"Unexpected error: {e}")
        results = []

    finally:
        if conn:
            conn.close()

    # Clean HTML content
    def clean_html(raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text()

    cleaned_results = [(title, clean_html(content)) for title, content in results]
    print(f"Cleaned results: {cleaned_results}")

    return cleaned_results


def ask_gpt(incidents, keyword):
    """
    Sends the found incidents to GPT for generating a summary.
    """
    context = f"Consulta: '{keyword}'\n\nIncidencias encontradas:\n\n"
    for i, (title, content) in enumerate(incidents[:10], start=1):  # Limit to 10 incidents for brevity
        context += f"Incidencia {i}:\nTítulo: {title}\nContenido: {content[:500]}...\n\n"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente técnico que responde sobre incidencias."},
                {"role": "user", "content": context}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return f"Error while processing the GPT request: {e}"


@app.route('/query', methods=['POST'])
def query():
    """
    Endpoint para buscar incidencias por palabra clave.
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

    # If results are found, construct a response
    response_message = {
        "incidencias": [
            {"titulo": title, "contenido": content} for title, content in incidents
        ]
    }

    # Send response back
    print(f"Response sent to client: {response_message}")
    return jsonify(response_message)


if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=8000)