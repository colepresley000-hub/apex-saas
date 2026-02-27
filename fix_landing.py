# Read current main.py
with open('main.py', 'r') as f:
    content = f.read()

# Find and replace the landing page HTML
landing_start = content.find('@app.get("/")')
landing_end = content.find('@app.get("/activate")')

original_mobile_html = '''@app.get("/")
def landing():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Apex Swarm</title><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#0a0e1a;color:white;padding-bottom:80px}
.container{max-width:480px;margin:0 auto;padding:20px}
.status-badge{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:20px;font-size:0.75rem;font-weight:600;color:#60a5fa;margin:20px 0}
.status-dot{width:8px;height:8px;background:#3b82f6;border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
h1{font-size:clamp(2.2rem,9vw,3.5rem);font-weight:900;line-height:1.1;margin:20px 0}
.highlight{background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
p{font-size:clamp(1rem,3vw,1.1rem);color:rgba(255,255,255,0.7);line-height:1.6;margin:20px 0}
.cta{width:100%;padding:18px;background:linear-gradient(135deg,#3b82f6,#2563eb);border:none;border-radius:12px;font-size:1.1rem;font-weight:700;color:white;cursor:pointer;margin:30px 0;display:block;text-align:center;text-decoration:none}
.stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:40px 0}
.stat-card{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:24px}
.stat-label{font-size:0.75rem;color:rgba(255,255,255,0.5);margin-bottom:12px;letter-spacing:1px}
.stat-value{font-size:2.5rem;font-weight:900;color:#00ff88}
</style></head><body>
<div class="container">
<div style="text-align:center"><div class="status-badge"><span class="status-dot"></span>SYSTEM ONLINE: V4.2.0</div></div>
<h1 style="text-align:center">AI Agents That<br>Make Money <span class="highlight">While<br>You Sleep</span></h1>
<p style="text-align:center">Deploy trading swarms with collective intelligence. <strong>One learns, all profit.</strong></p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" class="cta">Deploy Your Swarm → $299/mo</a>
<div class="stats-grid">
<div class="stat-card"><div class="stat-label">ACTIVE AGENTS</div><div class="stat-value">126</div></div>
<div class="stat-card"><div class="stat-label">ACTIONS EXECUTED</div><div class="stat-value">29,497</div></div>
<div class="stat-card"><div class="stat-label">30D USER PROFIT</div><div class="stat-value">$847K</div></div>
<div class="stat-card"><div class="stat-label">SUCCESS RATE</div><div class="stat-value">98.7%</div></div>
</div>
<p style="text-align:center;font-size:0.9rem;color:#666;margin-top:20px">🚀 Launch Special: 50% off with code LAUNCH50</p>
</div></body></html>""")

'''

new_content = content[:landing_start] + original_mobile_html + content[landing_end:]

with open('main.py', 'w') as f:
    f.write(new_content)

print("✅ Fixed to match original mobile design!")
