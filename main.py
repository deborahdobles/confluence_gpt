import os
import requests
import base64
import sqlite3
import openai
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
EMAIL = os.getenv("CONFLUENCE_EMAIL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

auth_string = f"{EMAIL}:{API_TOKEN}"
auth_header = base64.b64encode(auth_string.encode()).decode()


def fetch_page_content(page_id):
    """
    Fetch the full content of a specific page using the Confluence REST API.
    """
    url = f"{BASE_URL}/content/{page_id}?expand=body.storage"
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("body", {}).get("storage", {}).get("value", "No content available")
    else:
        print(f"Failed to fetch page content. Status code: {response.status_code}")
        return "Failed to fetch content"


def fetch_child_pages(parent_id):
    """
    Fetch all child pages of a specific parent page with pagination.
    """
    url = f"{BASE_URL}/content/{parent_id}/child/page"
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }

    all_pages = []
    start = 0
    limit = 500

    while True:
        params = {"start": start, "limit": limit}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            all_pages.extend(data.get("results", []))

            if len(data.get("results", [])) < limit:
                break
            start += limit
        else:
            print(f"Failed to fetch child pages. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            break

    return all_pages


def fetch_all_reports(parent_id):
    """
    Recursively fetch all `INC-XXXX` or `RIC-XXXX` reports, including their titles and detailed content.
    """
    reports = []
    children = fetch_child_pages(parent_id)

    for child in children:
        if child['title'].startswith("INC-") or child['title'].startswith("RIC-"):
            content = fetch_page_content(child['id'])
            report = {
                "title": child['title'],
                "content": content
            }
            reports.append(report)
            print(f"Fetched report: {child['title']}")

        sub_reports = fetch_all_reports(child['id'])
        reports.extend(sub_reports)

    return reports


def update_database_from_confluence(parent_id):
    """
    Synchronize incidents from Confluence with the SQLite database.
    """
    reports = fetch_all_reports(parent_id)

    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    # Verificar si la tabla existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidencias (
        title TEXT PRIMARY KEY,
        content TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    for report in reports:
        cursor.execute("""
        INSERT INTO incidencias (title, content)
        VALUES (?, ?)
        ON CONFLICT(title) DO UPDATE SET content = excluded.content, last_updated = CURRENT_TIMESTAMP
        """, (report['title'], report['content']))

    conn.commit()
    conn.close()
    print(f"{len(reports)} incidencias sincronizadas con la base de datos.")


def clean_html(raw_html):
    """
    Limpia el contenido HTML y extrae solo el texto.
    """
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()


def search_incidents_in_db(keyword):
    """
    Busca incidencias relacionadas con la palabra clave en la base de datos y limpia el contenido HTML.
    """
    conn = sqlite3.connect("incidencias.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT title, content FROM incidencias
    WHERE title LIKE ? OR content LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    results = cursor.fetchall()
    conn.close()

    # Limpia el contenido HTML
    cleaned_results = [(title, clean_html(content)) for title, content in results]
    return cleaned_results


def ask_gpt_about_query(keyword):
    """
    Consulta a GPT sobre incidencias relacionadas con una palabra clave.
    """
    incidents = search_incidents_in_db(keyword)

    if not incidents:
        return f"No se encontraron incidencias relacionadas con '{keyword}'."

    context = f"Consulta: '{keyword}'\n\nIncidencias encontradas:\n\n"
    for i, (title, content) in enumerate(incidents[:10], start=1):
        context += f"Incidencia {i}:\nTítulo: {title}\nContenido Completo: {content[:500]}...\n\n"
    print("\nContexto enviado a GPT:")
    print(context)

    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "Eres un asistente técnico que analiza incidencias. Proporciona un resumen claro y "
                "estructurado con los títulos y contenidos proporcionados."
            )},
            {"role": "user", "content": context}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    return response['choices'][0]['message']['content']


def main():
    """
    Main interface to interact with the user.
    """
    print("Bienvenido al Asistente de Incidencias.\n")

    query = input("Introduce tu consulta (por ejemplo, 'core', 'duplicación', 'Sysde'): ")
    response = ask_gpt_about_query(query)
    print("\nRespuesta GPT:\n")
    print(response)


if __name__ == "__main__":
    main()
