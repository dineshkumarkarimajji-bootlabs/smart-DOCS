Smart-DOCS 🧠

Secure AI-Powered Document QA System with User-Level Access Control

🚀 Overview

Smart-DOCS is an intelligent document management and question-answering system that allows multiple users to securely upload, query, and manage their own documents. Each user’s data and embeddings are private and isolated, ensuring full document access control.

It leverages FastAPI + ChromaDB for backend processing and a React frontend for an intuitive user interface.

✅ Key Features

🔐 User Authentication (Login / Logout) using JWT tokens

🧱 User-specific document isolation — users can only query their own uploads

📂 Document upload (PDF/TXT) with automatic text extraction and chunking

🧠 Semantic retrieval using SentenceTransformer embeddings

🤖 LLM-based question answering (via Ollama or HuggingFace models)

📊 Retrieval evaluation metrics for accuracy testing

⚙️ FastAPI + React full-stack integration

🏗️ Architecture

1. Frontend (React + Axios)

Modern, responsive interface for:

User login/logout

Document upload (PDF/TXT)

Question input and results display

Sends API requests (with JWT in headers) to backend endpoints

Displays retrieved chunks and LLM-generated answers

2. Backend (FastAPI)

Handles user management, document processing, and retrieval logic.

Main Components:

auth.py – JWT creation, validation, and OAuth2 authentication

main.py – FastAPI routes (/login, /upload, /query, /logout)

retriever.py – Document chunking, embedding generation, vector search

utils.py – PDF/TXT loading and preprocessing

3. Database (ChromaDB)

Documents are namespaced per user using metadata["user"]

Persistent storage under chroma_db/

Queries filter by user to ensure isolation

4. Authentication & Authorization Flow

User logs in → /token → JWT issued

JWT stored in frontend (e.g., localStorage)

All requests include token in Authorization header

Backend decodes token → identifies user → filters document access

5. Retrieval Pipeline

Upload → Chunk Document → Generate Embeddings → Store in ChromaDB

User Query → Retrieve Relevant Chunks (filtered by user) → Pass Context + Query to LLM → Return structured answer + relevant chunks

🧱 Tech Stack

Frontend:	React, Axios, Vite

Backend: FastAPI, Uvicorn

Auth:	JWT, python-jose, passlib

Embeddings:	SentenceTransformer (all-MiniLM-L6-v2)

Database:	ChromaDB

Environment	Poetry (Python 3.13)

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

Login with a user (as defined in auth.py)

Upload your PDFs/TXT files

Ask questions securely on your own documents

🧠 Example Usage (Python)

from App.retriever import Retriever

retriever = Retriever(embedding_model_name="all-MiniLM-L6-v2", chunk_size=250)

# Upload documents for user1

retriever.add_document("data/week1_Lecture.pdf", user="user1")

retriever.add_document("data/animal_facts.txt", user="user1")

# Query user-specific documents

results = retriever.query("What is transformer architecture?", top_k=5, user="user1")

# Evaluate retrieval quality

metrics = retriever.evaluate("What is transformer architecture?", results)

print("Results:", results)

print("Metrics:", metrics)


Each document and embedding is tagged with its uploader (user), ensuring complete isolation between users.

🔐 Security

JWT-based authentication protects all endpoints

Document retrieval is user-specific

Users cannot access other users’ documents or embeddings
