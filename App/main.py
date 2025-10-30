from fastapi import FastAPI, UploadFile, File, Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from App.retriever import Retriever
from App.llm import ask_llm
from App.auth import authenticate_user, create_access_token, get_current_user
import os, time, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title="Secure Document QA")
retriever = Retriever()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Auth endpoint ---
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Upload endpoint ---
@app.post("/upload")
async def upload(files: list[UploadFile] = File(...), current_user: dict = Depends(get_current_user)):
    start_time = time.time()
    uploaded_files = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, f"{current_user['username']}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(await file.read())

        retriever.add_document(file_path, user=current_user["username"])
        uploaded_files.append(file.filename)
        logging.info(f"Uploaded and indexed: {file.filename}")

    elapsed = time.time() - start_time
    return {"message": f"{len(uploaded_files)} files uploaded.", "files": uploaded_files, "upload_time_sec": round(elapsed, 2)}

# --- Query endpoint ---
@app.get("/query")
def query(q: str = Query(...), top_k: int = 5, use_llm: bool = True, current_user: dict = Depends(get_current_user)):
    results = retriever.query(query_text=q, top_k=top_k, user=current_user["username"])
    answer = ask_llm(q, [r["text"] for r in results]) if use_llm else None
    return {"query": q, "results": results, "answer": answer}
