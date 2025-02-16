import os
import sqlite3
import hashlib
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

#  Initialize FastAPI app
app = FastAPI()

#  Ensure `templates/` directory is used
templates = Jinja2Templates(directory="templates")

#  Mount `static/` directory (Create it if needed)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

#  SQLite Database Connection
DB_FILE = "database/db.sqlite"

def get_db_connection():
    """Connect to SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

#  Ensure database and table exist
def init_db():
    os.makedirs("database", exist_ok=True)
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS short_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_key TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()
init_db()  #  Call database setup on startup

#  Request Model for URL Shortening
class URLRequest(BaseModel):
    url: str

#  Generate SHA256 Hash for Short Key
def generate_hash(url: str):
    return hashlib.sha256(url.encode()).hexdigest()[:8]

#  API: Serve Favicon to Prevent 404 Errors
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"message": "No favicon available"}

#  API: Shorten URL
@app.post("/shorten/")
async def shorten_url(request: URLRequest):
    short_key = generate_hash(request.url)

    with get_db_connection() as conn:
        # Check if the URL is already stored
        existing = conn.execute("SELECT short_key FROM short_urls WHERE original_url = ?", (request.url,)).fetchone()
        if existing:
            return {"short_url": f"https://fastapi-url-shortener-production-7250.up.railway.app/{existing['short_key']}"}

        # Store the new short URL
        try:
            conn.execute("INSERT INTO short_urls (original_url, short_key) VALUES (?, ?)", (request.url, short_key))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Short key conflict, try again.")

    return {"short_url": f"https://fastapi-url-shortener-production-7250.up.railway.app/{short_key}"}

#  API: Retrieve Original URL (Now Fixed with RedirectResponse)
@app.get("/{short_key}")
async def redirect_url(short_key: str):
    with get_db_connection() as conn:
        row = conn.execute("SELECT original_url FROM short_urls WHERE short_key = ?", (short_key,)).fetchone()

    if row:
        return RedirectResponse(url=row["original_url"])  # ✅ Redirects correctly!

    raise HTTPException(status_code=404, detail="URL not found")

#  Serve `templates/index.html`
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#  Run the server with Railway's dynamic PORT
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Default to 8080 if Railway doesn't provide PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
