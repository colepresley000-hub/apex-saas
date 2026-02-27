"""
AUTHENTICATION SYSTEM
User signup, login, JWT tokens, password hashing
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3
from typing import Optional

# Security
SECRET_KEY = "your-secret-key-change-in-production"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthManager:
    def __init__(self, db_path="apex_users.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize users database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                plan TEXT DEFAULT 'starter',
                api_key TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict):
        """Create JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str):
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def create_user(self, email: str, password: str, full_name: str = None):
        """Create new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            hashed_pwd = self.hash_password(password)
            
            import secrets
            api_key = f"apex_{secrets.token_urlsafe(32)}"
            
            cursor.execute("""
                INSERT INTO users (email, hashed_password, full_name, api_key)
                VALUES (?, ?, ?, ?)
            """, (email, hashed_pwd, full_name, api_key))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                'user_id': user_id,
                'email': email,
                'api_key': api_key
            }
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, hashed_password, full_name, plan, api_key
            FROM users
            WHERE email = ? AND is_active = 1
        """, (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return None
        
        if not self.verify_password(password, user[2]):
            return None
        
        return {
            'user_id': user[0],
            'email': user[1],
            'full_name': user[3],
            'plan': user[4],
            'api_key': user[5]
        }
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, full_name, plan, api_key
            FROM users
            WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'user_id': user[0],
                'email': user[1],
                'full_name': user[2],
                'plan': user[3],
                'api_key': user[4]
            }
        return None

# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    
    auth_manager = AuthManager()
    payload = auth_manager.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id = payload.get("sub")
    user = auth_manager.get_user_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
