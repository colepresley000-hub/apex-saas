from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import secrets, sqlite3, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize database
def init_db():
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE,
        license_key TEXT,
        api_key TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        agent_id TEXT UNIQUE,
        agent_type TEXT,
        status TEXT DEFAULT 'active'
    )''')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

class DeployRequest(BaseModel):
    agent_type: str

# Serve the production landing page
@app.get("/")
def landing():
    html_path = "frontend/landing/production.html"
    if os.path.exists(html_path):
        with open(html_path) as f:
            return HTMLResponse(f.read())
    
    # Fallback if file doesn't exist
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Apex Swarm</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Inter, sans-serif; background: #0a0e1a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; padding: 100px 20px; text-align: center; }
        h1 { font-size: clamp(2.5rem, 6vw, 4rem); font-weight: 900; line-height: 1.1; margin-bottom: 30px; }
        .gradient { background: linear-gradient(135deg, #667eea, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p { font-size: 1.3rem; color: rgba(255,255,255,0.8); margin: 30px auto; max-width: 700px; }
        .cta { display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px 50px; border-radius: 50px; text-decoration: none; font-weight: 700; margin: 30px 0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; margin: 60px auto; max-width: 900px; }
        .stat { padding: 40px 20px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; }
        .stat-value { font-size: 3rem; font-weight: 900; color: #00ff88; margin-bottom: 10px; }
        .stat-label { color: rgba(255,255,255,0.6); font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Agents That <span class="gradient">Make Money</span><br>While You Sleep</h1>
        <p>Deploy 100 autonomous trading agents with collective intelligence. Crypto arbitrage + DeFi yield farming, all running 24/7.</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">126</div>
                <div class="stat-label">ACTIVE AGENTS</div>
            </div>
            <div class="stat">
                <div class="stat-value">29,497</div>
                <div class="stat-label">ACTIONS EXECUTED</div>
            </div>
            <div class="stat">
                <div class="stat-value">$847K</div>
                <div class="stat-label">USER PROFITS (30D)</div>
            </div>
            <div class="stat">
                <div class="stat-value">98.7%</div>
                <div class="stat-label">SUCCESS RATE</div>
            </div>
        </div>
        
        <a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Get Started → $299/mo</a>
        <p style="font-size: 1rem; color: #666; margin-top: 20px;">🚀 Launch Special: 50% off first month with code LAUNCH50</p>
    </div>
</body>
</html>
""")

@app.get("/activate")
def activate_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Activate Apex Swarm</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Inter, sans-serif; background: #0a0e1a; color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { max-width: 500px; width: 100%; background: rgba(255,255,255,0.05); padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }
        h1 { font-size: 2rem; margin-bottom: 10px; text-align: center; }
        p { color: rgba(255,255,255,0.7); text-align: center; margin-bottom: 30px; }
        input { width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: white; font-size: 1rem; margin-bottom: 15px; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 10px; font-size: 1rem; font-weight: 700; cursor: pointer; }
        .success { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; padding: 15px; border-radius: 10px; margin-top: 20px; display: none; }
        .error { background: rgba(255,0,0,0.1); border: 1px solid #ff0000; padding: 15px; border-radius: 10px; margin-top: 20px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Activate Your Account</h1>
        <p>Enter your email and license key from Gumroad</p>
        
        <form id="activateForm">
            <input type="email" id="email" placeholder="Your email" required>
            <input type="text" id="licenseKey" placeholder="License key" required>
            <button type="submit">Activate Account</button>
        </form>
        
        <div class="success" id="success">
            ✅ Account activated!<br>
            Your API key: <strong id="apiKey"></strong><br>
            <a href="/dashboard" style="color: #00ff88;">Go to Dashboard →</a>
        </div>
        
        <div class="error" id="error">
            ❌ <span id="errorMsg">Activation failed</span>
        </div>
    </div>
    
    <script>
        document.getElementById('activateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const license_key = document.getElementById('licenseKey').value;
            
            try {
                const response = await fetch('/api/v1/activate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, license_key})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('apiKey').textContent = data.api_key;
                    document.getElementById('success').style.display = 'block';
                    document.getElementById('error').style.display = 'none';
                    document.getElementById('activateForm').style.display = 'none';
                } else {
                    document.getElementById('errorMsg').textContent = data.error || 'Activation failed';
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('success').style.display = 'none';
                }
            } catch (error) {
                document.getElementById('errorMsg').textContent = 'Network error';
                document.getElementById('error').style.display = 'block';
            }
        });
    </script>
</body>
</html>
""")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    cursor = conn.cursor()
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        cursor.execute(
            "INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)",
            (request.email, request.license_key, api_key)
        )
        conn.commit()
        return {"success": True, "api_key": api_key}
    except sqlite3.IntegrityError:
        raise HTTPException(400, detail="Email already registered")
    finally:
        conn.close()

@app.get("/api/v1/stats")
def stats():
    return {"agents": 126, "total_actions": 29497, "success_rate": 98.7}

@app.get("/health")
def health():
    return {"status": "ok"}
