import reflex as rx
import httpx
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)
BACKEND_URL = "http://localhost:8080"


class State(rx.State):
    """Estado global do DrTilápia 1.3."""

    # --- AUTENTICAÇÃO ---
    user_email: str = ""
    user_name: str = ""
    access_token: str = ""
    is_authenticated: bool = False

    # --- CHAT RAG ---
    current_message: str = ""
    chat_history: List[Tuple[str, str]] = []
    is_loading: bool = False
    error_message: str = ""

    # --- MÉTRICAS ---
    temperatura: float = 26.5
    oxigenio: float = 7.2
    ph: float = 6.8
    amonia: float = 0.5
    loading_metrics: bool = False

    # --- SETTERS ---
    def set_user_email(self, email: str):
        self.user_email = email

    def set_current_message(self, msg: str):
        self.current_message = msg

    def set_password(self, password: str):
        self.current_message = password

    # --- PROTEÇÃO DE ROTAS ---
    def check_login(self):
        """Redireciona se não autenticado."""
        if not self.is_authenticated:
            return rx.redirect("/login")

    def logout(self):
        """Realiza logout."""
        self.user_email = ""
        self.user_name = ""
        self.access_token = ""
        self.is_authenticated = False
        self.chat_history = []
        self.error_message = ""
        self.current_message = ""
        return rx.redirect("/login")

    # --- LOGIN ---
    async def handle_login(self):
        """Realiza login com validação."""
        if not self.user_email or not self.current_message:
            self.error_message = "Preencha todos os campos."
            return

        self.is_loading = True
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": self.user_email, "password": self.current_message},
                    timeout=10.0
                )

                if res.status_code == 200:
                    data = res.json()
                    # CRÍTICO: Atualizar estado ANTES de redirecionar
                    self.access_token = data.get("access_token", "")
                    self.user_name = data.get("user_name", "")
                    self.is_authenticated = True  # Marcar como autenticado
                    self.error_message = ""
                    self.current_message = ""
                    logger.info(f"Login bem-sucedido para: {self.user_email}")
                    # Redirecionar após atualizar estado
                    return rx.redirect("/hub")
                else:
                    error_detail = res.json().get("detail", "Erro ao fazer login")
                    self.error_message = error_detail
                    logger.warning(f"Falha no login: {error_detail}")
        except Exception as e:
            self.error_message = f"Erro de conexão: {str(e)}"
            logger.error(f"Erro no login: {e}")
        finally:
            self.is_loading = False

    # --- CHAT RAG ---
    async def handle_chat_message(self):
        """Envia mensagem para RAG."""
        if not self.current_message.strip():
            return

        question = self.current_message
        self.chat_history.append((question, "Pensando..."))
        self.current_message = ""
        self.is_loading = True

        yield

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/consultoria/chat",
                    json={
                        "message": question,
                        "history": self.chat_history[:-1]
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "Sem resposta.")
                    self.chat_history[-1] = (question, answer)
                else:
                    self.chat_history[-1] = (question, "Erro ao processar.")
        except Exception as e:
            self.chat_history[-1] = (question, f"Erro: {str(e)}")
        finally:
            self.is_loading = False

    # --- MÉTRICAS ---
    async def fetch_metrics(self):
        """Busca métricas do backend."""
        self.loading_metrics = True
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{BACKEND_URL}/metrics/latest",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )

                if response.status_code == 200:
                    data = response.json()
                    self.temperatura = data.get("temperatura", 26.5)
                    self.oxigenio = data.get("oxigenio", 7.2)
                    self.ph = data.get("ph", 6.8)
                    self.amonia = data.get("amonia", 0.5)
        except Exception as e:
            logger.error(f"Erro ao buscar métricas: {e}")
        finally:
            self.loading_metrics = False