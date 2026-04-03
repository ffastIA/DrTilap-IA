from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import os
import jwt

# Importações de módulos locais
from app.auth.auth_service import (
    verify_password,
    create_access_token,
    validar_email,
    SECRET_KEY,
    ALGORITHM
)
from app.database import supabase
from app.services.rag_service import rag_service

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Inicialização do FastAPI ---
app = FastAPI(
    title="Dr. Tilápia 1.3 API",
    description="API para o sistema de monitoramento e consultoria de piscicultura Dr. Tilápia.",
    version="1.3.0"
)

# --- Configuração CORS Restritiva ---
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuração de Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- Modelos Pydantic para Requisições ---
class LoginRequest(BaseModel):
    """Modelo para a requisição de login."""
    email: str
    password: str


class ChatRequest(BaseModel):
    """Modelo para a requisição de chat RAG."""
    message: str
    history: list = []


# --- Segurança JWT ---
security = HTTPBearer()


def verify_token(credentials=Depends(security)):
    """
    Verifica a validade de um token JWT fornecido no cabeçalho Authorization.

    Args:
        credentials: Credenciais HTTP do tipo Bearer.

    Returns:
        dict: O payload do token se for válido.

    Raises:
        HTTPException: Se o token for inválido ou expirado.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Tentativa de acesso com token expirado.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        logger.warning("Tentativa de acesso com token inválido.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Erro inesperado na verificação de token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Endpoints da API ---

@app.get("/health", summary="Verifica a saúde da API")
async def health_check():
    """
    Endpoint simples para verificar se a API está online e respondendo.
    """
    logger.info("Requisição /health recebida.")
    return {"status": "healthy", "version": app.version}


@app.post("/auth/login", summary="Autentica um usuário e retorna um token JWT")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    """
    Processa a autenticação do usuário.

    Args:
        request (Request): Objeto da requisição FastAPI (usado pelo rate limiter).
        credentials (LoginRequest): Email e senha do usuário.

    Returns:
        dict: Um token de acesso JWT e informações básicas do usuário.

    Raises:
        HTTPException: Se as credenciais forem inválidas, email malformado ou erro interno.
    """
    logger.info(f"Tentativa de login para o email: {credentials.email}")
    try:
        # 1. Validação do formato do email
        if not validar_email(credentials.email):
            logger.warning(f"Login falhou: Email inválido '{credentials.email}'.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de email inválido."
            )

        # 2. Buscar usuário no Supabase
        user_response = supabase.table("users").select("*").eq("email", credentials.email).execute()
        user_data = user_response.data

        if not user_data:
            logger.warning(f"Login falhou: Usuário não encontrado para '{credentials.email}'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas."
            )

        user = user_data[0]

        # 3. Verificar senha
        if not verify_password(credentials.password, user.get("password_hash", "")):
            logger.warning(f"Login falhou: Senha incorreta para '{credentials.email}'.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas."
            )

        # 4. Gerar token JWT
        access_token = create_access_token(data={"sub": credentials.email})

        logger.info(f"Login bem-sucedido para '{credentials.email}'.")
        return {
            "status": "success",
            "access_token": access_token,
            "token_type": "bearer",
            "user_email": credentials.email,
            "user_name": user.get("name", credentials.email.split("@")[0])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado durante o login para '{credentials.email}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao processar o login."
        )


@app.post("/consultoria/chat", summary="Envia uma mensagem para o serviço de consultoria IA (RAG)")
async def chat_consultoria(request: ChatRequest, token_payload: dict = Depends(verify_token)):
    """
    Processa uma requisição de chat com o serviço RAG. Requer autenticação JWT.

    Args:
        request (ChatRequest): Mensagem do usuário e histórico da conversa.
        token_payload (dict): Payload do token JWT verificado (injetado por Depends).

    Returns:
        dict: A resposta gerada pelo modelo RAG.

    Raises:
        HTTPException: Se a autenticação falhar ou ocorrer um erro no serviço RAG.
    """
    user_email = token_payload.get("sub", "desconhecido")
    logger.info(f"Requisição de chat de '{user_email}': '{request.message[:50]}...'")
    try:
        formatted_history = [tuple(item) for item in request.history]
        response = await rag_service.get_response(request.message, formatted_history)

        logger.info(f"Resposta RAG gerada para '{user_email}'.")
        return {"answer": response}
    except Exception as e:
        logger.error(f"Erro no serviço RAG para '{user_email}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar a consulta com a IA."
        )


@app.get("/metrics/latest", summary="Retorna as métricas mais recentes do sistema")
async def get_metrics(token_payload: dict = Depends(verify_token)):
    """
    Retorna as métricas mais recentes do sistema de monitoramento. Requer autenticação JWT.

    Args:
        token_payload (dict): Payload do token JWT verificado (injetado por Depends).

    Returns:
        dict: Dicionário contendo as métricas (temperatura, oxigênio, pH, amônia).

    Raises:
        HTTPException: Se a autenticação falhar ou ocorrer um erro na obtenção das métricas.
    """
    user_email = token_payload.get("sub", "desconhecido")
    logger.info(f"Requisição de métricas de '{user_email}'.")
    try:
        metrics_data = {
            "temperatura": 26.5,
            "oxigenio": 7.2,
            "ph": 6.8,
            "amonia": 0.5
        }
        logger.info(f"Métricas retornadas para '{user_email}'.")
        return metrics_data
    except Exception as e:
        logger.error(f"Erro ao obter métricas para '{user_email}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar as métricas do sistema."
        )