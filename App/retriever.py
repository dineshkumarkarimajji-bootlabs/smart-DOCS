
import os, time, logging
from sentence_transformers import SentenceTransformer
from App.utils import chunk_text, load_pdf, load_txt
import chromadb
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Retriever:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2", chunk_size=300, persist_dir="chroma_db"):
        self.model = SentenceTransformer(embedding_model_name)
        self.chunk_size = chunk_size
        self.persist_dir = persist_dir

        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)

        try:
            existing_collections = [c.name for c in self.client.list_collections()]
            if "documents" in existing_collections:
                self.collection = self.client.get_collection("documents")
            else:
                self.collection = self.client.create_collection(name="documents", embedding_function=self.embedding_function)
        except Exception as e:
            logging.error(f"Error initializing collection: {e}")
            self.collection = self.client.create_collection(name="documents", embedding_function=self.embedding_function)

    def add_document(self, file_path: str, user: str):
        text = load_pdf(file_path) if file_path.endswith(".pdf") else load_txt(file_path)
        chunks = chunk_text(text, self.chunk_size)
        metadatas = [{"source": os.path.basename(file_path), "user": user} for _ in chunks]
        ids = [f"{user}_{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]

        # Add documents to collection
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )



        logging.info(f"Indexed {len(chunks)} chunks from {file_path} for user '{user}'")

    def query(self, query_text: str, top_k: int = 5, user: str = None):
        results = self.collection.query(query_texts=[query_text], n_results=top_k*2, include=["documents","metadatas","distances"])
        filtered = []
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            if user and meta.get("user") != user:
                continue
            filtered.append({"text": doc, "source": meta.get("source"), "score": float(dist)})
            if len(filtered) >= top_k:
                break
        return filtered


    def evaluate(self, query_text: str, retrieved_docs: list, ground_truth: str = None):
        """Compute basic RAG metrics."""
        if not retrieved_docs:
            return {"avg_similarity": 0.0, "hallucination_rate": 1.0}

        similarities = [1 / (1 + r["score"]) for r in retrieved_docs]
        avg_similarity = sum(similarities) / len(similarities)
        hallucination_rate = 1 - avg_similarity

        logging.info(f"Evaluation -> Similarity: {avg_similarity:.3f}, Hallucination Rate: {hallucination_rate:.3f}")
        return {
            "avg_similarity": float(avg_similarity),
            "hallucination_rate": float(hallucination_rate)
        }
