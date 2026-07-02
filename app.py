from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os
import psycopg2

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'mydb')
DB_USER = os.environ.get('DB_USER', 'myuser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mypassword')

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            visited_at TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Записать визит в базу данных
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO visits (visited_at) VALUES (%s)", (datetime.now(),))
        conn.commit()

        # Посчитать общее количество визитов
        cur.execute("SELECT COUNT(*) FROM visits")
        total = cur.fetchone()[0]
        cur.close()
        conn.close()

        # Также записать в лог-файл (оставили с прошлого раза)
        with open('/app/logs/access.log', 'a') as f:
            f.write(f"{datetime.now()} - request received (total: {total})\n")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"Hello from Docker! Total visits: {total}".encode())

if __name__ == '__main__':
    init_db()
    HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
