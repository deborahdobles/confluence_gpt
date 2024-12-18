from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

DB_FILE = "incidencias.db"


def search_incidents_in_db(keyword):
    """
    Busca incidencias relacionadas con la palabra clave en la base de datos.
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
    Envia los incidentes encontrados a GPT para generar un resumen.
    """
    context = f"La consulta se relaciona con la palabra clave: '{keyword}'. Por favor, revisa las siguientes incidencias y confirma cuáles están relacionadas con '{keyword}':\n\n"
    for i, (title, content) in enumerate(incidents[:10], start=1):
        context += f"Incidencia {i}:\nTítulo: {title}\nContenido: {content[:500]}...\n\n"

    print(f"GPT context:\n{context}")  # Debug print

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
        gpt_output = response['choices'][0]['message']['content']
        print(f"GPT response:\n{gpt_output}")  # Debug print
        return gpt_output

    except Exception as e:
        print(f"Error with GPT request: {e}")
        return "Error al procesar la solicitud con GPT."


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
    print(f"Incidents found: {incidents}")

    # Process incidents with GPT
    gpt_response = ask_gpt(incidents, keyword)

    # Send response back
    print(f"Response sent to client: {gpt_response}")
    return jsonify({"response": gpt_response})


if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=8000)