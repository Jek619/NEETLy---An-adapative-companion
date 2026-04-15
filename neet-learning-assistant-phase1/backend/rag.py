# backend/rag.py
"""
RAG utilities: embedding via OpenAI + vector store.
Uses faiss if available; otherwise a simple numpy-based store (cosine similarity).
"""
import os
import asyncio
from typing import List, Dict, Tuple
import numpy as np
import openai

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # We won't raise here; many endpoints check before using OpenAI.
    pass
openai.api_key = OPENAI_API_KEY

EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")  # or text-embedding-3-large

# Try to import faiss; if unavailable, we'll fallback.
try:
    import faiss
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

# Simple in-memory fallback
class InMemoryStore:
    def __init__(self):
        self.vectors = None  # numpy array shape (n, dim)
        self.metadatas = []

    def add(self, vectors: np.ndarray, metadatas: List[dict]):
        if self.vectors is None:
            self.vectors = vectors.copy()
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        self.metadatas.extend(metadatas)

    def search(self, qvec: np.ndarray, k: int = 5) -> List[Tuple[dict, float]]:
        if self.vectors is None or self.vectors.shape[0] == 0:
            return []
        # cosine similarity
        q = qvec / (np.linalg.norm(qvec, axis=1, keepdims=True) + 1e-12)
        X = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-12)
        sims = (X @ q.T).squeeze()  # shape (n,)
        idx = np.argsort(-sims)[:k]
        return [(self.metadatas[i], float(sims[i])) for i in idx]

# Faiss wrapper
class FaissStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # use inner product on normalized vectors
        self.metadatas = []

    def add(self, vectors: np.ndarray, metadatas: List[dict]):
        # normalize vectors for cosine via inner product
        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
        vectors = vectors / norms
        self.index.add(vectors.astype(np.float32))
        self.metadatas.extend(metadatas)

    def search(self, qvec: np.ndarray, k: int = 5):
        qnorm = qvec / (np.linalg.norm(qvec, axis=1, keepdims=True) + 1e-12)
        D, I = self.index.search(qnorm.astype(np.float32), k)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx < len(self.metadatas):
                results.append((self.metadatas[idx], float(score)))
        return results

# singleton store (will be created on first use)
_STORE = None
_STORE_DIM = None

def get_store(dim: int):
    global _STORE, _STORE_DIM
    if _STORE is None or _STORE_DIM != dim:
        if HAS_FAISS:
            _STORE = FaissStore(dim)
        else:
            _STORE = InMemoryStore()
        _STORE_DIM = dim
    return _STORE

# Embedding helper (non-blocking wrapper)
async def get_embeddings(texts: List[str]) -> List[List[float]]:
    loop = asyncio.get_running_loop()
    # run blocking OpenAI call in executor
    def _call():
        resp = openai.Embedding.create(model=EMBED_MODEL, input=texts)
        return [r["embedding"] for r in resp["data"]]
    embeddings = await loop.run_in_executor(None, _call)
    return embeddings

async def embed_and_add(chunks: List[dict]):
    """
    chunks: list of dicts with key 'text' and optional metadata fields.
    """
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    embs = await get_embeddings(texts)
    arr = np.array(embs).astype("float32")
    store = get_store(arr.shape[1])
    metadatas = []
    for c in chunks:
        met = {
            "subject": c.get("subject", "unknown"),
            "chapter": c.get("chapter", "unknown"),
            "page": c.get("page"),
            "text_preview": (c.get("text") or "")[:400],
        }
        metadatas.append(met)
    store.add(arr, metadatas)
    return len(metadatas)

async def retrieve(query: str, k: int = 4) -> List[dict]:
    if not query:
        return []
    embs = await get_embeddings([query])
    arr = np.array(embs).astype("float32")
    store = get_store(arr.shape[1])
    results = store.search(arr, k)
    return [{"metadata": m, "score": s} for (m, s) in results]
