import os
import time
import numpy as np
import faiss
import logging
from sentence_transformers import SentenceTransformer
from App.utils import chunk_text, load_pdf, load_txt

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Retriever:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2", chunk_size=300):
        self.model = SentenceTransformer(embedding_model_name)
        self.chunk_size = chunk_size
        self.sentences = []  # Stores chunks with metadata
        self.embeddings = None
        self.index = None
        logging.info(f"Initialized retriever with model={embedding_model_name}, chunk_size={chunk_size}")

    def add_document(self, file_path: str):
        """Load document, split into chunks, and index."""
        start_time = time.time()
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = load_pdf(file_path)
        else:
            text = load_txt(file_path)

        chunks = chunk_text(text, chunk_size=self.chunk_size)
        for chunk in chunks:
            self.sentences.append({
                "text": chunk,
                "source": os.path.basename(file_path)
            })

        # Compute embeddings
        embeddings = self.model.encode([c["text"] for c in self.sentences], convert_to_numpy=True)

        # Initialize or update FAISS index
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack((self.embeddings, embeddings))

        self.index.add(embeddings)
        elapsed = time.time() - start_time
        logging.info(f"Indexed {len(chunks)} chunks from {file_path} in {elapsed:.2f}s")

    def query(self, query_text: str, top_k: int = 5, filter_doc: str = None):
        """Query index with optional metadata filtering."""
        if self.index is None or len(self.sentences) == 0:
            return []

        start_time = time.time()
        query_vec = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(query_vec, top_k * 2)  # Fetch extra for filtering

        results = []
        for i, score in zip(I[0], D[0]):
            if i < len(self.sentences):
                entry = self.sentences[i]
                if filter_doc and filter_doc.lower() not in entry["source"].lower():
                    continue
                results.append({
                    "text": entry["text"],
                    "source": entry["source"],
                    "score": float(score)
                })
                if len(results) >= top_k:
                    break

        latency = time.time() - start_time
        logging.info(f"Query '{query_text[:40]}...' retrieved {len(results)} results in {latency:.2f}s")

        return results

    def evaluate(self, query_text: str, retrieved_docs: list, ground_truth: str = None):
        """Compute basic RAG metrics."""
        if not retrieved_docs:
            return {"avg_similarity": 0.0, "hallucination_rate": 1.0}

        similarities = [1 / (1 + r["score"]) for r in retrieved_docs]  # Convert distance to similarity
        avg_similarity = np.mean(similarities)

        # Placeholder hallucination rate (use LLM comparison if available)
        hallucination_rate = 1 - avg_similarity  # Simplistic proxy

        logging.info(f"Evaluation -> Similarity: {avg_similarity:.3f}, Hallucination Rate: {hallucination_rate:.3f}")
        return {
            "avg_similarity": float(avg_similarity),
            "hallucination_rate": float(hallucination_rate)
        }
