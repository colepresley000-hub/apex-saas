with open('main.py', 'r') as f:
    content = f.read()

landing_start = content.find('@app.get("/")')
landing_end = content.find('@app.get("/activate")')

responsive_landing = '''@app.get("/")
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

'''

new_content = content[:landing_start] + responsive_landing + content[landing_end:]

with open('main.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed! Now responsive for desktop & mobile!")
