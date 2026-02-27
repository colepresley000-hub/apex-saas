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
    html = open('FINAL_LANDING_PAGE.html').read()
    return HTMLResponse(html)

@app.get("/activate")
def activate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Activate</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#0a0e1a;color:white;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.container{max-width:500px;width:100%;background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;border:1px solid rgba(255,255,255,0.1)}
h1{font-size:2rem;margin-bottom:10px;text-align:center}p{color:rgba(255,255,255,0.7);text-align:center;margin-bottom:30px}
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
if(data.success){localStorage.setItem('apex_api_key',data.api_key);document.getElementById('apiKey').textContent=data.api_key;
document.getElementById('success').style.display='block';document.getElementById('error').style.display='none';
document.getElementById('activateForm').style.display='none';}
else{document.getElementById('errorMsg').textContent=data.error||'Failed';document.getElementById('error').style.display='block';}}
catch(error){document.getElementById('errorMsg').textContent='Network error';document.getElementById('error').style.display='block';}});
</script></body></html>""")

@app.get("/dashboard")
def dashboard():
    return HTMLResponse("Dashboard - Coming soon")

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

@app.get("/health")
def health():
    return {"status": "ok"}
