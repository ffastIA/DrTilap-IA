import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from passlib.context import CryptContext

# --- CONFIGURAÇÃO DE AMBIENTE ---
basedir = Path(__file__).resolve().parent
env_path = basedir / '.env'
load_dotenv(dotenv_path=env_path)

# Configuração do Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SetupUser")


def sync_test_user():
    email = "ffasti01@gmail.com"
    password = "123456"  # ⚠️ Use a mesma senha do seu test_integration.py
    hashed_password = pwd_context.hash(password)

    print(f"\n🚀 Sincronizando usuário no Supabase (Tabela Public): {email}")

    try:
        # Verifica se o usuário existe
        res = supabase.table("users").select("id").eq("email", email).execute()

        # Mapeamento EXATO conforme o seu JSON de public.users
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": "Fabio Ffasti"
        }

        if res.data:
            print("🔄 Usuário encontrado. Atualizando 'hashed_password'...")
            supabase.table("users").update(user_data).eq("email", email).execute()
            print("✅ Sucesso: Hash de senha e nome atualizados.")
        else:
            print("🆕 Usuário não encontrado. Criando novo registro...")
            supabase.table("users").insert(user_data).execute()
            print("✅ Sucesso: Usuário criado com sucesso.")

        print(f"\n👉 Senha para o teste: '{password}'")

    except Exception as e:
        print(f"❌ Erro ao acessar Supabase: {e}")


if __name__ == "__main__":
    sync_test_user()