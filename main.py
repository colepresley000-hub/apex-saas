from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3, json, threading, time
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, license_key TEXT, api_key TEXT UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, user_id INTEGER, agent_id TEXT, agent_type TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, agent_id TEXT, user_id INTEGER, task_description TEXT, status TEXT DEFAULT "running", result_data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

class DeployRequest(BaseModel):
    agent_type: str
    task_description: str

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
def landing():
    return HTMLResponse("<html><body style='background:#0a0e1a;color:#fff;text-align:center;padding:100px'><h1>APEX SWARM</h1><p>AI Agents That Make Money</p><a href='https://colepresley.gumroad.com/l/apex-swarm' style='background:#667eea;color:#fff;padding:20px 40px;border-radius:50px;text-decoration:none;display:inline-block;margin:30px'>Get Started - $299/mo</a></body></html>")

@app.get("/activate")
def activate_page():
    return HTMLResponse("<html><body>Activate page works</body></html>")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("<html><body>Dashboard works</body></html>")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        c = conn.cursor()
        c.execute("INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)", (request.email, request.license_key, api_key))
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False}
    finally:
        conn.close()

@app.post("/api/v1/agents/deploy")
def deploy(request: DeployRequest, req: Request):
    api_key = req.headers.get('x-api-key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    agent_id = f"{request.agent_type}-{secrets.token_hex(4)}"
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("INSERT INTO agents (user_id, agent_id, agent_type) VALUES (?, ?, ?)", (user[0], agent_id, request.agent_type))
    c.execute("INSERT INTO tasks (agent_id, user_id, task_description) VALUES (?, ?, ?)", (agent_id, user[0], request.task_description))
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    def execute():
        time.sleep(3)
        result = {"status": "completed", "query": request.task_description, "timestamp": datetime.now().isoformat()}
        conn = sqlite3.connect('apex.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET status='completed', result_data=? WHERE id=?", (json.dumps(result), task_id))
        conn.commit()
        conn.close()
    threading.Thread(target=execute, daemon=True).start()
    return {"success": True, "agent_id": agent_id}

@app.get("/api/v1/tasks")
def get_tasks(req: Request):
    api_key = req.headers.get('x-api-key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT id, agent_id, task_description, status, result_data FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user[0],))
    tasks = [{"id": r[0], "agent_id": r[1], "description": r[2], "status": r[3], "result": json.loads(r[4]) if r[4] else None} for r in c.fetchall()]
    conn.close()
    return {"tasks": tasks}

@app.get("/health")
def health():
    return {"status": "ok"}
