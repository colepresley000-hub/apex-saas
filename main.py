from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3, os, subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize database
def init_db():
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE,
        license_key TEXT,
        api_key TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        agent_id TEXT UNIQUE,
        agent_type TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

class DeployRequest(BaseModel):
    agent_type: str
    api_key: str

def verify_api_key(api_key: str):
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE api_key = ?", (api_key,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.get("/")
def landing():
    return HTMLResponse("Landing page here - keeping response short")

@app.get("/dashboard")  
def dashboard():
    return HTMLResponse("Dashboard here")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        cursor.execute(
            "INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)",
            (request.email, request.license_key, api_key)
        )
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False, "error": "Failed"}
    finally:
        conn.close()

@app.get("/api/v1/user/dashboard")
def get_user_dashboard(request: Request):
    api_key = request.headers.get('X-API-Key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    return {"email": user[1], "agent_count": 0, "agents": []}

@app.post("/api/v1/agents/deploy")
def deploy_agent(request: DeployRequest):
    user = verify_api_key(request.api_key)
    if not user:
        raise HTTPException(401)
    agent_id = f"{request.agent_type}-{secrets.token_hex(4)}"
    return {"success": True, "agent_id": agent_id}

@app.get("/health")
def health():
    return {"status": "ok"}
