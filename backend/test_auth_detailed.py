import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_detailed_auth_test():
    """
    Executa um teste detalhado da função authenticate_user() para diagnosticar erros.
    Captura e exibe o tipo exato da exceção, mensagem e traceback completo.
    """
    logger.info("\n--- Iniciando teste DETALHADO da função authenticate_user() ---")

    # 1. Carregar variáveis de ambiente
    logger.info("Passo 1: Carregando variáveis de ambiente do .env...")
    load_dotenv()
    logger.info("Variáveis de ambiente carregadas.")

    # Adiciona o diretório raiz do projeto ao sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    logger.info(f"sys.path ajustado para incluir: {project_root}")

    # 2. Importar a função authenticate_user
    logger.info("Passo 2: Tentando importar 'authenticate_user' de 'app.auth.auth_service'...")
    try:
        from app.auth.auth_service import authenticate_user
        logger.info("Função 'authenticate_user' importada com sucesso.")
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        logger.error("Verifique se o arquivo 'app/auth/auth_service.py' existe e está no caminho correto.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro inesperado ao importar 'authenticate_user': {e}", exc_info=True)
        sys.exit(1)

    # 3. Solicitar credenciais ao usuário
    print("\n--- Credenciais para Teste ---")
    test_email = input("Por favor, digite o email do usuário para teste: ")
    test_password = input("Por favor, digite a senha do usuário para teste: ")

    if not test_email or not test_password:
        logger.warning("Email ou senha não fornecidos. Encerrando teste.")
        return

    # 4. Executar o teste de autenticação e capturar qualquer exceção
    logger.info(f"\nPasso 3: Chamando authenticate_user() para o email: {test_email}")
    try:
        user_data = authenticate_user(test_email, test_password)

        # 5. Exibir os dados do usuário se for um sucesso
        logger.info("✅ authenticate_user() executada com sucesso!")
        logger.info("Dados do usuário autenticado:")
        for key, value in user_data.items():
            logger.info(f"  {key}: {value}")

    except Exception as e:
        # 4. Capturar QUALQUER exceção e exibir detalhes
        logger.error(f"❌ Ocorreu uma exceção durante a autenticação!")
        logger.error(f"Tipo da exceção: {type(e).__name__}")
        logger.error(f"Mensagem da exceção: {e}")
        logger.error("Traceback completo:")
        traceback.print_exc(file=sys.stderr)
        logger.error("Isso indica um problema na função authenticate_user() ou na comunicação com o Supabase.")

    logger.info("\n--- Teste DETALHADO da função authenticate_user() concluído ---")

if __name__ == "__main__":
    run_detailed_auth_test()