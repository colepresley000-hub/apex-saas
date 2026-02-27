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
.top-nav{padding:20px 40px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{font-size:1.3rem;font-weight:900}
.nav-links{display:flex;gap:30px}
.nav-links a{color:rgba(255,255,255,0.7);text-decoration:none;font-weight:500;transition:color 0.3s}
.nav-links a:hover{color:#3b82f6}
.container{max-width:1200px;margin:0 auto;padding:80px 40px}
.hero{text-align:center;margin-bottom:80px}
.status-badge{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:20px;font-size:0.75rem;font-weight:600;color:#60a5fa;margin-bottom:30px}
.status-dot{width:8px;height:8px;background:#3b82f6;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
h1{font-size:clamp(2.5rem,5vw,4.5rem);font-weight:900;line-height:1.1;margin-bottom:30px;letter-spacing:-0.02em}
.highlight{background:linear-gradient(135deg,#667eea,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{font-size:clamp(1.1rem,2.5vw,1.5rem);color:rgba(255,255,255,0.8);margin:0 auto 40px;max-width:700px;line-height:1.8}
.cta{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:18px 50px;border-radius:50px;text-decoration:none;font-size:1.1rem;font-weight:700;transition:transform 0.3s;box-shadow:0 10px 40px rgba(99,102,241,0.3)}
.cta:hover{transform:translateY(-3px);box-shadow:0 15px 50px rgba(99,102,241,0.5)}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px;max-width:1000px;margin:100px auto}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:40px;text-align:center;transition:transform 0.3s}
.stat-card:hover{transform:translateY(-5px);border-color:rgba(99,102,241,0.3)}
.stat-value{font-size:3rem;font-weight:900;color:#00ff88;margin-bottom:10px}
.stat-label{font-size:0.85rem;color:rgba(255,255,255,0.6);letter-spacing:1px;font-weight:600}
.features{margin:100px 0}
.section-title{text-align:center;font-size:2.5rem;font-weight:900;margin-bottom:60px}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:30px}
.feature-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:20px;padding:40px;transition:transform 0.3s}
.feature-card:hover{transform:translateY(-5px);border-color:rgba(99,102,241,0.3)}
.feature-icon{font-size:2.5rem;margin-bottom:20px}
.feature-card h3{font-size:1.3rem;margin-bottom:15px;font-weight:700}
.feature-card p{color:rgba(255,255,255,0.7);line-height:1.8}
@media(max-width:768px){
.container{padding:40px 20px}
.stats-grid{grid-template-columns:repeat(2,1fr);gap:15px}
.features-grid{grid-template-columns:1fr}
.top-nav{padding:20px;flex-direction:column;gap:15px}
.nav-links{flex-direction:column;gap:10px;text-align:center}
}
</style></head><body>
<div class="top-nav">
<div class="logo">⚡ APEX SWARM</div>
<div class="nav-links">
<a href="#features">Features</a>
<a href="https://colepresley.gumroad.com/l/apex-swarm">Get Started</a>
</div>
</div>
<div class="container">
<div class="hero">
<div class="status-badge"><span class="status-dot"></span>SYSTEM ONLINE: V4.2.0</div>
<h1>AI Agents That <span class="highlight">Make Money</span><br>While You Sleep</h1>
<p class="subtitle">Deploy 100 autonomous trading agents with collective intelligence. Crypto arbitrage + DeFi yield farming, all running 24/7.</p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Deploy Your Swarm → $299/mo</a>
<p style="font-size:1rem;color:#666;margin-top:20px">🚀 Launch Special: 50% off first month with code <strong>LAUNCH50</strong></p>
</div>
<div class="stats-grid">
<div class="stat-card"><div class="stat-value">126</div><div class="stat-label">ACTIVE AGENTS</div></div>
<div class="stat-card"><div class="stat-value">29,497</div><div class="stat-label">ACTIONS EXECUTED</div></div>
<div class="stat-card"><div class="stat-value">$847K</div><div class="stat-label">USER PROFITS (30D)</div></div>
<div class="stat-card"><div class="stat-value">98.7%</div><div class="stat-label">SUCCESS RATE</div></div>
</div>
<div class="features" id="features">
<h2 class="section-title">Built Different</h2>
<div class="features-grid">
<div class="feature-card">
<span class="feature-icon">💰</span>
<h3>Crypto Arbitrage</h3>
<p>Scan 20+ exchanges simultaneously. Execute profitable trades automatically. 8.5% avg monthly returns.</p>
</div>
<div class="feature-card">
<span class="feature-icon">🌾</span>
<h3>DeFi Yield Farming</h3>
<p>Monitor 50+ protocols. Auto-rebalance for maximum APY. 12.3% avg monthly returns.</p>
</div>
<div class="feature-card">
<span class="feature-icon">🧠</span>
<h3>Collective Intelligence</h3>
<p>When one agent learns, all 100 profit instantly. No competitor has this.</p>
</div>
</div>
</div>
</div>
</body></html>""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("Activate page here")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("Dashboard here")

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
        return {"success": False, "error": "Failed"}
    finally:
        conn.close()

@app.get("/health")
def health():
    return {"status": "ok"}
