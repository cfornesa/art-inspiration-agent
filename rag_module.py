import os
import logging
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from replit.object_storage import Client

logger = logging.getLogger(__name__)
storage = Client()
embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    mistral_api_key=os.environ["MISTRAL_API_KEY"]
)

vector_store = None

def _download_index():
    global vector_store
    try:
        os.makedirs("/tmp/art_index", exist_ok=True)
        faiss_bytes = storage.download_as_bytes("art_index/index.faiss")
        pkl_bytes   = storage.download_as_bytes("art_index/index.pkl")
        with open("/tmp/art_index/index.faiss", "wb") as f:
            f.write(faiss_bytes)
        with open("/tmp/art_index/index.pkl", "wb") as f:
            f.write(pkl_bytes)
        vector_store = FAISS.load_local(
            "/tmp/art_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info("RAG: FAISS index loaded from Object Storage.")
    except Exception as e:
        logger.warning(f"RAG: Index not available, running without retrieval. ({e})")

_download_index()

def get_art_context(query: str) -> str:
    if vector_store is None:
        return ""   # agent answers without RAG context until index is built
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(query)
    return "\n\n---\n\n".join([doc.page_content for doc in docs])
