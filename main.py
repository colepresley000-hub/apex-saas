from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import secrets, sqlite3

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def init_db():
    conn = sqlite3.connect('apex.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, license_key TEXT, api_key TEXT UNIQUE)')
    conn.commit()
    conn.close()

init_db()

class ActivateRequest(BaseModel):
    email: EmailStr
    license_key: str

@app.get("/")
def root():
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>APEX SWARM</title></head>
<body style="font-family:Arial;background:#0a0e1a;color:white;padding:50px;text-align:center">
<h1>APEX SWARM</h1>
<p>AI Agents That Make Money While You Sleep</p>
<a href="https://colepresley.gumroad.com/l/apex-swarm" style="background:#667eea;color:white;padding:15px 30px;border-radius:50px;text-decoration:none;display:inline-block;margin:20px">Get Started - $299/mo</a>
</body></html>""")

@app.post("/api/v1/activate")
def activate(request: ActivateRequest):
    conn = sqlite3.connect('apex.db')
    try:
        api_key = f"apex_{secrets.token_urlsafe(32)}"
        c = conn.cursor()
        c.execute("INSERT INTO users (email, license_key, api_key) VALUES (?, ?, ?)", 
                  (request.email, request.license_key, api_key))
        conn.commit()
        return {"success": True, "api_key": api_key}
    except:
        return {"success": False}
    finally:
        conn.close()

@app.get("/health")
def health():
    return {"status": "ok"}
