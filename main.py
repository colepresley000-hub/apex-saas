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
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#0a0e1a;color:#fff;padding-bottom:80px}
.top-nav{padding:20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{font-size:1.3rem;font-weight:900}
.container{max-width:600px;margin:0 auto;padding:20px}
h1{font-size:2rem;margin:20px 0}

.deploy-section{margin:30px 0}
.section-title{font-size:0.75rem;letter-spacing:1px;color:rgba(255,255,255,0.5);margin-bottom:20px;font-weight:600}
.deploy-btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:15px;border-radius:12px;display:flex;align-items:center;gap:15px;cursor:pointer;margin-bottom:10px}
.deploy-btn:hover{background:rgba(59,130,246,0.1)}
.deploy-btn .icon{font-size:1.5rem}
.deploy-btn .info{flex:1}
.deploy-btn .name{font-weight:700;margin-bottom:4px}
.deploy-btn .desc{font-size:0.85rem;color:rgba(255,255,255,0.6)}

.tasks-section{margin:30px 0}
.task-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px;margin-bottom:15px}
.task-header{display:flex;justify-content:space-between;margin-bottom:10px}
.task-status{padding:4px 12px;border-radius:12px;font-size:0.75rem;font-weight:600}
.task-status.running{background:rgba(59,130,246,0.2);color:#60a5fa}
.task-status.completed{background:rgba(16,185,129,0.2);color:#10b981}
.task-result{background:rgba(255,255,255,0.02);padding:15px;border-radius:8px;margin-top:10px;font-size:0.9rem;line-height:1.6}

.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center}
.modal.active{display:flex}
.modal-content{background:#1a1f3a;padding:30px;border-radius:20px;max-width:500px;width:90%}
.modal-title{font-size:1.5rem;font-weight:700;margin-bottom:20px}
input,textarea{width:100%;padding:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:white;font-size:1rem;margin-bottom:15px;font-family:Inter}
textarea{min-height:100px;resize:vertical}
.modal-btn{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer}
.close-modal{position:absolute;top:15px;right:15px;font-size:1.5rem;cursor:pointer;color:rgba(255,255,255,0.5)}
</style></head><body>

<div class="top-nav">
<div class="logo">⚡ APEX SWARM</div>
<div id="userEmail" style="font-size:0.9rem;color:rgba(255,255,255,0.7)">Loading...</div>
</div>

<div class="container">
<h1>Dashboard</h1>

<div class="deploy-section">
<div class="section-title">DEPLOY AGENTS</div>
<div class="deploy-btn" onclick="openModal('research')">
<div class="icon">🔍</div>
<div class="info"><div class="name">Research Agent</div><div class="desc">Market research & analysis</div></div>
</div>
<div class="deploy-btn" onclick="openModal('arbitrage')">
<div class="icon">💰</div>
<div class="info"><div class="name">Arbitrage Agent</div><div class="desc">Scan 20+ exchanges</div></div>
</div>
<div class="deploy-btn" onclick="openModal('defi')">
<div class="icon">🌾</div>
<div class="info"><div class="name">DeFi Agent</div><div class="desc">Monitor 50+ protocols</div></div>
</div>
</div>

<div class="tasks-section">
<div class="section-title">YOUR TASKS</div>
<div id="tasksList">
<div style="text-align:center;color:rgba(255,255,255,0.5);padding:40px">No tasks yet. Deploy an agent above!</div>
</div>
</div>
</div>

<div class="modal" id="taskModal">
<div class="modal-content">
<span class="close-modal" onclick="closeModal()">×</span>
<div class="modal-title" id="modalTitle">Deploy Agent</div>
<textarea id="taskDescription" placeholder="What do you want this agent to do?"></textarea>
<button class="modal-btn" onclick="deployAgent()">Deploy & Execute</button>
</div>
</div>

<script>
const API_KEY=localStorage.getItem('apex_api_key');
if(!API_KEY)window.location.href='/activate';

let currentAgentType='';

function openModal(type){
currentAgentType=type;
const titles={research:'Research Agent',arbitrage:'Arbitrage Agent',defi:'DeFi Agent'};
const placeholders={
research:'Example: Research latest AI developments in 2026',
arbitrage:'Example: Scan BTC, ETH, SOL pairs across all exchanges',
defi:'Example: Find best USDC yields on Aave and Compound'
};
document.getElementById('modalTitle').textContent=titles[type];
document.getElementById('taskDescription').placeholder=placeholders[type];
document.getElementById('taskDescription').value='';
document.getElementById('taskModal').classList.add('active');
}

function closeModal(){
document.getElementById('taskModal').classList.remove('active');
}

async function deployAgent(){
const description=document.getElementById('taskDescription').value.trim();
if(!description){alert('Please enter a task description');return;}

try{
const r=await fetch('/api/v1/agents/deploy',{
method:'POST',
headers:{'Content-Type':'application/json','X-API-Key':API_KEY},
body:JSON.stringify({agent_type:currentAgentType,api_key:API_KEY,task_description:description})
});
const d=await r.json();
if(d.success){
closeModal();
loadTasks();
}}catch(e){alert('Deployment failed')}}

async function loadTasks(){
try{
const r=await fetch('/api/v1/tasks',{headers:{'X-API-Key':API_KEY}});
const d=await r.json();
if(d.tasks&&d.tasks.length>0){
document.getElementById('tasksList').innerHTML=d.tasks.map(t=>`
<div class="task-card">
<div class="task-header">
<div><strong>${t.agent_id}</strong></div>
<span class="task-status ${t.status}">${t.status.toUpperCase()}</span>
</div>
<div style="color:rgba(255,255,255,0.7);margin-bottom:10px">${t.description}</div>
${t.result?`<div class="task-result"><pre>${JSON.stringify(t.result,null,2)}</pre></div>`:'<div style="color:rgba(255,255,255,0.5)">Processing...</div>'}
</div>
`).join('');
}}catch(e){console.error(e)}}

async function loadUser(){
try{
const r=await fetch('/api/v1/user/dashboard',{headers:{'X-API-Key':API_KEY}});
const d=await r.json();
if(d.email)document.getElementById('userEmail').textContent=d.email;
}catch(e){}}

loadUser();
loadTasks();
setInterval(loadTasks,5000);
</script></body></html>""")

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
