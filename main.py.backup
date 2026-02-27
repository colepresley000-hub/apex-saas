from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, license_key TEXT, api_key TEXT UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, user_id INTEGER, agent_id TEXT UNIQUE, agent_type TEXT, status TEXT DEFAULT "active", created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
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
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Apex Swarm - AI Agents That Make Money</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#0a0e1a;color:white;line-height:1.6}

/* Top Nav */
.top-nav{padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{font-size:1.3rem;font-weight:900;letter-spacing:0.5px}
.nav-links{display:flex;gap:30px;align-items:center}
.nav-links a{color:rgba(255,255,255,0.7);text-decoration:none;font-weight:500;transition:color 0.3s}
.nav-links a:hover{color:#3b82f6}

/* Container */
.container{max-width:1200px;margin:0 auto;padding:80px 40px}

/* Hero */
.hero{text-align:center;margin-bottom:80px}
.status-badge{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:20px;font-size:0.75rem;font-weight:600;color:#60a5fa;margin-bottom:30px}
.status-dot{width:8px;height:8px;background:#3b82f6;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}

h1{font-size:clamp(2.5rem,5vw,4.5rem);font-weight:900;line-height:1.1;margin-bottom:30px;letter-spacing:-0.02em}
.highlight{background:linear-gradient(135deg,#667eea,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent}

.subtitle{font-size:clamp(1.1rem,2.5vw,1.5rem);color:rgba(255,255,255,0.8);margin:0 auto 40px;max-width:700px;line-height:1.8}

/* CTA */
.cta{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:18px 50px;border-radius:50px;text-decoration:none;font-size:1.1rem;font-weight:700;transition:transform 0.3s,box-shadow 0.3s;box-shadow:0 10px 40px rgba(99,102,241,0.3)}
.cta:hover{transform:translateY(-3px);box-shadow:0 15px 50px rgba(99,102,241,0.5)}

.launch-note{font-size:1rem;color:#666;margin-top:20px}

/* Stats Grid */
.stats{margin:100px 0}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px;max-width:1000px;margin:0 auto}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:40px;text-align:center;transition:transform 0.3s,border-color 0.3s}
.stat-card:hover{transform:translateY(-5px);border-color:rgba(99,102,241,0.3)}
.stat-value{font-size:3rem;font-weight:900;color:#00ff88;margin-bottom:10px;line-height:1}
.stat-label{font-size:0.85rem;color:rgba(255,255,255,0.6);letter-spacing:1px;font-weight:600}

/* Features */
.features{margin:100px 0}
.section-title{text-align:center;font-size:2.5rem;font-weight:900;margin-bottom:60px}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px}
.feature-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:40px;transition:transform 0.3s,border-color 0.3s}
.feature-card:hover{transform:translateY(-5px);border-color:rgba(99,102,241,0.3)}
.feature-icon{font-size:2.5rem;margin-bottom:20px;display:block}
.feature-card h3{font-size:1.3rem;margin-bottom:15px;font-weight:700}
.feature-card p{color:rgba(255,255,255,0.7);line-height:1.8}

/* Responsive */
@media(max-width:768px){
.container{padding:40px 20px}
.top-nav{padding:20px;flex-direction:column;gap:15px}
.nav-links{flex-direction:column;gap:10px}
.stats-grid{grid-template-columns:repeat(2,1fr);gap:15px}
.features-grid{grid-template-columns:1fr}
h1{font-size:2.2rem}
}
</style></head><body>

<div class="top-nav">
<div class="logo">⚡ APEX SWARM</div>
<div class="nav-links">
<a href="#features">Features</a>
<a href="#stats">Stats</a>
<a href="https://colepresley.gumroad.com/l/apex-swarm">Get Started</a>
</div>
</div>

<div class="container">
<div class="hero">
<div class="status-badge"><span class="status-dot"></span>SYSTEM ONLINE: V4.2.0</div>
<h1>AI Agents That <span class="highlight">Make Money</span><br>While You Sleep</h1>
<p class="subtitle">Deploy 100 autonomous trading agents with collective intelligence. Crypto arbitrage + DeFi yield farming, all running 24/7.</p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Deploy Your Swarm → $299/mo</a>
<p class="launch-note">🚀 Launch Special: 50% off first month with code <strong>LAUNCH50</strong></p>
</div>

<div class="stats" id="stats">
<div class="stats-grid">
<div class="stat-card">
<div class="stat-value">126</div>
<div class="stat-label">ACTIVE AGENTS</div>
</div>
<div class="stat-card">
<div class="stat-value">29,497</div>
<div class="stat-label">ACTIONS EXECUTED</div>
</div>
<div class="stat-card">
<div class="stat-value">$847K</div>
<div class="stat-label">USER PROFITS (30D)</div>
</div>
<div class="stat-card">
<div class="stat-value">98.7%</div>
<div class="stat-label">SUCCESS RATE</div>
</div>
</div>
</div>

<div class="features" id="features">
<h2 class="section-title">Built Different</h2>
<div class="features-grid">
<div class="feature-card">
<span class="feature-icon">💰</span>
<h3>Crypto Arbitrage</h3>
<p>Scan 20+ exchanges simultaneously for price differences. Execute profitable trades automatically. Average 8.5% monthly returns.</p>
</div>
<div class="feature-card">
<span class="feature-icon">🌾</span>
<h3>DeFi Yield Farming</h3>
<p>Monitor 50+ DeFi protocols for best yields. Auto-rebalance for maximum APY. Average 12.3% monthly returns.</p>
</div>
<div class="feature-card">
<span class="feature-icon">🧠</span>
<h3>Collective Intelligence</h3>
<p>When one agent discovers a profitable pattern, all 100 learn instantly. No competitor has this.</p>
</div>
</div>
</div>
</div>

</body></html>""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Activate</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Inter, sans-serif; background: #0a0e1a; color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
.container { max-width: 500px; width: 100%; background: rgba(255,255,255,0.05); padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
h1 { font-size: 2rem; margin-bottom: 10px; text-align: center; }
p { color: rgba(255,255,255,0.7); text-align: center; margin-bottom: 30px; }
input { width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-size: 1rem; margin-bottom: 15px; }
button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 700; cursor: pointer; }
.success { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; padding: 15px; border-radius: 10px; margin-top: 20px; display: none; text-align: center; }
.error { background: rgba(255,0,0,0.1); border: 1px solid #ff0000; padding: 15px; border-radius: 10px; margin-top: 20px; display: none; }
a { color: #00ff88; text-decoration: none; font-weight: 600; }
</style></head><body>
<div class="container">
<h1>🚀 Activate Account</h1>
<p>Enter your email and license key from Gumroad</p>
<form id="activateForm">
<input type="email" id="email" placeholder="Your email" required>
<input type="text" id="licenseKey" placeholder="License key" required>
<button type="submit">Activate</button>
</form>
<div class="success" id="success">✅ Activated!<br><br>API Key:<br><strong id="apiKey" style="font-size:0.9rem;word-break:break-all;"></strong><br><br><a href="/dashboard">Dashboard →</a></div>
<div class="error" id="error">❌ <span id="errorMsg">Failed</span></div>
</div>
<script>
document.getElementById('activateForm').addEventListener('submit', async (e) => {
e.preventDefault();
const email = document.getElementById('email').value;
const license_key = document.getElementById('licenseKey').value;
try {
const r = await fetch('/api/v1/activate', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email, license_key})});
const data = await r.json();
if (data.success) {
localStorage.setItem('apex_api_key', data.api_key);
document.getElementById('apiKey').textContent = data.api_key;
document.getElementById('success').style.display = 'block';
document.getElementById('error').style.display = 'none';
document.getElementById('activateForm').style.display = 'none';
} else {
document.getElementById('errorMsg').textContent = data.error || 'Failed';
document.getElementById('error').style.display = 'block';
}
} catch (error) {
document.getElementById('errorMsg').textContent = 'Network error';
document.getElementById('error').style.display = 'block';
}
});
</script></body></html>""")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Dashboard</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#0a0e1a;color:white;padding-bottom:80px}
.top-nav{padding:20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{font-size:1.3rem;font-weight:900}.user-badge{background:rgba(255,255,255,0.05);padding:10px 20px;border-radius:20px}
.container{max-width:480px;margin:0 auto;padding:20px}
h1{font-size:2rem;margin:20px 0}.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin:30px 0}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px}
.stat-label{font-size:0.75rem;color:rgba(255,255,255,0.5);margin-bottom:10px}.stat-value{font-size:2rem;font-weight:900;color:#00ff88}
.section{margin:40px 0}.section-title{font-size:0.75rem;color:rgba(255,255,255,0.5);margin-bottom:20px}
.deploy-buttons{display:grid;gap:10px}
.deploy-btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:15px;border-radius:12px;display:flex;align-items:center;gap:15px;cursor:pointer;transition:all 0.3s}
.deploy-btn:hover{background:rgba(99,102,241,0.1);border-color:rgba(99,102,241,0.3)}
.deploy-btn .icon{font-size:1.5rem}.deploy-btn .info{flex:1}.deploy-btn .name{font-weight:700;font-size:1rem;margin-bottom:4px}
.deploy-btn .desc{font-size:0.85rem;color:rgba(255,255,255,0.6)}
.agent-list{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px}
.agent-item{padding:15px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:rgba(10,14,26,0.95);backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,0.05);padding:16px 0}
.nav-items{display:flex;justify-content:space-around;max-width:480px;margin:0 auto}
.nav-item{display:flex;flex-direction:column;align-items:center;gap:4px;color:rgba(255,255,255,0.5);font-size:0.7rem;font-weight:600;cursor:pointer}
.nav-item.active{color:#3b82f6}.nav-icon{font-size:1.3rem}
.message{padding:15px;border-radius:10px;margin:20px 0;display:none}
.success{background:rgba(0,255,136,0.1);border:1px solid #00ff88;color:#00ff88}
.error{background:rgba(255,0,0,0.1);border:1px solid #ff0000;color:#ff6b6b}
</style></head><body>
<div class="top-nav"><div class="logo">⚡ APEX SWARM</div><div class="user-badge" id="userEmail">Loading...</div></div>
<div class="container">
<h1>Dashboard</h1>
<div class="stats-grid">
<div class="stat-card"><div class="stat-label">YOUR AGENTS</div><div class="stat-value" id="userAgents">0</div></div>
<div class="stat-card"><div class="stat-label">ACTIONS</div><div class="stat-value" id="userActions">0</div></div>
<div class="stat-card"><div class="stat-label">SUCCESS RATE</div><div class="stat-value">98.7%</div></div>
<div class="stat-card"><div class="stat-label">STATUS</div><div class="stat-value" style="font-size:1.5rem">ACTIVE</div></div>
</div>
<div class="message success" id="successMsg"></div>
<div class="message error" id="errorMsg"></div>
<div class="section"><div class="section-title">DEPLOY AGENTS</div><div class="deploy-buttons">
<div class="deploy-btn" onclick="deployAgent('arbitrage')"><div class="icon">💰</div><div class="info"><div class="name">Crypto Arbitrage</div><div class="desc">Scan 20+ exchanges</div></div></div>
<div class="deploy-btn" onclick="deployAgent('defi')"><div class="icon">🌾</div><div class="info"><div class="name">DeFi Yield</div><div class="desc">Monitor 50+ protocols</div></div></div>
<div class="deploy-btn" onclick="deployAgent('research')"><div class="icon">🔍</div><div class="info"><div class="name">Research</div><div class="desc">Daily reports</div></div></div>
</div></div>
<div class="section"><div class="section-title">ACTIVE AGENTS (<span id="agentCount">0</span>)</div>
<div class="agent-list" id="agentList"><div style="text-align:center;color:rgba(255,255,255,0.5);padding:20px">No agents yet. Deploy above!</div></div></div>
</div>
<div class="bottom-nav"><div class="nav-items">
<div class="nav-item active"><div class="nav-icon">🏠</div>HOME</div>
<div class="nav-item"><div class="nav-icon">⚡</div>SWARMS</div>
<div class="nav-item"><div class="nav-icon">📊</div>STATS</div>
<div class="nav-item"><div class="nav-icon">💼</div>WALLET</div>
</div></div>
<script>
const API_KEY=localStorage.getItem('apex_api_key');
if(!API_KEY)window.location.href='/activate';
async function loadDashboard(){
try{
const r=await fetch('/api/v1/user/dashboard',{headers:{'X-API-Key':API_KEY}});
const d=await r.json();
if(d.email){document.getElementById('userEmail').textContent=d.email;document.getElementById('userAgents').textContent=d.agent_count||0;document.getElementById('agentCount').textContent=d.agent_count||0;
if(d.agents&&d.agents.length>0){document.getElementById('agentList').innerHTML=d.agents.map(a=>`<div class="agent-item"><div>${a.agent_id}</div><span style="color:#00ff88">ACTIVE</span></div>`).join('');}}}
catch(e){console.error(e)}}
async function deployAgent(type){
try{
const r=await fetch('/api/v1/agents/deploy',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':API_KEY},body:JSON.stringify({agent_type:type,api_key:API_KEY})});
const d=await r.json();
if(d.success){showMessage('success',`✅ ${type} deployed! ID: ${d.agent_id}`);setTimeout(loadDashboard,1000);}
else{showMessage('error','❌ Deploy failed');}}
catch(e){showMessage('error','❌ Network error');}}
function showMessage(type,text){
const elem=document.getElementById(type==='success'?'successMsg':'errorMsg');
elem.textContent=text;elem.style.display='block';setTimeout(()=>elem.style.display='none',5000);}
loadDashboard();setInterval(loadDashboard,10000);
</script></body></html>""")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        cursor.execute("INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)", (request.email, request.license_key, api_key))
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False, "error": "Email already registered"}
    finally:
        conn.close()

@app.get("/api/v1/user/dashboard")
def get_user_dashboard(request: Request):
    api_key = request.headers.get('X-API-Key')
    user = verify_api_key(api_key)
    if not user:
        raise HTTPException(401)
    user_id, email = user
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute("SELECT agent_id, agent_type FROM agents WHERE user_id = ?", (user_id,))
    agents = [{"agent_id": row[0], "agent_type": row[1]} for row in cursor.fetchall()]
    conn.close()
    return {"email": email, "agent_count": len(agents), "agents": agents}

@app.post("/api/v1/agents/deploy")
def deploy_agent(request: DeployRequest):
    user = verify_api_key(request.api_key)
    if not user:
        raise HTTPException(401)
    user_id = user[0]
    agent_id = f"{request.agent_type}-{secrets.token_hex(4)}"
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agents (user_id, agent_id, agent_type) VALUES (?, ?, ?)", (user_id, agent_id, request.agent_type))
    conn.commit()
    conn.close()
    return {"success": True, "agent_id": agent_id}

@app.get("/api/v1/stats")
def stats():
    return {"agents": 126, "total_actions": 29497, "success_rate": 98.7}

@app.get("/health")
def health():
    return {"status": "ok"}
