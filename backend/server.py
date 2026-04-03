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

# --- 1. CONFIGURAÇÃO DE AMBIENTE ---
basedir = Path(__file__).resolve().parent
env_path = basedir / '.env'
load_dotenv(dotenv_path=env_path)

# Importações de módulos locais com tratamento de erro robusto
try:
    from app.auth.auth_service import (
        ALGORITHM,
        SECRET_KEY,
        create_access_token,
        validar_email,
        verify_password,
    )
    from app.database import supabase
    from app.services.rag_service import rag_service
except ImportError as e:
    print(f"❌ Erro crítico de importação: {e}")
    # Definimos valores padrão para evitar que o app quebre no carregamento
    ALGORITHM = "HS256"
    SECRET_KEY = "fallback-key-if-env-fails"

# --- 2. LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DrTilapia_API")

# --- 3. INICIALIZAÇÃO DA API ---
# Este é o objeto 'app' que o Uvicorn procura
app = FastAPI(
    title="Dr. Tilápia 2.0 API",
    description="Backend oficial para monitoramento e consultoria técnica via RAG.",
    version="2.0.0"
)

# --- 4. CONFIGURAÇÃO DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em desenvolvimento, permitimos tudo para evitar bloqueios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. CONFIGURAÇÃO DE RATE LIMITING ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- 6. MODELOS DE DADOS ---
class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str
    history: List[List[str]] = []


# --- 7. SEGURANÇA ---
security = HTTPBearer()


def verify_token(credentials=Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )


# --- 8. ENDPOINTS ---

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}


@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    logger.info(f"Tentativa de login: {credentials.email}")
    try:
        res = supabase.table("users").select("email, hashed_password, full_name").eq("email",
                                                                                     credentials.email).execute()

        if not res.data or not verify_password(credentials.password, res.data[0].get("hashed_password", "")):
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = create_access_token(data={"sub": credentials.email})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_name": res.data[0].get("full_name") or credentials.email.split("@")[0]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")


@app.post("/consultoria/chat")
async def chat_consultoria(request: ChatRequest, token_payload: dict = Depends(verify_token)):
    try:
        formatted_history = [tuple(h) for h in request.history]
        return await rag_service.get_response(request.message, formatted_history)
    except Exception as e:
        logger.error(f"Erro no RAG: {e}")
        raise HTTPException(status_code=500, detail="Erro no processamento da IA")


@app.post("/admin/upload")
async def upload_document(file: UploadFile = File(...), token_payload: dict = Depends(verify_token)):
    try:
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        file_path = docs_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": f"Arquivo {file.filename} carregado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/reindex")
async def reindex_rag(token_payload: dict = Depends(verify_token)):
    try:
        rag_service._vectorstore = None
        rag_service._load_vectorstore()
        return {"message": "Base de conhecimento reindexada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 9. EXECUÇÃO ---
if __name__ == "__main__":
    import uvicorn

    # Execução direta via 'python main.py'
    uvicorn.run(app, host="0.0.0.0", port=8080)