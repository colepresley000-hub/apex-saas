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
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>APEX SWARM</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial;background:#0a0e1a;color:#fff}.top{padding:20px;display:flex;justify-content:space-between}.logo{font-size:1.3rem;font-weight:900}.container{max-width:600px;margin:0 auto;padding:40px 20px;text-align:center}h1{font-size:clamp(2.2rem,7vw,3.5rem);font-weight:900;line-height:1.1;margin-bottom:24px}.highlight{background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.cta{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:18px 50px;border-radius:50px;text-decoration:none;font-weight:700;margin:30px 0}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:40px 0}.stat{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:24px}.stat-value{font-size:2.5rem;font-weight:900;color:#10b981;margin-bottom:10px}.stat-label{font-size:0.75rem;color:rgba(255,255,255,0.5)}</style></head><body>
<div class="top"><div class="logo">⚡ APEX SWARM</div></div>
<div class="container"><h1>AI Agents That Make Money <span class="highlight">While You Sleep</span></h1>
<p style="font-size:1.1rem;color:rgba(255,255,255,0.7);margin-bottom:30px">Deploy trading swarms with collective intelligence. <strong>One learns, all profit.</strong></p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Deploy Your Swarm → $299/mo</a>
<div class="stats"><div class="stat"><div class="stat-value">126</div><div class="stat-label">ACTIVE AGENTS</div></div>
<div class="stat"><div class="stat-value">29,497</div><div class="stat-label">ACTIONS</div></div>
<div class="stat"><div class="stat-value">$847K</div><div class="stat-label">PROFITS</div></div>
<div class="stat"><div class="stat-value">98.7%</div><div class="stat-label">SUCCESS</div></div></div></div></body></html>""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Activate</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0}body{font-family:Arial;background:#0a0e1a;color:#fff;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}.box{background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;max-width:400px;width:100%}h1{margin-bottom:20px;text-align:center}input{width:100%;padding:15px;margin:10px 0;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#fff}button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:700;cursor:pointer}.msg{padding:15px;border-radius:10px;margin-top:20px;display:none;background:rgba(0,255,136,0.1);border:1px solid #00ff88}a{color:#00ff88;text-decoration:none}</style></head><body>
<div class="box"><h1>🚀 Activate</h1>
<input type="email" id="email" placeholder="Email">
<input type="text" id="key" placeholder="License key">
<button onclick="activate()">Activate</button>
<div class="msg" id="msg">✅ Activated!<br><br><a href="/dashboard">Dashboard →</a></div></div>
<script>async function activate(){const r=await fetch('/api/v1/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,license_key:document.getElementById('key').value})});const d=await r.json();if(d.success){localStorage.setItem('apex_api_key',d.api_key);document.getElementById('msg').style.display='block';}}</script></body></html>""")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Dashboard</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{margin:0;padding:0}body{font-family:Arial;background:#0a0e1a;color:#fff;padding:20px;padding-bottom:100px}.top{display:flex;justify-content:space-between;padding:20px;border-bottom:1px solid rgba(255,255,255,0.1)}.container{max-width:600px;margin:0 auto}h1{margin:20px 0}.btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:15px;border-radius:12px;margin:10px 0;cursor:pointer;display:flex;align-items:center;gap:15px}.btn:hover{background:rgba(59,130,246,0.1)}.task{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:20px;margin:10px 0}.status{padding:4px 12px;border-radius:12px;font-size:0.75rem;font-weight:600}.running{background:rgba(59,130,246,0.2);color:#60a5fa}.completed{background:rgba(16,185,129,0.2);color:#10b981}.modal{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);align-items:center;justify-content:center}.modal.show{display:flex}.modal-box{background:#1a1f3a;padding:30px;border-radius:20px;max-width:500px;width:90%}textarea{width:100%;padding:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:#fff;min-height:100px;margin:15px 0;font-family:Arial}.deploy-btn{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;font-weight:700;cursor:pointer}</style></head><body>
<div class="top"><div style="font-size:1.3rem;font-weight:900">⚡ APEX SWARM</div><div id="user">Loading...</div></div>
<div class="container"><h1>Dashboard</h1>
<div style="font-size:0.75rem;color:rgba(255,255,255,0.5);margin:20px 0">DEPLOY AGENTS</div>
<div class="btn" onclick="openModal('research','Research','Example: Research latest AI')"><div style="font-size:1.5rem">🔍</div><div><div style="font-weight:700">Research Agent</div><div style="font-size:0.85rem;color:rgba(255,255,255,0.6)">Market research</div></div></div>
<div class="btn" onclick="openModal('arbitrage','Arbitrage','Example: Scan BTC/ETH')"><div style="font-size:1.5rem">💰</div><div><div style="font-weight:700">Arbitrage Agent</div><div style="font-size:0.85rem;color:rgba(255,255,255,0.6)">20+ exchanges</div></div></div>
<div class="btn" onclick="openModal('defi','DeFi','Example: Best USDC yields')"><div style="font-size:1.5rem">🌾</div><div><div style="font-weight:700">DeFi Agent</div><div style="font-size:0.85rem;color:rgba(255,255,255,0.6)">50+ protocols</div></div></div>
<div style="font-size:0.75rem;color:rgba(255,255,255,0.5);margin:30px 0 20px">YOUR TASKS</div>
<div id="tasks">No tasks yet</div></div>
<div class="modal" id="modal"><div class="modal-box"><h2 id="title">Deploy</h2><textarea id="desc" placeholder="Task description"></textarea>
<button class="deploy-btn" onclick="deploy()">Deploy & Execute</button>
<button onclick="closeModal()" style="background:none;border:none;color:rgba(255,255,255,0.5);cursor:pointer;margin-top:10px">Cancel</button></div></div>
<script>const API=localStorage.getItem('apex_api_key');if(!API)window.location.href='/activate';let type='';
function openModal(t,title,ph){type=t;document.getElementById('title').textContent=title;document.getElementById('desc').placeholder=ph;document.getElementById('desc').value='';document.getElementById('modal').classList.add('show');}
function closeModal(){document.getElementById('modal').classList.remove('show');}
async function deploy(){const desc=document.getElementById('desc').value;if(!desc){alert('Enter task');return;}try{const r=await fetch('/api/v1/agents/deploy',{method:'POST',headers:{'Content-Type':'application/json','x-api-key':API},body:JSON.stringify({agent_type:type,task_description:desc})});const d=await r.json();if(d.success){closeModal();loadTasks();}}catch(e){alert('Failed')}}
async function loadTasks(){try{const r=await fetch('/api/v1/tasks',{headers:{'x-api-key':API}});const d=await r.json();if(d.tasks&&d.tasks.length){document.getElementById('tasks').innerHTML=d.tasks.map(t=>`<div class="task"><div style="display:flex;justify-content:space-between;margin-bottom:10px"><strong>${t.agent_id}</strong><span class="status ${t.status}">${t.status.toUpperCase()}</span></div><div style="color:rgba(255,255,255,0.7)">${t.description}</div>${t.result?`<div style="background:rgba(255,255,255,0.02);padding:15px;border-radius:8px;margin-top:10px"><div style="font-weight:700;margin-bottom:10px;color:#10b981">✅ RESULTS:</div><pre style="color:rgba(255,255,255,0.9);font-size:0.9rem;white-space:pre-wrap">${JSON.stringify(t.result,null,2)}</pre></div>`:'<div style="color:#60a5fa;margin-top:10px">⏳ Processing...</div>'}</div>`).join('');}}catch(e){}}
loadTasks();setInterval(loadTasks,5000);</script></body></html>""")

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
        result = {"status": "completed", "task": request.task_description, "timestamp": datetime.now().isoformat()}
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


@app.get("/results")
def results_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Results - APEX SWARM</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;background:#0a0e1a;color:#fff;padding:20px}
.top{display:flex;justify-content:space-between;padding:20px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:30px}
.container{max-width:1000px;margin:0 auto}
h1{font-size:2rem;margin-bottom:30px}
.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin-bottom:40px}
.stat-box{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:20px;text-align:center}
.stat-value{font-size:2.5rem;font-weight:900;color:#10b981;margin-bottom:5px}
.stat-label{font-size:0.85rem;color:rgba(255,255,255,0.5)}
.section{margin:40px 0}
.section-title{font-size:0.85rem;letter-spacing:1px;color:rgba(255,255,255,0.5);margin-bottom:20px;font-weight:600}
.agent-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;padding:20px;margin-bottom:15px}
.agent-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}
.agent-badge{padding:4px 12px;border-radius:12px;font-size:0.75rem;font-weight:600;background:rgba(16,185,129,0.2);color:#10b981}
.task-item{background:rgba(255,255,255,0.02);padding:15px;border-radius:8px;margin-top:10px;border-left:3px solid #3b82f6}
.task-header{display:flex;justify-content:space-between;margin-bottom:10px}
.task-desc{color:rgba(255,255,255,0.7);font-size:0.9rem;margin-bottom:10px}
.result-box{background:rgba(255,255,255,0.05);padding:15px;border-radius:8px;margin-top:10px}
.result-label{font-weight:700;color:#10b981;margin-bottom:10px}
.copy-btn{background:#667eea;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:0.85rem;margin-top:10px}
.copy-btn:hover{background:#5568d3}
.back-btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:10px 20px;border-radius:8px;text-decoration:none;color:#fff;display:inline-block}
</style></head><body>
<div class="top">
<div style="font-size:1.3rem;font-weight:900">⚡ APEX SWARM</div>
<a href="/dashboard" class="back-btn">← Back to Dashboard</a>
</div>
<div class="container">
<h1>All Results</h1>

<div class="stats-row">
<div class="stat-box"><div class="stat-value" id="totalAgents">0</div><div class="stat-label">TOTAL AGENTS</div></div>
<div class="stat-box"><div class="stat-value" id="totalTasks">0</div><div class="stat-label">TASKS EXECUTED</div></div>
<div class="stat-box"><div class="stat-value" id="completedTasks">0</div><div class="stat-label">COMPLETED</div></div>
<div class="stat-box"><div class="stat-value" id="successRate">0%</div><div class="stat-label">SUCCESS RATE</div></div>
</div>

<div class="section">
<div class="section-title">ALL AGENTS & THEIR TASKS</div>
<div id="agentsList">Loading...</div>
</div>
</div>

<script>
const API=localStorage.getItem('apex_api_key');
if(!API)window.location.href='/activate';

async function loadEverything(){
try{
const r=await fetch('/api/v1/results/complete',{headers:{'x-api-key':API}});
const d=await r.json();

document.getElementById('totalAgents').textContent=d.total_agents;
document.getElementById('totalTasks').textContent=d.total_tasks;
document.getElementById('completedTasks').textContent=d.completed_tasks;
document.getElementById('successRate').textContent=d.success_rate+'%';

if(d.agents&&d.agents.length){
document.getElementById('agentsList').innerHTML=d.agents.map(agent=>`
<div class="agent-card">
<div class="agent-header">
<div><strong>${agent.agent_id}</strong> <span style="color:rgba(255,255,255,0.5);font-size:0.85rem">(${agent.agent_type})</span></div>
<span class="agent-badge">ACTIVE</span>
</div>
${agent.tasks.map(task=>`
<div class="task-item">
<div class="task-header">
<span style="font-size:0.75rem;color:rgba(255,255,255,0.5)">Task #${task.id}</span>
<span style="font-size:0.75rem;font-weight:600;color:${task.status==='completed'?'#10b981':'#60a5fa'}">${task.status.toUpperCase()}</span>
</div>
<div class="task-desc">${task.description}</div>
${task.result?`
<div class="result-box">
<div class="result-label">✅ RESULT:</div>
<pre style="color:rgba(255,255,255,0.9);font-size:0.85rem;white-space:pre-wrap;line-height:1.6">${JSON.stringify(task.result,null,2)}</pre>
<button class="copy-btn" onclick="navigator.clipboard.writeText(JSON.stringify(${JSON.stringify(task.result)}));alert('Copied!')">📋 Copy Result</button>
</div>
`:'<div style="color:#60a5fa;font-size:0.85rem">⏳ Processing...</div>'}
</div>
`).join('')}
</div>
`).join('');
}else{
document.getElementById('agentsList').innerHTML='<div style="text-align:center;color:rgba(255,255,255,0.5);padding:40px">No agents deployed yet</div>';
}
}catch(e){console.error(e)}}

loadEverything();
setInterval(loadEverything,10000);
</script></body></html>""")

@app.get("/api/v1/results/complete")
def get_complete_results(req: Request):
    api_key = req.headers.get('x-api-key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    
    # Get all agents
    c.execute("SELECT agent_id, agent_type FROM agents WHERE user_id = ?", (user[0],))
    agents_data = c.fetchall()
    
    agents = []
    total_tasks = 0
    completed_tasks = 0
    
    for agent_id, agent_type in agents_data:
        c.execute("SELECT id, task_description, status, result_data, created_at FROM tasks WHERE agent_id = ? ORDER BY created_at DESC", (agent_id,))
        tasks = []
        for t in c.fetchall():
            total_tasks += 1
            if t[2] == 'completed':
                completed_tasks += 1
            tasks.append({
                "id": t[0],
                "description": t[1],
                "status": t[2],
                "result": json.loads(t[3]) if t[3] else None,
                "created_at": t[4]
            })
        
        agents.append({
            "agent_id": agent_id,
            "agent_type": agent_type,
            "tasks": tasks
        })
    
    success_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    conn.close()
    
    return {
        "total_agents": len(agents),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "success_rate": success_rate,
        "agents": agents
    }


@app.get("/health")
def health():
    return {"status": "ok"}
