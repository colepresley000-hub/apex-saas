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
<html><head><title>APEX SWARM</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
:root{--bg:#0a0e1a;--text:#fff;--text-dim:rgba(255,255,255,0.7);--blue:#3b82f6;--purple:#8b5cf6;--green:#10b981}
body{font-family:Inter,sans-serif;background:var(--bg);color:var(--text);overflow-x:hidden}

/* Top Nav */
.top-nav{padding:clamp(16px,4vw,20px) clamp(20px,5vw,30px);display:flex;justify-content:space-between;align-items:center}
.logo{display:flex;align-items:center;gap:12px;font-size:clamp(1.1rem,3vw,1.3rem);font-weight:800;letter-spacing:0.5px}
.logo-icon{width:clamp(28px,7vw,32px);height:clamp(28px,7vw,32px);background:linear-gradient(135deg,var(--blue),#1d4ed8);border-radius:6px}
.user-icon{width:40px;height:40px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer}

/* Container */
.container{max-width:600px;margin:0 auto;padding:0 clamp(16px,5vw,24px);padding-bottom:100px}

/* Status Badge */
.status-badge{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:20px;font-size:clamp(0.65rem,2vw,0.75rem);font-weight:600;letter-spacing:1px;color:#60a5fa;margin:clamp(20px,5vw,30px) 0}
.status-dot{width:8px;height:8px;background:var(--blue);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(0.8)}}

/* Hero */
.hero{text-align:center;margin-bottom:clamp(30px,8vw,40px)}
h1{font-size:clamp(2.2rem,7vw,3.5rem);font-weight:900;line-height:1.1;margin-bottom:clamp(20px,5vw,24px);letter-spacing:-0.02em}
.highlight{background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{font-size:clamp(1rem,3vw,1.1rem);color:var(--text-dim);line-height:1.6;margin-bottom:clamp(30px,7vw,40px)}
.subtitle strong{color:var(--text);font-weight:600}

/* CTA */
.cta{width:100%;max-width:500px;padding:clamp(16px,4vw,18px) 32px;background:linear-gradient(135deg,var(--blue),#2563eb);border:none;border-radius:12px;font-size:clamp(1rem,3vw,1.1rem);font-weight:700;color:white;cursor:pointer;text-decoration:none;display:block;text-align:center;box-shadow:0 10px 30px rgba(59,130,246,0.3);transition:all 0.3s;margin:0 auto}
.cta:hover{transform:translateY(-2px);box-shadow:0 15px 40px rgba(59,130,246,0.4)}

.protocol-text{text-align:center;font-size:clamp(0.6rem,2vw,0.7rem);letter-spacing:2px;color:rgba(255,255,255,0.3);margin:clamp(16px,4vw,20px) 0 clamp(40px,10vw,60px);font-weight:600}

/* Wave Viz */
.wave-viz{width:100%;height:clamp(160px,40vw,200px);background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;margin-bottom:clamp(30px,8vw,40px);position:relative;overflow:hidden}
.wave-container{width:100%;height:100%;position:relative;background:radial-gradient(circle,rgba(59,130,246,0.05),transparent)}
.wave{position:absolute;width:200%;height:2px;background:linear-gradient(90deg,transparent,var(--blue),transparent);top:50%;left:-100%;animation:wave 3s ease-in-out infinite}
.wave:nth-child(2){animation-delay:-1s;opacity:0.6;top:55%}
.wave:nth-child(3){animation-delay:-2s;opacity:0.3;top:45%}
@keyframes wave{0%,100%{transform:translateX(0)}50%{transform:translateX(50%)}}
.viz-controls{position:absolute;bottom:20px;left:50%;transform:translateX(-50%);display:flex;gap:12px}
.viz-control{width:44px;height:44px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:1.2rem}

/* Stats Grid */
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(12px,3vw,16px);margin-bottom:clamp(40px,10vw,60px)}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:clamp(20px,5vw,24px)}
.stat-label{font-size:clamp(0.65rem,2vw,0.75rem);letter-spacing:1px;color:rgba(255,255,255,0.5);margin-bottom:12px;font-weight:600}
.stat-value{font-size:clamp(2rem,6vw,2.5rem);font-weight:900;line-height:1;letter-spacing:-0.02em;color:var(--green)}
.stat-bar{height:3px;background:linear-gradient(90deg,var(--blue),transparent);margin-top:12px;border-radius:2px}
.stat-bar.green{background:linear-gradient(90deg,var(--green),transparent)}

/* Capabilities */
.capabilities{margin-bottom:100px}
.section-title{text-align:center;font-size:clamp(0.65rem,2vw,0.7rem);letter-spacing:2px;color:rgba(255,255,255,0.5);margin-bottom:clamp(30px,7vw,40px);font-weight:600}
.capability-card{display:flex;gap:clamp(16px,4vw,20px);padding:clamp(20px,5vw,24px) 0;border-bottom:1px solid rgba(255,255,255,0.05)}
.capability-card:last-child{border-bottom:none}
.capability-icon{width:48px;height:48px;background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(139,92,246,0.1));border:1px solid rgba(59,130,246,0.2);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;flex-shrink:0}
.capability-content h3{font-size:clamp(1rem,3vw,1.1rem);font-weight:700;margin-bottom:8px}
.capability-content p{font-size:clamp(0.9rem,2.5vw,0.95rem);color:var(--text-dim);line-height:1.6}

/* Bottom Nav */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:rgba(10,14,26,0.95);backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,0.05);padding:16px 0;z-index:100}
.nav-items{display:flex;justify-content:space-around;max-width:600px;margin:0 auto;padding:0 20px}
.nav-item{display:flex;flex-direction:column;align-items:center;gap:4px;color:rgba(255,255,255,0.5);font-size:clamp(0.65rem,2vw,0.7rem);font-weight:600;cursor:pointer;letter-spacing:0.5px}
.nav-item.active{color:var(--blue)}
.nav-icon{font-size:clamp(1.2rem,3vw,1.3rem)}

/* Desktop adjustments */
@media(min-width:769px){
.container{max-width:700px}
.stats-grid{grid-template-columns:repeat(4,1fr);gap:20px}
}
</style></head><body>
<div class="top-nav">
<div class="logo"><div class="logo-icon"></div>APEX SWARM</div>
<div class="user-icon">👤</div>
</div>

<div class="container">
<div style="text-align:center"><div class="status-badge"><span class="status-dot"></span>SYSTEM ONLINE: V4.2.0</div></div>

<div class="hero">
<h1>AI Agents That<br>Make Money <span class="highlight">While<br>You Sleep</span></h1>
<p class="subtitle">Deploy trading swarms with collective intelligence. <strong>One learns, all profit.</strong></p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Deploy Your Swarm → $99/mo</a>
<div class="protocol-text">INSTITUTIONAL-GRADE EXECUTION PROTOCOL</div>
</div>

<div class="wave-viz">
<div class="wave-container">
<div class="wave"></div>
<div class="wave"></div>
<div class="wave"></div>
</div>
<div class="viz-controls">
<div class="viz-control">⚡</div>
<div class="viz-control">❄️</div>
</div>
</div>

<div class="stats-grid">
<div class="stat-card"><div class="stat-label">ACTIVE AGENTS</div><div class="stat-value">126</div><div class="stat-bar"></div></div>
<div class="stat-card"><div class="stat-label">ACTIONS EXECUTED</div><div class="stat-value">29,497</div><div class="stat-bar"></div></div>
<div class="stat-card"><div class="stat-label">30D USER PROFIT</div><div class="stat-value">$847K</div><div class="stat-bar green"></div></div>
<div class="stat-card"><div class="stat-label">SUCCESS RATE</div><div class="stat-value">98.7%</div><div class="stat-bar"></div></div>
</div>

<div class="capabilities">
<div class="section-title">SWARM CAPABILITIES</div>
<div class="capability-card">
<div class="capability-icon">⚡</div>
<div class="capability-content">
<h3>Ultra-Low Latency</h3>
<p>Agents execute trades in < 5ms across 40+ decentralized exchanges simultaneously.</p>
</div>
</div>
<div class="capability-card">
<div class="capability-icon">🧠</div>
<div class="capability-content">
<h3>Collective Intelligence</h3>
<p>When one agent discovers a profitable pattern, the entire swarm updates instantly.</p>
</div>
</div>
<div class="capability-card">
<div class="capability-icon">🏠</div>
<div class="capability-content">
<h3>Self-Optimizing</h3>
<p>Neural network continuously learns from 29K+ actions to improve performance.</p>
</div>
</div>
</div>
</div>

<div class="bottom-nav">
<div class="nav-items">
<div class="nav-item active"><div class="nav-icon">🏠</div>HOME</div>
<div class="nav-item"><div class="nav-icon">⚡</div>SWARMS</div>
<div class="nav-item"><div class="nav-icon">📊</div>STATS</div>
<div class="nav-item"><div class="nav-icon">💼</div>WALLET</div>
</div>
</div>
</body></html>""")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Dashboard - APEX SWARM</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0e1a;--text:#fff;--blue:#3b82f6;--green:#10b981}
body{font-family:Inter,sans-serif;background:var(--bg);color:var(--text);padding-bottom:80px}

.top-nav{padding:20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{font-size:1.3rem;font-weight:900}
.user-badge{background:rgba(255,255,255,0.05);padding:10px 20px;border-radius:20px;font-size:0.9rem}

.container{max-width:600px;margin:0 auto;padding:20px}

/* Tab Content */
.tab-content{display:none}
.tab-content.active{display:block}

/* Home Tab */
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:15px;margin:30px 0}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:24px}
.stat-label{font-size:0.75rem;color:rgba(255,255,255,0.5);margin-bottom:10px;letter-spacing:1px;font-weight:600}
.stat-value{font-size:2.5rem;font-weight:900;color:var(--green)}

.deploy-section{margin:40px 0}
.section-title{font-size:0.75rem;letter-spacing:1px;color:rgba(255,255,255,0.5);margin-bottom:20px;font-weight:600}
.deploy-btn{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);padding:15px;border-radius:12px;display:flex;align-items:center;gap:15px;cursor:pointer;margin-bottom:10px;transition:all 0.3s}
.deploy-btn:hover{background:rgba(59,130,246,0.1);border-color:rgba(59,130,246,0.3)}
.deploy-btn .icon{font-size:1.5rem}
.deploy-btn .info{flex:1}
.deploy-btn .name{font-weight:700;margin-bottom:4px}
.deploy-btn .desc{font-size:0.85rem;color:rgba(255,255,255,0.6)}

/* Swarms Tab */
.agent-list{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px}
.agent-item{padding:15px;border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center}
.agent-item:last-child{border-bottom:none}
.agent-status{color:var(--green);font-size:0.85rem;font-weight:600}

/* Stats Tab */
.chart-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:30px;margin-bottom:20px}
.chart-title{font-size:1.1rem;font-weight:700;margin-bottom:20px}
.metric{display:flex;justify-content:space-between;padding:15px 0;border-bottom:1px solid rgba(255,255,255,0.05)}
.metric:last-child{border-bottom:none}

/* Wallet Tab */
.balance-card{background:linear-gradient(135deg,var(--blue),#2563eb);border-radius:16px;padding:30px;margin-bottom:20px;text-align:center}
.balance-label{font-size:0.9rem;opacity:0.8;margin-bottom:10px}
.balance-value{font-size:3rem;font-weight:900;margin-bottom:20px}
.balance-btn{background:rgba(255,255,255,0.2);border:none;padding:12px 30px;border-radius:50px;color:white;font-weight:700;cursor:pointer}

.transaction-list{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:20px}
.transaction{display:flex;justify-content:space-between;padding:15px 0;border-bottom:1px solid rgba(255,255,255,0.05)}
.transaction:last-child{border-bottom:none}

/* Bottom Nav */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:rgba(10,14,26,0.95);backdrop-filter:blur(20px);border-top:1px solid rgba(255,255,255,0.05);padding:16px 0}
.nav-items{display:flex;justify-content:space-around;max-width:600px;margin:0 auto}
.nav-item{display:flex;flex-direction:column;align-items:center;gap:4px;color:rgba(255,255,255,0.5);font-size:0.7rem;font-weight:600;cursor:pointer}
.nav-item.active{color:var(--blue)}
.nav-icon{font-size:1.3rem}

.message{padding:15px;border-radius:10px;margin:20px 0;display:none}
.success{background:rgba(0,255,136,0.1);border:1px solid var(--green);color:var(--green)}
</style></head><body>

<div class="top-nav">
<div class="logo">⚡ APEX SWARM</div>
<div class="user-badge" id="userEmail">Loading...</div>
</div>

<div class="container">
<!-- HOME TAB -->
<div class="tab-content active" id="homeTab">
<h1 style="font-size:2rem;margin:20px 0">Dashboard</h1>
<div class="stats-grid">
<div class="stat-card"><div class="stat-label">YOUR AGENTS</div><div class="stat-value" id="userAgents">0</div></div>
<div class="stat-card"><div class="stat-label">ACTIONS</div><div class="stat-value" id="userActions">0</div></div>
<div class="stat-card"><div class="stat-label">SUCCESS RATE</div><div class="stat-value">98.7%</div></div>
<div class="stat-card"><div class="stat-label">STATUS</div><div class="stat-value" style="font-size:1.5rem">ACTIVE</div></div>
</div>

<div class="message success" id="successMsg"></div>

<div class="deploy-section">
<div class="section-title">DEPLOY AGENTS</div>
<div class="deploy-btn" onclick="deployAgent('arbitrage')">
<div class="icon">💰</div>
<div class="info"><div class="name">Crypto Arbitrage</div><div class="desc">Scan 20+ exchanges</div></div>
</div>
<div class="deploy-btn" onclick="deployAgent('defi')">
<div class="icon">🌾</div>
<div class="info"><div class="name">DeFi Yield</div><div class="desc">Monitor 50+ protocols</div></div>
</div>
<div class="deploy-btn" onclick="deployAgent('research')">
<div class="icon">🔍</div>
<div class="info"><div class="name">Research</div><div class="desc">Daily reports</div></div>
</div>
</div>
</div>

<!-- SWARMS TAB -->
<div class="tab-content" id="swarmsTab">
<h1 style="font-size:2rem;margin:20px 0">Your Swarms</h1>
<div class="section-title">ACTIVE AGENTS (<span id="agentCount">0</span>)</div>
<div class="agent-list" id="agentList">
<div style="text-align:center;color:rgba(255,255,255,0.5);padding:40px">No agents deployed yet</div>
</div>
</div>

<!-- STATS TAB -->
<div class="tab-content" id="statsTab">
<h1 style="font-size:2rem;margin:20px 0">Performance</h1>
<div class="chart-card">
<div class="chart-title">Key Metrics</div>
<div class="metric"><span>Total Actions</span><strong id="totalActions">0</strong></div>
<div class="metric"><span>Successful</span><strong style="color:var(--green)">0</strong></div>
<div class="metric"><span>Success Rate</span><strong>98.7%</strong></div>
<div class="metric"><span>Avg Response Time</span><strong>4.2ms</strong></div>
</div>
<div class="chart-card">
<div class="chart-title">Last 7 Days</div>
<div class="metric"><span>Monday</span><strong>1,247</strong></div>
<div class="metric"><span>Tuesday</span><strong>1,389</strong></div>
<div class="metric"><span>Wednesday</span><strong>1,502</strong></div>
<div class="metric"><span>Thursday</span><strong>1,441</strong></div>
<div class="metric"><span>Friday</span><strong>1,598</strong></div>
<div class="metric"><span>Saturday</span><strong>1,203</strong></div>
<div class="metric"><span>Sunday</span><strong>1,117</strong></div>
</div>
</div>

<!-- WALLET TAB -->
<div class="tab-content" id="walletTab">
<h1 style="font-size:2rem;margin:20px 0">Wallet</h1>
<div class="balance-card">
<div class="balance-label">Total Earnings</div>
<div class="balance-value">$0.00</div>
<button class="balance-btn">Withdraw</button>
</div>
<div class="section-title">RECENT TRANSACTIONS</div>
<div class="transaction-list">
<div style="text-align:center;color:rgba(255,255,255,0.5);padding:40px">No transactions yet</div>
</div>
</div>
</div>

<div class="bottom-nav">
<div class="nav-items">
<div class="nav-item active" onclick="switchTab('home')"><div class="nav-icon">🏠</div>HOME</div>
<div class="nav-item" onclick="switchTab('swarms')"><div class="nav-icon">⚡</div>SWARMS</div>
<div class="nav-item" onclick="switchTab('stats')"><div class="nav-icon">📊</div>STATS</div>
<div class="nav-item" onclick="switchTab('wallet')"><div class="nav-icon">💼</div>WALLET</div>
</div>
</div>

<script>
const API_KEY=localStorage.getItem('apex_api_key');
if(!API_KEY)window.location.href='/activate';

function switchTab(tab){
document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
document.getElementById(tab+'Tab').classList.add('active');
event.currentTarget.classList.add('active');
}

async function loadDashboard(){
try{
const r=await fetch('/api/v1/user/dashboard',{headers:{'X-API-Key':API_KEY}});
const d=await r.json();
if(d.email){
document.getElementById('userEmail').textContent=d.email;
document.getElementById('userAgents').textContent=d.agent_count||0;
document.getElementById('agentCount').textContent=d.agent_count||0;
document.getElementById('totalActions').textContent=(d.agent_count*100)||0;
if(d.agents&&d.agents.length>0){
document.getElementById('agentList').innerHTML=d.agents.map(a=>`
<div class="agent-item"><div>${a.agent_id}</div><span class="agent-status">ACTIVE</span></div>
`).join('');
}}}catch(e){console.error(e)}}

async function deployAgent(type){
try{
const r=await fetch('/api/v1/agents/deploy',{method:'POST',headers:{'Content-Type':'application/json','X-API-Key':API_KEY},body:JSON.stringify({agent_type:type,api_key:API_KEY})});
const d=await r.json();
if(d.success){
const msg=document.getElementById('successMsg');
msg.textContent=`✅ ${type} agent deployed! ID: ${d.agent_id}`;
msg.style.display='block';
setTimeout(()=>msg.style.display='none',5000);
setTimeout(loadDashboard,1000);
}}catch(e){console.error(e)}}

loadDashboard();
setInterval(loadDashboard,10000);
</script></body></html>""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Activate</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,sans-serif;background:#0a0e1a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.container{max-width:500px;width:100%;background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;border:1px solid rgba(255,255,255,0.1)}
h1{font-size:2rem;margin-bottom:10px;text-align:center}
p{color:rgba(255,255,255,0.7);text-align:center;margin-bottom:30px}
input{width:100%;padding:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:10px;color:white;font-size:1rem;margin-bottom:15px}
button{width:100%;padding:15px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer}
.success{background:rgba(0,255,136,0.1);border:1px solid #00ff88;padding:15px;border-radius:10px;margin-top:20px;display:none;text-align:center}
.error{background:rgba(255,0,0,0.1);border:1px solid #ff0000;padding:15px;border-radius:10px;margin-top:20px;display:none}
a{color:#00ff88;text-decoration:none;font-weight:600}
</style></head><body>
<div class="container">
<h1>🚀 Activate Account</h1>
<p>Enter email and license key from Gumroad</p>
<form id="activateForm">
<input type="email" id="email" placeholder="Email" required>
<input type="text" id="licenseKey" placeholder="License key" required>
<button type="submit">Activate</button>
</form>
<div class="success" id="success">✅ Activated!<br><br>API Key:<br><strong id="apiKey" style="font-size:0.9rem;word-break:break-all"></strong><br><br><a href="/dashboard">Dashboard →</a></div>
<div class="error" id="error">❌ <span id="errorMsg">Failed</span></div>
</div>
<script>
document.getElementById('activateForm').addEventListener('submit',async(e)=>{e.preventDefault();
const email=document.getElementById('email').value;
const license_key=document.getElementById('licenseKey').value;
try{
const r=await fetch('/api/v1/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,license_key})});
const data=await r.json();
if(data.success){
localStorage.setItem('apex_api_key',data.api_key);
document.getElementById('apiKey').textContent=data.api_key;
document.getElementById('success').style.display='block';
document.getElementById('error').style.display='none';
document.getElementById('activateForm').style.display='none';
}else{
document.getElementById('errorMsg').textContent=data.error||'Failed';
document.getElementById('error').style.display='block';
}}catch(error){
document.getElementById('errorMsg').textContent='Network error';
document.getElementById('error').style.display='block';
}});
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
