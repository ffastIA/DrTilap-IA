import logging
import os
import shutil
from pathlib import Path
from typing import List
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# --- CONFIGURAÇÃO ---
basedir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=basedir / '.env')

from app.auth.auth_service import ALGORITHM, SECRET_KEY, create_access_token, verify_password
from app.database import supabase
from app.services.rag_service import rag_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DrTilapia_API")

app = FastAPI(title="Dr. Tilápia 2.0 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str
    history: List[List[str]] = []


security = HTTPBearer()


def verify_token(credentials=Depends(security)):
    token = credentials.credentials
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Token inválido")


# --- ENDPOINTS ---

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    res = supabase.table("users").select("email, hashed_password, full_name, role").eq("email",
                                                                                       credentials.email).execute()
    if not res.data or not verify_password(credentials.password, res.data[0].get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    user = res.data[0]
    token = create_access_token(data={"sub": user["email"], "role": user.get("role", "user")})
    return {
        "access_token": token,
        "user_name": user.get("full_name"),
        "user_role": user.get("role", "user")
    }


@app.post("/consultoria/chat")
async def chat(req: ChatRequest, token: dict = Depends(verify_token)):
    return await rag_service.get_response(req.message, [tuple(h) for h in req.history])


@app.post("/admin/upload")
async def upload(file: UploadFile = File(...), token: dict = Depends(verify_token)):
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    file_path = docs_dir / file.filename.replace(" ", "_")
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Upload realizado"}


@app.post("/admin/reindex")
async def reindex(token: dict = Depends(verify_token)):
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    rag_service._vectorstore = None
    rag_service._load_vectorstore()
    return {"message": "Reindexado"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)