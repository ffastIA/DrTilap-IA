import asyncio
import httpx
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
BASE_URL = "http://localhost:8080"

# Carrega ambiente para pegar credenciais de teste se existirem
basedir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=basedir / ".env")

# ⚠️ AJUSTE ESTAS CREDENCIAIS COM UM DOS 3 USUÁRIOS DO SEU SUPABASE
TEST_EMAIL = os.environ.get("TEST_USER_EMAIL", "ffasti01@gmail.com")
TEST_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "123456")


async def run_integration_test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n" + "=" * 60)
        print("🚀 INICIANDO TESTE DE INTEGRAÇÃO - DR. TILÁPIA 2.0")
        print("=" * 60)

        # 1. Teste de Health Check
        print("\n[1/3] Verificando integridade da API (/health)...")
        try:
            res_health = await client.get(f"{BASE_URL}/health")
            if res_health.status_code == 200:
                print(f"✅ API Online: {res_health.json()}")
            else:
                print(f"❌ API Offline ou erro: {res_health.status_code}")
                return
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return

        # 2. Teste de Login
        print(f"\n[2/3] Tentando autenticação para: {TEST_EMAIL}...")
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        res_login = await client.post(f"{BASE_URL}/auth/login", json=login_data)

        if res_login.status_code == 200:
            auth_data = res_login.json()
            token = auth_data.get("access_token")
            user_name = auth_data.get("user_name")
            print(f"✅ Login bem-sucedido! Bem-vindo, {user_name}.")
            print(f"🔑 Token JWT obtido (parcial): {token[:20]}...")
        else:
            print(f"❌ Falha no login ({res_login.status_code}): {res_login.json().get('detail')}")
            return

        # 3. Teste de Chat RAG (Protegido)
        print("\n[3/3] Enviando pergunta técnica ao Consultor IA (/consultoria/chat)...")
        headers = {"Authorization": f"Bearer {token}"}
        chat_data = {
            "message": "Qual a temperatura ideal para a criação de tilápias?",
            "history": []
        }

        try:
            res_chat = await client.post(
                f"{BASE_URL}/consultoria/chat",
                json=chat_data,
                headers=headers
            )

            if res_chat.status_code == 200:
                answer = res_chat.json()
                print("\n✅ RESPOSTA DA IA RECEBIDA:")
                print("-" * 40)
                print(answer.get("answer"))
                print("-" * 40)
                print("\n📚 Fontes:")
                for src in answer.get("sources", []):
                    print(f"  - {Path(src).name}")
            else:
                print(f"❌ Erro no Chat ({res_chat.status_code}): {res_chat.json().get('detail')}")
        except Exception as e:
            print(f"❌ Erro durante a consulta RAG: {e}")

        print("\n" + "=" * 60)
        print("🏁 TESTE DE INTEGRAÇÃO FINALIZADO")
        print("=" * 60)


if __name__ == "__main__":
    if TEST_EMAIL == "seu_email@exemplo.com":
        print("⚠️  AVISO: Edite o arquivo test_integration.py com um e-mail/senha válidos do seu Supabase.")
    else:
        asyncio.run(run_integration_test())