import reflex as rx
import httpx
import logging
from typing import List, Tuple

# Configurações Globais
BACKEND_URL = "http://localhost:8080"
logger = logging.getLogger(__name__)

class State(rx.State):
    # --- VARIÁVEIS DE ESTADO ---
    user_email: str = ""
    password: str = ""
    user_name: str = "Usuário"
    access_token: str = rx.LocalStorage("")
    is_authenticated: bool = False
    current_message: str = ""
    chat_history: List[Tuple[str, str]] = []
    is_loading: bool = False
    error_message: str = ""

    # --- SETTERS EXPLÍCITOS (Resolve os DeprecationWarnings) ---
    def set_user_email(self, val: str): self.user_email = val
    def set_password(self, val: str): self.password = val
    def set_current_message(self, val: str): self.current_message = val

    # --- LÓGICA DE NAVEGAÇÃO ---
    def check_login(self):
        if not self.access_token:
            return rx.redirect("/login")
        self.is_authenticated = True

    def logout(self):
        self.access_token = ""
        self.is_authenticated = False
        return rx.redirect("/")

    # --- AÇÕES ASSÍNCRONAS ---
    async def handle_login(self):
        self.is_loading = True
        self.error_message = ""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": self.user_email, "password": self.password},
                    timeout=10.0
                )
                if res.status_code == 200:
                    data = res.json()
                    self.access_token = data["access_token"]
                    self.user_name = data["user_name"]
                    return rx.redirect("/hub")
                self.error_message = "E-mail ou senha incorretos."
        except Exception as e:
            self.error_message = "Erro de conexão com o servidor."
        finally:
            self.is_loading = False

    async def handle_chat(self):
        if not self.current_message: return
        msg = self.current_message
        self.chat_history.append((msg, ""))
        self.current_message = ""
        self.is_loading = True
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                res = await client.post(
                    f"{BACKEND_URL}/consultoria/chat",
                    json={"message": msg, "history": [list(p) for p in self.chat_history[:-1]]},
                    headers=headers, timeout=60.0
                )
                self.chat_history[-1] = (msg, res.json().get("answer", "Sem resposta."))
        except:
            self.chat_history[-1] = (msg, "Erro ao consultar IA.")
        finally:
            self.is_loading = False

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Upload de arquivos para o backend."""
        self.is_loading = True
        try:
            for file in files:
                upload_data = await file.read()
                async with httpx.AsyncClient() as client:
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    files_payload = {"file": (file.filename, upload_data, "application/pdf")}
                    await client.post(f"{BACKEND_URL}/admin/upload", files=files_payload, headers=headers)
            return rx.window_alert("Upload concluído!")
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
        finally:
            self.is_loading = False

    async def handle_reindex(self):
        self.is_loading = True
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with httpx.AsyncClient() as client:
                await client.post(f"{BACKEND_URL}/admin/reindex", headers=headers, timeout=120.0)
            return rx.window_alert("Base reindexada!")
        except:
            pass
        finally:
            self.is_loading = False