from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Swarm</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #0a0e1a; color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 20px; }
        h1 { font-size: 3rem; margin-bottom: 20px; text-align: center; }
        .gradient { background: linear-gradient(135deg, #667eea, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p { font-size: 1.3rem; margin: 20px 0; text-align: center; max-width: 600px; }
        .cta { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px 40px; border-radius: 12px; text-decoration: none; display: inline-block; margin: 30px; font-size: 1.2rem; font-weight: bold; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 40px 0; max-width: 800px; }
        .stat { padding: 30px; background: rgba(255,255,255,0.05); border-radius: 15px; text-align: center; }
        .stat-value { font-size: 2.5rem; font-weight: bold; color: #00ff88; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>AI Agents That <span class="gradient">Make Money</span> While You Sleep</h1>
    <p>Deploy 100 autonomous trading agents with collective intelligence. Crypto arbitrage + DeFi yield farming, all running 24/7.</p>
    
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
    
    <a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Get Started - $299/mo →</a>
    
    <p style="font-size: 1rem; color: #666; margin-top: 20px;">🚀 Launch Special: 50% off first month with code LAUNCH50</p>
</body>
</html>
""")
