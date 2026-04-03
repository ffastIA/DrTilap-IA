import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configuração de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_simulated_login_test():
    """
    Simula uma requisição POST para /auth/login e testa a função authenticate_user()
    com os dados que o backend receberia.
    """
    logger.info("\n--- Iniciando teste de simulação de requisição de login ---")

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

    # 3. Simular uma requisição POST com email e password
    print("\n--- Dados da Requisição Simulada ---")
    simulated_email = input("Por favor, digite o email para a requisição simulada: ")
    simulated_password = input("Por favor, digite a senha para a requisição simulada: ")

    if not simulated_email or not simulated_password:
        logger.warning("Email ou senha não fornecidos. Encerrando teste.")
        return

    logger.info(f"\nPasso 3: Simulando requisição POST para /auth/login com:")
    logger.info(f"  Email: {simulated_email}")
    logger.info(f"  Senha: (não exibida por segurança)")

    # 4. Chamar authenticate_user() com os MESMOS dados que o backend receberia
    logger.info(f"\nPasso 4: Chamando authenticate_user() com os dados simulados...")
    try:
        user_data = authenticate_user(simulated_email, simulated_password)

        # 5. Exibir o resultado (sucesso)
        logger.info("✅ authenticate_user() executada com sucesso com dados simulados!")
        logger.info("Dados do usuário autenticado:")
        for key, value in user_data.items():
            logger.info(f"  {key}: {value}")

    except Exception as e:
        # 5. Exibir o resultado (erro detalhado)
        logger.error(f"❌ Ocorreu uma exceção durante a autenticação com dados simulados!")
        logger.error(f"Tipo da exceção: {type(e).__name__}")
        logger.error(f"Mensagem da exceção: {e}")
        logger.error("Traceback completo:")
        traceback.print_exc(file=sys.stderr)
        logger.error("Isso indica um problema na função authenticate_user() ou na comunicação com o Supabase.")

    logger.info("\n--- Teste de simulação de requisição de login concluído ---")

if __name__ == "__main__":
    run_simulated_login_test()