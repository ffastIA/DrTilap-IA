import os
from app.database import supabase
from postgrest.exceptions import APIError


def validar_conexao():
    print("🔍 Iniciando validação de conexão...")

    # 1. Verificar se as variáveis foram carregadas
    url = os.environ.get("SUPABASE_URL")
    if url:
        print(f"✅ SUPABASE_URL encontrada: {url[:20]}...")
    else:
        print("❌ Erro: SUPABASE_URL não encontrada no ambiente.")
        return

    # 2. Testar chamada simples ao banco de dados
    try:
        # Tenta listar as tabelas ou fazer um select simples na tabela 'users'
        # (Ajuste o nome da tabela se necessário)
        response = supabase.table("users").select("count", count="exact").limit(1).execute()
        print("✅ Conexão com o Banco de Dados: OK")
        print(f"📊 Total de usuários registrados: {response.count}")

    except APIError as e:
        print(f"❌ Erro de API do Supabase: {e.message}")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    validar_conexao()