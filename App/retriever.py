import os
import time
import logging
from sentence_transformers import SentenceTransformer
from App.utils import chunk_text, load_pdf, load_txt
import chromadb
from chromadb.utils import embedding_functions

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Retriever:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2", chunk_size=300, persist_dir="chroma_db"):
        self.model = SentenceTransformer(embedding_model_name)
        self.chunk_size = chunk_size
        self.persist_dir = persist_dir

        # ✅ Ensure persistence directory exists
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)
            logging.warning(f"Chroma persist directory '{persist_dir}' was missing — created new one.")

        # ✅ Initialize persistent Chroma client (ensures data is stored on disk)
        self.client = chromadb.PersistentClient(path=persist_dir)

        # ✅ Define embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model_name
        )

        # ✅ Load or create the collection safely
        try:
            existing_collections = [c.name for c in self.client.list_collections()]
            if "documents" in existing_collections:
                self.collection = self.client.get_collection("documents")
                logging.info("Loaded existing Chroma collection 'documents'.")
            else:
                self.collection = self.client.create_collection(
                    name="documents",
                    embedding_function=self.embedding_function
                )
                logging.info("Created new Chroma collection 'documents'.")
        except Exception as e:
            logging.error(f"Error initializing Chroma collection: {e}")
            self.collection = self.client.create_collection(
                name="documents",
                embedding_function=self.embedding_function
            )
            logging.info("Recreated new Chroma collection due to error.")

    def add_document(self, file_path: str):
        """Load document, split into chunks, and index in ChromaDB."""
        start_time = time.time()
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = load_pdf(file_path)
        else:
            text = load_txt(file_path)

        chunks = chunk_text(text, chunk_size=self.chunk_size)
        metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]

        # ✅ Add to ChromaDB
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

        elapsed = time.time() - start_time
        logging.info(f"Indexed {len(chunks)} chunks from {file_path} in {elapsed:.2f}s")
        logging.info(f"ChromaDB persisted successfully at '{self.persist_dir}'")

    def query(self, query_text: str, top_k: int = 5, filter_doc: str = None):
        """Query ChromaDB with optional metadata filtering."""
        start_time = time.time()

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k * 2,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logging.error(f"Query failed: {e}")
            return []

        retrieved = []
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            if filter_doc and filter_doc.lower() not in meta.get("source", "").lower():
                continue
            retrieved.append({
                "text": doc,
                "source": meta.get("source"),
                "score": float(dist)
            })
            if len(retrieved) >= top_k:
                break

        latency = time.time() - start_time
        logging.info(f"Query '{query_text[:40]}...' retrieved {len(retrieved)} results in {latency:.2f}s")
        return retrieved

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
