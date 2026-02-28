from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, license_key TEXT, api_key TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, user_id INTEGER, agent_id TEXT, agent_type TEXT)')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

def verify_api_key(api_key: str):
    if not api_key:
        return None
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT id, email FROM users WHERE api_key = ?", (api_key,))
    user = c.fetchone()
    conn.close()
    return user

@app.get("/")
def root():
    return HTMLResponse(open('FINAL_LANDING_PAGE.html').read() if True else "Apex Swarm")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        c = conn.cursor()
        c.execute("INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)", 
                  (request.email, request.license_key, api_key))
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False, "error": "Failed"}
    finally:
        conn.close()

@app.get("/health")
def health():
    return {"status": "ok", "message": "System online"}
