import reflex as rx
import httpx
import logging
from typing import List, Tuple

BACKEND_URL = "http://localhost:8080"
logger = logging.getLogger(__name__)

class State(rx.State):
    user_email: str = ""
    password: str = ""
    user_name: str = "Usuário"
    user_role: str = rx.LocalStorage("user")
    access_token: str = rx.LocalStorage("")
    is_authenticated: bool = False
    current_message: str = ""
    chat_history: List[Tuple[str, str]] = []
    is_loading: bool = False
    error_message: str = ""

    # Setters explícitos para evitar DeprecationWarnings
    def set_user_email(self, val: str): self.user_email = val
    def set_password(self, val: str): self.password = val
    def set_current_message(self, val: str): self.current_message = val

    def check_login(self):
        if not self.access_token: return rx.redirect("/login")
        self.is_authenticated = True

    def logout(self):
        self.access_token = ""
        self.is_authenticated = False
        self.user_role = "user"
        return rx.redirect("/")

    async def handle_login(self):
        self.is_loading = True
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{BACKEND_URL}/auth/login", json={"email": self.user_email, "password": self.password})
                if res.status_code == 200:
                    data = res.json()
                    self.access_token = data["access_token"]
                    self.user_name = data["user_name"]
                    self.user_role = data["user_role"]
                    return rx.redirect("/hub")
                self.error_message = "Credenciais inválidas."
        except: self.error_message = "Erro de conexão."
        finally: self.is_loading = False

    async def handle_chat(self):
        """Método que estava faltando ou com erro de referência."""
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
            self.chat_history[-1] = (msg, "Erro na conexão com a IA.")
        finally: self.is_loading = False

    async def handle_upload(self, files: List[rx.UploadFile]):
        self.is_loading = True
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                for file in files:
                    content = await file.read()
                    await client.post(f"{BACKEND_URL}/admin/upload", files={"file": (file.filename, content)}, headers=headers)
            return [rx.window_alert("Upload concluído!"), rx.clear_selected_files("upload_manual")]
        except: return rx.window_alert("Falha no upload.")
        finally: self.is_loading = False

    async def handle_reindex(self):
        self.is_loading = True
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                await client.post(f"{BACKEND_URL}/admin/reindex", headers=headers)
            return rx.window_alert("Reindexado!")
        except: pass
        finally: self.is_loading = False