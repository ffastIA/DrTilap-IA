import os
import sys
import logging
from dotenv import load_dotenv

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- PRIMEIRA COISA: CARREGAR VARIÁVEIS DE AMBIENTE ---
load_dotenv()
logger.info("Variáveis de ambiente carregadas.")

# Adiciona o diretório ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importa a função authenticate_user APÓS carregar as variáveis de ambiente
try:
    from app.auth.auth_service import authenticate_user
    logger.info("Função 'authenticate_user' importada com sucesso.")
except ImportError as e:
    logger.error(f"Erro ao importar 'authenticate_user': {e}")
    logger.error("Verifique se o arquivo 'app/auth/auth_service.py' existe e está correto.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Erro inesperado ao importar 'authenticate_user': {e}", exc_info=True)
    sys.exit(1)

def run_authenticate_user_test():
    """
    Executa um teste direto da função authenticate_user() com credenciais fornecidas pelo usuário.
    """
    logger.info("\n--- Iniciando teste da função authenticate_user() ---")

    test_email = input("Por favor, digite o email do usuário para teste: ")
    test_password = input("Por favor, digite a senha do usuário para teste: ")

    if not test_email or not test_password:
        logger.warning("Email ou senha não fornecidos. Encerrando teste.")
        return

    try:
        logger.info(f"Chamando authenticate_user() para o email: {test_email}")
        user_data = authenticate_user(test_email, test_password)

        logger.info("✅ authenticate_user() executada com sucesso!")
        logger.info("Dados do usuário autenticado:")
        for key, value in user_data.items():
            logger.info(f"  {key}: {value}")

    except ValueError as e:
        logger.error(f"❌ Falha na autenticação (ValueError): {e}")
        logger.error("Isso geralmente indica credenciais inválidas ou problema de comunicação com o Supabase.")
    except Exception as e:
        logger.error(f"❌ Ocorreu um erro inesperado ao chamar authenticate_user(): {e}", exc_info=True)
        logger.error("Verifique o traceback acima para mais detalhes.")

    logger.info("--- Teste da função authenticate_user() concluído ---")

if __name__ == "__main__":
    run_authenticate_user_test()