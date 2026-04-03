import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain

# --- CONFIGURAÇÃO DE AMBIENTE (ROBUSTA) ---
# Resolve o caminho do .env subindo 3 níveis (services -> app -> backend -> .env)
basedir = Path(__file__).resolve().parent.parent.parent
env_path = basedir / '.env'
load_dotenv(dotenv_path=env_path)

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGService")


class RAGService:
    def __init__(self):
        # Agora o ambiente já está carregado, evitando o erro de api_key
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore_path = str(basedir / "vectorstore_faiss")
        self.docs_path = str(basedir / "docs")
        self._vectorstore = None

    def _load_vectorstore(self):
        """Carrega o FAISS local ou cria um novo a partir dos PDFs."""
        index_file = Path(self.vectorstore_path) / "index.faiss"

        if index_file.exists():
            logger.info(f"Carregando VectorStore existente em: {self.vectorstore_path}")
            return FAISS.load_local(
                self.vectorstore_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

        logger.info("Criando novo VectorStore a partir dos documentos em /docs...")
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)

        loader = DirectoryLoader(self.docs_path, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        if not documents:
            logger.warning(f"Nenhum documento encontrado em {self.docs_path}.")
            return None

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        return vectorstore

    async def get_response(self, question: str, chat_history: list):
        """Gera resposta baseada nos documentos e histórico."""
        if self._vectorstore is None:
            self._vectorstore = self._load_vectorstore()

        if self._vectorstore is None:
            return {
                "answer": "A base de conhecimento está vazia. Adicione PDFs na pasta /docs.",
                "sources": []
            }

        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4-turbo", temperature=0),
            retriever=self._vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )

        # LangChain invoke espera o dicionário com as chaves corretas
        result = chain.invoke({"question": question, "chat_history": chat_history})

        # Extração única das fontes
        sources = list(set([doc.metadata.get("source") for doc in result["source_documents"]]))

        return {
            "answer": result["answer"],
            "sources": sources
        }


# Instância global para o projeto
rag_service = RAGService()