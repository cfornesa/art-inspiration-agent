import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from replit.object_storage import Client

# ── Load all PDFs and DOCX files from art_documents/ ──────────────────────────
def load_document(filepath):
    if filepath.endswith(".pdf"):
        return PyPDFLoader(filepath).load()
    elif filepath.endswith(".docx"):
        return Docx2txtLoader(filepath).load()
    return []

all_docs = []
for filename in os.listdir("art_documents/"):
    filepath = os.path.join("art_documents/", filename)
    loaded = load_document(filepath)
    all_docs.extend(loaded)
    print(f"Loaded: {filename} ({len(loaded)} chunks)")

print(f"Total documents loaded: {len(all_docs)}")
# ──────────────────────────────────────────────────────────────────────────────

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)
chunks = splitter.split_documents(all_docs)

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    mistral_api_key=os.environ["MISTRAL_API_KEY"]
)

vector_store = FAISS.from_documents(chunks, embeddings)
vector_store.save_local("art_vector_store")
print(f"Built index with {len(chunks)} chunks.")

storage = Client()
storage.upload_from_filename("art_index/index.faiss", "art_vector_store/index.faiss")
storage.upload_from_filename("art_index/index.pkl",   "art_vector_store/index.pkl")
print("Index uploaded to Object Storage.")
