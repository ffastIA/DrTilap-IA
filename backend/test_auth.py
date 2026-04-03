import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_auth_test():
    """
    Executa uma série de testes para diagnosticar problemas de autenticação com o Supabase.
    Verifica variáveis de ambiente, conexão e tenta um login.
    """
    logger.info("Iniciando teste de autenticação do Supabase...")

    # 1. Carregar variáveis de ambiente
    load_dotenv()

    supabase_url: str = os.environ.get("SUPABASE_URL")
    supabase_key: str = os.environ.get("SUPABASE_KEY")

    # 2. Exibir as credenciais carregadas (mascaradas por segurança)
    logger.info(f"SUPABASE_URL carregada: {supabase_url is not None}")
    logger.info(f"SUPABASE_KEY carregada: {supabase_key is not None}")

    if not supabase_url or not supabase_key:
        logger.error("Erro: SUPABASE_URL ou SUPABASE_KEY não encontradas no arquivo .env.")
        logger.error("Certifique-se de que o arquivo .env está na raiz do diretório 'backend' e contém as chaves.")
        sys.exit(1)

    # 3. Testar a conexão com Supabase
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Cliente Supabase criado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar cliente Supabase: {e}")
        sys.exit(1)

    # Teste de conexão básica
    try:
        response = supabase.from_('users').select('id').limit(1).execute()
        logger.info(f"Conexão básica com Supabase bem-sucedida.")
    except Exception as e:
        logger.error(f"Erro ao realizar consulta de teste no Supabase: {e}")
        logger.error("Verifique se a SUPABASE_URL e SUPABASE_KEY estão corretas.")
        sys.exit(1)

    logger.info("Conexão com Supabase verificada com sucesso.")

    # 4. Tentar fazer login com credenciais de teste
    print("\n--- Teste de Login ---")
    test_email = input("Por favor, digite o email do usuário para teste de login: ")
    test_password = input("Por favor, digite a senha do usuário para teste de login: ")

    if not test_email or not test_password:
        logger.warning("Email ou senha não fornecidos. Pulando teste de login.")
        return

    try:
        logger.info(f"Tentando login para o email: {test_email}")
        auth_response = supabase.auth.sign_in_with_password({
            "email": test_email,
            "password": test_password
        })

        # 5. Exibir o resultado completo do login
        if auth_response.user:
            logger.info("✅ Login bem-sucedido!")
            logger.info(f"ID do Usuário: {auth_response.user.id}")
            logger.info(f"Email do Usuário: {auth_response.user.email}")
            logger.info(
                f"Nome Completo (metadata): {auth_response.user.user_metadata.get('full_name', 'N/A') if auth_response.user.user_metadata else 'N/A'}")
            logger.info(f"Access Token (primeiros 20 caracteres): {auth_response.session.access_token[:20]}...")
            logger.info("Login funcionando corretamente!")
        else:
            logger.error("❌ Login falhou. Nenhuma informação de usuário na resposta.")

    except Exception as e:
        logger.error(f"❌ Erro durante a tentativa de login: {e}")
        logger.error(
            "Verifique se o email e a senha estão corretos e se o usuário existe e está confirmado no Supabase.")
        logger.error(f"Tipo de erro: {type(e).__name__}")

    logger.info("Teste de autenticação concluído.")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    run_auth_test()