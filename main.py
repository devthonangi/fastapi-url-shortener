import os
import sqlite3
import hashlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ SQLite Database Path
DB_FILE = "database/db.sqlite"

# ✅ Connect to SQLite Database
def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Jinja2 Template Setup (Frontend Rendering)
templates = Jinja2Templates(directory="templates")

# ✅ Request Model for URL Shortening
class URLRequest(BaseModel):
    url: str

# ✅ Generate SHA256 Hash for Short Key
def generate_hash(url: str):
    """Generate an 8-character hash for the shortened URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:8]

# 📌 API: Serve HTML Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 📌 API: Shorten URL (Inserts into Database)
@app.post("/shorten/")
async def shorten_url(request: URLRequest):
    short_key = generate_hash(request.url)

    with get_db_connection() as conn:
        existing = conn.execute("SELECT short_key FROM short_urls WHERE original_url = ?", (request.url,)).fetchone()
        if existing:
            return {"short_url": f"http://127.0.0.1:8000/{existing['short_key']}"}

        conn.execute("INSERT INTO short_urls (original_url, short_key) VALUES (?, ?)", (request.url, short_key))
        conn.commit()

    return {"short_url": f"http://127.0.0.1:8000/{short_key}"}

# 📌 API: Redirect to Original URL (Fixes Redirect Issue)
@app.get("/{short_key}")
async def redirect_url(short_key: str):
    with get_db_connection() as conn:
        row = conn.execute("SELECT original_url FROM short_urls WHERE short_key = ?", (short_key,)).fetchone()

    if row:
        return RedirectResponse(url=row["original_url"])  # ✅ Correctly Redirects to Original URL

    raise HTTPException(status_code=404, detail="URL not found")

