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
