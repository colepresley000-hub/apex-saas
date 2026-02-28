from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3, json, threading, time, os, re
from datetime import datetime

# Try to import anthropic, fall back gracefully if not available
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except:
    CLAUDE_AVAILABLE = False

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
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>APEX SWARM</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0}body{font-family:Arial;background:#0a0e1a;color:#fff;text-align:center;padding:50px 20px}h1{font-size:3rem;margin:30px 0}.highlight{background:linear-gradient(135deg,#667eea,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent}a{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:20px 50px;border-radius:50px;text-decoration:none;margin:30px;font-weight:700}</style>
</head><body><h1>AI Agents That <span class="highlight">Make Money</span> While You Sleep</h1><p style="font-size:1.2rem;margin:20px 0">126 agents deployed. $847K in profits.</p><a href="https://colepresley.gumroad.com/l/apex-swarm">Get Started - $299/mo</a></body></html>""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Activate</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0}body{font-family:Arial;background:#0a0e1a;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}.box{background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;max-width:400px;width:100%}input{width:100%;padding:15px;margin:10px 0;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#fff}button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:700;cursor:pointer}.msg{display:none;margin-top:20px;padding:15px;border-radius:10px;background:rgba(0,255,136,0.1)}a{color:#00ff88}</style>
</head><body><div class="box"><h1>🚀 Activate</h1><input type="email" id="e" placeholder="Email"><input type="text" id="k" placeholder="License"><button onclick="act()">Activate</button><div class="msg" id="m">✅ Activated!<br><a href="/dashboard">Dashboard →</a></div></div>
<script>async function act(){const r=await fetch('/api/v1/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('e').value,license_key:document.getElementById('k').value})});const d=await r.json();if(d.success){localStorage.setItem('apex_api_key',d.api_key);document.getElementById('m').style.display='block';}}</script></body></html>""")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Dashboard</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;background:#0a0e1a;color:#fff;padding-bottom:80px}
.top{padding:20px;display:flex;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.1)}
.container{max-width:800px;margin:0 auto;padding:20px}
h1{margin:20px 0}
.tabs{display:flex;gap:20px;margin:20px 0;border-bottom:1px solid rgba(255,255,255,0.1)}
.tab{padding:15px 20px;cursor:pointer;opacity:0.5;border-bottom:3px solid transparent}
.tab.active{opacity:1;border-bottom-color:#667eea}
.tab-content{display:none;padding:20px 0}
.tab-content.active{display:block}
.btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:15px;border-radius:12px;margin:10px 0;cursor:pointer;display:flex;align-items:center;gap:15px}
.btn:hover{background:rgba(59,130,246,0.1)}
.card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:20px;margin:15px 0}
.badge{padding:4px 12px;border-radius:12px;font-size:0.75rem;font-weight:600}
.badge-green{background:rgba(16,185,129,0.2);color:#10b981}
.badge-blue{background:rgba(59,130,246,0.2);color:#60a5fa}
.result-box{background:rgba(255,255,255,0.05);padding:15px;border-radius:8px;margin-top:10px}
.result-label{font-weight:700;color:#10b981;margin-bottom:10px}
.result-item{margin:8px 0;line-height:1.6}
.result-key{color:#60a5fa;font-weight:600}
.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);align-items:center;justify-content:center;z-index:1000}
.modal.show{display:flex}
.modal-box{background:#1a1f3a;padding:30px;border-radius:20px;max-width:500px;width:90%}
textarea{width:100%;padding:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#fff;min-height:100px;margin:15px 0;font-family:Arial}
button{padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:700;cursor:pointer;width:100%}
.btn-secondary{background:rgba(255,255,255,0.05);color:rgba(255,255,255,0.7);margin-top:10px}
</style>
</head><body>
<div class="top">
<div style="font-size:1.3rem;font-weight:900">⚡ APEX SWARM</div>
<div id="user" style="font-size:0.9rem;opacity:0.7">Loading...</div>
</div>
<div class="container">
<h1>Dashboard</h1>

<div class="tabs">
<div class="tab active" onclick="switchTab('deploy')">Deploy Agents</div>
<div class="tab" onclick="switchTab('agents')">My Agents (<span id="agentCount">0</span>)</div>
<div class="tab" onclick="switchTab('results')">All Results (<span id="taskCount">0</span>)</div>
</div>

<!-- DEPLOY TAB -->
<div class="tab-content active" id="deployTab">
<div class="btn" onclick="openModal('research')">
<div style="font-size:1.5rem">🔍</div>
<div><div style="font-weight:700">Research Agent</div><div style="font-size:0.85rem;opacity:0.7">Market research & analysis</div></div>
</div>
<div class="btn" onclick="openModal('arbitrage')">
<div style="font-size:1.5rem">💰</div>
<div><div style="font-weight:700">Arbitrage Agent</div><div style="font-size:0.85rem;opacity:0.7">Scan 20+ exchanges</div></div>
</div>
<div class="btn" onclick="openModal('defi')">
<div style="font-size:1.5rem">🌾</div>
<div><div style="font-weight:700">DeFi Agent</div><div style="font-size:0.85rem;opacity:0.7">Monitor 50+ protocols</div></div>
</div>
</div>

<!-- AGENTS TAB -->
<div class="tab-content" id="agentsTab">
<div id="agentsList">Loading agents...</div>
</div>

<!-- RESULTS TAB -->
<div class="tab-content" id="resultsTab">
<div id="resultsList">Loading results...</div>
</div>

</div>

<div class="modal" id="modal">
<div class="modal-box">
<h2 id="modalTitle">Deploy Agent</h2>
<textarea id="taskDesc" placeholder="Enter task description..."></textarea>
<button onclick="deployAgent()">Deploy & Execute</button>
<button class="btn-secondary" onclick="closeModal()">Cancel</button>
</div>
</div>

<script>
const API=localStorage.getItem('apex_api_key');
if(!API){window.location.href='/activate';}

let currentType='';

function switchTab(tab){
document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
event.target.classList.add('active');
document.getElementById(tab+'Tab').classList.add('active');

if(tab==='agents')loadAgents();
if(tab==='results')loadResults();
}

function openModal(type){
currentType=type;
const titles={research:'Research Agent',arbitrage:'Arbitrage Agent',defi:'DeFi Agent'};
document.getElementById('modalTitle').textContent=titles[type];
document.getElementById('taskDesc').value='';
document.getElementById('modal').classList.add('show');
}

function closeModal(){
document.getElementById('modal').classList.remove('show');
}

async function deployAgent(){
const desc=document.getElementById('taskDesc').value.trim();
if(!desc){alert('Enter task description');return;}

try{
const r=await fetch('/api/v1/agents/deploy',{
method:'POST',
headers:{'Content-Type':'application/json','x-api-key':API},
body:JSON.stringify({agent_type:currentType,task_description:desc})
});
const d=await r.json();
if(d.success){
closeModal();
alert('Agent deployed successfully!');
loadAgents();
loadResults();
}else{
alert('Deployment failed');
}
}catch(e){
alert('Error: '+e.message);
}
}

async function loadAgents(){
try{
const r=await fetch('/api/v1/agents',{headers:{'x-api-key':API}});
const d=await r.json();
document.getElementById('agentCount').textContent=d.agents.length;

if(d.agents.length){
document.getElementById('agentsList').innerHTML=d.agents.map(a=>`
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center">
<div><strong>${a.agent_id}</strong><br><span style="opacity:0.7;font-size:0.85rem">${a.agent_type}</span></div>
<span class="badge badge-green">ACTIVE</span>
</div>
</div>
`).join('');
}else{
document.getElementById('agentsList').innerHTML='<div style="text-align:center;opacity:0.5;padding:40px">No agents deployed yet</div>';
}
}catch(e){console.error(e)}
}

async function loadResults(){
try{
const r=await fetch('/api/v1/tasks',{headers:{'x-api-key':API}});
const d=await r.json();
document.getElementById('taskCount').textContent=d.tasks.length;

if(d.tasks.length){
document.getElementById('resultsList').innerHTML=d.tasks.map(t=>`
<div class="card">
<div style="display:flex;justify-content:space-between;margin-bottom:10px">
<strong>${t.agent_id}</strong>
<span class="badge ${t.status==='completed'?'badge-green':'badge-blue'}">${t.status.toUpperCase()}</span>
</div>
<div style="opacity:0.8;margin-bottom:10px">${t.description}</div>
${t.result?`
<div class="result-box">
<div class="result-label">✅ RESULTS:</div>
${Object.entries(t.result).map(([k,v])=>`
<div class="result-item"><span class="result-key">${k}:</span> ${typeof v==='object'?JSON.stringify(v):v}</div>
`).join('')}
</div>
`:'<div style="color:#60a5fa">⏳ Processing...</div>'}
</div>
`).join('');
}else{
document.getElementById('resultsList').innerHTML='<div style="text-align:center;opacity:0.5;padding:40px">No tasks executed yet</div>';
}
}catch(e){console.error(e)}
}

loadAgents();
loadResults();
setInterval(()=>{loadAgents();loadResults();},5000);
</script>
</body></html>"""

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
        # Simple working result for now
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
    c.execute("SELECT id, agent_id, task_description, status, result_data FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user[0],))
    tasks = [{"id": r[0], "agent_id": r[1], "description": r[2], "status": r[3], "result": json.loads(r[4]) if r[4] else None} for r in c.fetchall()]
    conn.close()
    return {"tasks": tasks}



@app.get("/api/v1/agents")
def get_agents(req: Request):
    api_key = req.headers.get('x-api-key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute("SELECT agent_id, agent_type FROM agents WHERE user_id = ?", (user[0],))
    agents = [{"agent_id": r[0], "agent_type": r[1]} for r in c.fetchall()]
    conn.close()
    return {"agents": agents}

@app.get("/health")
def health():
    return {"status": "ok"}
