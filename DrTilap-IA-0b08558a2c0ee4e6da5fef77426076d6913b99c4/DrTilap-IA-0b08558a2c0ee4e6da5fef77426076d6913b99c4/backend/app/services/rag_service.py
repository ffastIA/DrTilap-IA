import os
import logging
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGService")


class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore_path = "vectorstore_faiss"
        self.docs_path = "docs/"
        self._vectorstore = None

    def _load_vectorstore(self):
        if os.path.exists(os.path.join(self.vectorstore_path, "index.faiss")):
            return FAISS.load_local(self.vectorstore_path, self.embeddings, allow_dangerous_deserialization=True)

        if not os.path.exists(self.docs_path): os.makedirs(self.docs_path)
        loader = DirectoryLoader(self.docs_path, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        if not documents: return None

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        vectorstore.save_local(self.vectorstore_path)
        return vectorstore

    async def get_response(self, question, chat_history):
        if self._vectorstore is None: self._vectorstore = self._load_vectorstore()
        if self._vectorstore is None: return {"answer": "Adicione PDFs em /docs.", "sources": []}

        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model="gpt-4-turbo", temperature=0),
            retriever=self._vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        result = chain.invoke({"question": question, "chat_history": chat_history})
        return {"answer": result["answer"],
                "sources": [doc.metadata.get("source") for doc in result["source_documents"]]}


rag_service = RAGService()