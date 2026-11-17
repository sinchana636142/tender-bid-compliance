
"""Local semantic indexing with Sentence Transformers and ChromaDB."""
from pathlib import Path
from functools import lru_cache
import hashlib
import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer
from app.retrieval.document_search import PROJECT_ROOT, DOCUMENT_FOLDERS

DB_PATH = PROJECT_ROOT / "data" / "chroma"
COLLECTION_NAME = "tender_pages"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180

@lru_cache(maxsize=1)
def get_model():
    # First launch downloads the model; subsequent launches use the local cache.
    return SentenceTransformer(MODEL_NAME)

@lru_cache(maxsize=1)
def get_collection():
    DB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_PATH))
    return client.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space":"cosine"})

def split_text(text: str):
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks

def index_pdf(path: Path):
    path = Path(path)
    if path.suffix.lower() != ".pdf" or not path.is_file():
        raise ValueError("A valid PDF file is required.")
    records = []
    with pymupdf.open(str(path)) as pdf:
        for page_no, page in enumerate(pdf, start=1):
            page_text = (page.get_text("text") or "").strip()
            for chunk_no, chunk in enumerate(split_text(page_text)):
                doc_id = hashlib.sha1(f"{path.name}:{page_no}:{chunk_no}".encode()).hexdigest()
                records.append((doc_id, chunk, {"document":path.name,"page":page_no,"chunk":chunk_no}))
    if not records:
        raise ValueError("No selectable text found in this PDF. OCR may be required for scanned PDFs.")
    model = get_model()
    collection = get_collection()
    # Upsert makes re-uploading the same PDF safe.
    batch = 64
    for i in range(0, len(records), batch):
        part = records[i:i+batch]
        vectors = model.encode([r[1] for r in part], normalize_embeddings=True).tolist()
        collection.upsert(ids=[r[0] for r in part], documents=[r[1] for r in part],
                          metadatas=[r[2] for r in part], embeddings=vectors)
    return {"document":path.name,"pages":len({r[2]["page"] for r in records}),"chunks_indexed":len(records)}

def index_corpus():
    summary = []
    for folder in DOCUMENT_FOLDERS:
        if folder.exists():
            for path in folder.glob("*.pdf"):
                try:
                    summary.append(index_pdf(path))
                except Exception as exc:
                    summary.append({"document":path.name,"error":str(exc)})
    return summary

def semantic_search(query: str, top_k: int = 5):
    if not query.strip():
        raise ValueError("Query cannot be empty.")
    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")
    collection = get_collection()
    if collection.count() == 0:
        index_corpus()
    if collection.count() == 0:
        return []
    vector = get_model().encode([query], normalize_embeddings=True).tolist()
    result = collection.query(query_embeddings=vector, n_results=min(top_k, collection.count()),
                              include=["documents","metadatas","distances"])
    output = []
    for doc, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        output.append({"document":meta["document"],"page":meta["page"],"text":doc,
                       "similarity":round(max(0.0, 1.0-float(distance)),4)})
    return output
