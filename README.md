# smart-DOCS
🧠 Smart-DOCS

Secure AI-Powered Document QA System with User-Level Access Control

🚀 Overview

Smart-DOCS is an intelligent document management and question-answering system that allows multiple users to securely upload, query, and manage their own documents. Each user’s data and embeddings are private and isolated, ensuring full document access control.

It uses FastAPI + ChromaDB for backend processing and a React frontend for an intuitive user interface.

✅ Key Features

🔐 User Authentication (Login / Logout) using JWT tokens

🧱 User-specific document isolation — users can only query their own uploads

📂 Document upload (PDF/TXT) with automatic text extraction and chunking

🧠 Semantic retrieval using SentenceTransformer embeddings

🤖 LLM-based question answering (via Ollama or HuggingFace models)

📊 Retrieval evaluation metrics for accuracy testing

⚙️ FastAPI + React full-stack integration

Architecture

🔷 1. Frontend (React + Axios)

Provides a modern, responsive interface for:

User Login / Logout

Document Upload (PDF/TXT)

Question Input and Results Display

Sends API requests (with JWT in headers) to backend endpoints for upload and querying.

Displays results, relevant document snippets, and the LLM-generated answer.

🔶 2. Backend (FastAPI)

Handles user management, document processing, and retrieval logic.

Main Components:

auth.py – Manages JWT creation, validation, and OAuth2 authentication flow.

main.py – Defines FastAPI routes (/login, /upload, /query, /logout).

retriever.py – Handles document chunking, embedding generation, and vector search.

utils.py – Helper functions for PDF/TXT loading and text preprocessing.

🔸 3. Database (ChromaDB)

Each user’s documents are stored as separate collections or namespaced entries with metadata["user"].

During query time, only chunks belonging to the requesting user are retrieved.

Persistent storage is under chroma_db/ directory.

🔹 4. Authentication & Authorization Flow

[Login Form] → [FastAPI /token] → issues JWT token

→ JWT stored in localStorage

→ All future requests include token in Authorization header

→ Backend decodes token to identify user → filters document access

🔸 5. Retrieval Pipeline

Upload → Chunk Document → Generate Embeddings → Store in ChromaDB

User Query → Retrieve Relevant Chunks (filtered by user)
          → Pass Context + Query to LLM (e.g., Ollama/HuggingFace)
          → Return Structured Answer + Relevant Chunks

🧱 Tech Stack

Frontend:	React, Axios, Vite
Backend:	FastAPI, Uvicorn
Auth:	JWT, python-jose, passlib
Embeddings:	SentenceTransformer (all-MiniLM-L6-v2)
Database:	ChromaDB
Environment:	Poetry (Python 3.13)

⚙️ Setup Instructions

1️⃣ Clone the Repository
git clone https://github.com/dineshkumarkarimajji-bootlabs/smart-DOCS.git

cd smart-DOCS

2️⃣ Backend Setup
poetry install
poetry run uvicorn App.main:app --reload

3️⃣ Frontend Setup
cd rag-frontend
npm install
npm run dev

4️⃣ Access the App

Visit: http://localhost:5173

Login with a user (e.g., from auth.py)

Upload your PDFs/TXT files

Ask questions securely on your own documents

🧠 Example Usage (Python Script)
from App.retriever import Retriever

retriever = Retriever(embedding_model_name="all-MiniLM-L6-v2", chunk_size=250)
retriever.add_document("data/week1_Lecture.pdf", user="user1")
retriever.add_document("data/animal_facts.txt", user="user1")

results = retriever.query("What is transformer architecture?", top_k=5, user="user1")
metrics = retriever.evaluate("What is transformer architecture?", results)

print("Results:", results)
print("Metrics:", metrics)


Each document and embedding is tagged with its uploader (user), ensuring isolation between users.



