import asyncio
import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- PASSO 1: CARREGAR AMBIENTE IMEDIATAMENTE ---
# Isso garante que a OPENAI_API_KEY esteja disponível antes de importar o serviço
basedir = Path(__file__).resolve().parent
env_path = basedir / '.env'
load_dotenv(dotenv_path=env_path)

# --- PASSO 2: AJUSTE DE PYTHONPATH E IMPORTAÇÃO ---
# Garante que o Python encontre a pasta 'app' mesmo rodando de diretórios diferentes
if str(basedir) not in sys.path:
    sys.path.append(str(basedir))

try:
    from app.services.rag_service import rag_service
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestRAG")


async def testar_rag():
    print("\n" + "=" * 50)
    print("🔍 INICIANDO VALIDAÇÃO DO SERVIÇO RAG")
    print("=" * 50)

    # Verificação rápida da chave
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
        return
    print(f"✅ Chave OpenAI carregada: {api_key[:8]}...")

    # Pergunta baseada no contexto do projeto Dr. Tilápia
    pergunta = "Como funciona o sistema de monitoramento do Dr. Tilápia?"
    historico = []

    print(f"\n❓ Pergunta: {pergunta}")
    print("⏳ Aguardando resposta da IA...")

    try:
        resultado = await rag_service.get_response(pergunta, historico)

        print("\n✅ RESPOSTA GERADA:")
        print("-" * 30)
        print(resultado["answer"])
        print("-" * 30)

        print("\n📚 FONTES UTILIZADAS:")
        if resultado["sources"]:
            for source in resultado["sources"]:
                # Exibe apenas o nome do arquivo para limpeza visual
                print(f"  • {Path(source).name}")
        else:
            print("  ⚠️ Nenhuma fonte encontrada. Verifique se há PDFs em 'backend/docs/'.")

    except Exception as e:
        print(f"❌ ERRO DURANTE A EXECUÇÃO: {str(e)}")


if __name__ == "__main__":
    # Executa o loop de eventos assíncronos
    asyncio.run(testar_rag())