from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from App.retriever import Retriever
from App.llm import ask_llm
import os
import time
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="Document QA System")
retriever = Retriever()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    start_time = time.time()
    uploaded_files = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        retriever.add_document(file_path)
        uploaded_files.append(file.filename)
        logging.info(f"Uploaded and indexed: {file.filename}")

    elapsed = time.time() - start_time
    return {
        "message": f"{len(uploaded_files)} files uploaded and indexed.",
        "files": uploaded_files,
        "upload_time_sec": round(elapsed, 2)
    }


@app.get("/query")
def query(
    q: str = Query(..., description="Your question for the documents"),
    use_llm: bool = True,
    top_k: int = 5,
    filter_doc: str | None = None
):
    start_time = time.time()
    results = retriever.query(query_text=q, top_k=top_k, filter_doc=filter_doc)
    latency = time.time() - start_time
    logging.info(f"Query '{q[:40]}...' retrieved {len(results)} results in {latency:.2f}s")

    response = {"query": q, "results": results, "retrieval_time_sec": round(latency, 2)}

    if use_llm:
        context_chunks = [r["text"] for r in results]
        answer = ask_llm(q, context_chunks)
        response["answer"] = answer

    return response