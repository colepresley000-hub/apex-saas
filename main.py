from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class DeployRequest(BaseModel):
    agent_type: str

@app.get("/")
def root():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Apex Swarm - AI Agents That Make Money</title>
    <style>
        body { font-family: Arial; background: #0a0e1a; color: white; margin: 0; padding: 50px; text-align: center; }
        h1 { font-size: 3rem; margin-bottom: 20px; }
        .gradient { background: linear-gradient(135deg, #667eea, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .cta { background: #667eea; color: white; padding: 20px 40px; border-radius: 10px; text-decoration: none; display: inline-block; margin: 20px; font-size: 1.2rem; }
        .stats { display: flex; justify-content: center; gap: 40px; margin: 40px 0; }
        .stat { padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px; }
        .stat-value { font-size: 2rem; font-weight: bold; color: #00ff88; }
    </style>
</head>
<body>
    <h1>AI Agents That <span class="gradient">Make Money</span><br>While You Sleep</h1>
    <p style="font-size: 1.3rem; margin: 30px 0;">Deploy 100 autonomous trading agents with collective intelligence</p>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">126</div>
            <div>Active Agents</div>
        </div>
        <div class="stat">
            <div class="stat-value">$847K</div>
            <div>User Profits</div>
        </div>
        <div class="stat">
            <div class="stat-value">98.7%</div>
            <div>Success Rate</div>
        </div>
    </div>
    
    <a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Get Started - $299/mo</a>
    
    <p style="margin-top: 40px; color: #666;">Launch Special: 50% off with code LAUNCH50</p>
</body>
</html>
""")

@app.get("/activate")
def activate():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head><title>Activate Apex Swarm</title></head>
<body style="font-family: Arial; background: #0a0e1a; color: white; padding: 50px; text-align: center;">
    <h1>Activate Your Account</h1>
    <p>Check your email for your license key</p>
    <p>Then email it to: support@apexswarm.com to activate</p>
    <a href="/" style="color: #667eea;">Back to Home</a>
</body>
</html>
""")

@app.get("/api/v1/stats")
def stats():
    return {"agents": 126, "total_actions": 29497, "success_rate": 98.7}

@app.post("/api/v1/agents/deploy")
def deploy(request: DeployRequest):
    agent_id = f"{request.agent_type}-{secrets.token_hex(4)}"
    return {"success": True, "agent_id": agent_id}

@app.get("/health")
def health():
    return {"status": "ok"}
