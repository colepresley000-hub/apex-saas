from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3, json, time, threading
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, license_key TEXT, api_key TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, user_id INTEGER, agent_id TEXT UNIQUE, agent_type TEXT, status TEXT DEFAULT "active", created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, agent_id TEXT, user_id INTEGER, task_type TEXT, task_description TEXT, status TEXT DEFAULT "running", result_data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, completed_at TIMESTAMP)')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

class DeployRequest(BaseModel):
    agent_type: str
    api_key: str
    task_description: str

def verify_api_key(api_key: str):
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT id, email FROM users WHERE api_key = ?", (api_key,))
    user = c.fetchone()
    conn.close()
    return user

@app.get("/")
def landing():
    return HTMLResponse("Landing page")

@app.get("/activate")  
def activate_page():
    return HTMLResponse("Activate page")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        c.execute("INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)", (request.email, request.license_key, api_key))
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False, "error": "Failed"}
    finally:
        conn.close()
@app.get("/dashboard")
def dashboard():
    return HTMLResponse("Dashboard with task modals - coming in next update")

@app.post("/api/v1/agents/deploy")
def deploy_agent(request: DeployRequest):
    user = verify_api_key(request.api_key)
    if not user:
        raise HTTPException(401)
    
    user_id = user[0]
    agent_id = f"{request.agent_type}-{secrets.token_hex(4)}"
    
    # Create agent
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("INSERT INTO agents (user_id, agent_id, agent_type) VALUES (?, ?, ?)", (user_id, agent_id, request.agent_type))
    
    # Create task
    task_id = c.lastrowid
    c.execute("INSERT INTO tasks (agent_id, user_id, task_type, task_description, status) VALUES (?, ?, ?, ?, 'running')", 
              (agent_id, user_id, request.agent_type, request.task_description))
    
    conn.commit()
    conn.close()
    
    # Execute task in background
    def execute_task():
        time.sleep(2)
        result = {"completed": True, "task": request.task_description, "timestamp": datetime.now().isoformat()}
        conn = sqlite3.connect('apex.db')
        c = conn.cursor()
        c.execute("UPDATE tasks SET status='completed', result_data=?, completed_at=? WHERE agent_id=?", 
                  (json.dumps(result), datetime.now(), agent_id))
        conn.commit()
        conn.close()
    
    threading.Thread(target=execute_task, daemon=True).start()
    
    return {"success": True, "agent_id": agent_id, "task_id": task_id}

@app.get("/api/v1/user/dashboard")
def get_dashboard(request: Request):
    api_key = request.headers.get('X-API-Key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    
    user_id = user[0]
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT agent_id, agent_type FROM agents WHERE user_id = ?", (user_id,))
    agents = [{"agent_id": r[0], "agent_type": r[1]} for r in c.fetchall()]
    conn.close()
    
    return {"email": user[1], "agent_count": len(agents), "agents": agents}

@app.get("/api/v1/tasks")
def get_tasks(request: Request):
    api_key = request.headers.get('X-API-Key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    
    user_id = user[0]
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT id, agent_id, task_description, status, result_data, created_at FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    tasks = []
    for r in c.fetchall():
        tasks.append({
            "id": r[0],
            "agent_id": r[1],
            "description": r[2],
            "status": r[3],
            "result": json.loads(r[4]) if r[4] else None,
            "created_at": r[5]
        })
    conn.close()
    
    return {"tasks": tasks}
