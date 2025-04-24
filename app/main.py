from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import shutil
import uuid
import os
import zipfile
import threading
import json
from app.colmap_runner import run_colmap_pipeline

app = FastAPI()

UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"
STATUS_DIR = "/workspace/status"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STATUS_DIR, exist_ok=True)

# Funzione di stato
def update_status(session_id: str, status: str):
    with open(os.path.join(STATUS_DIR, f"{session_id}.json"), "w") as f:
        json.dump({"status": status}, f)

def get_status(session_id: str):
    path = os.path.join(STATUS_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"status": "not_found"}

# Task COLMAP in background
def background_task(session_id: str, session_path: str):
    try:
        update_status(session_id, "processing")
        run_colmap_pipeline(session_path, os.path.join(OUTPUT_DIR, session_id))
        update_status(session_id, "done")
    except Exception as e:
        update_status(session_id, f"error: {str(e)}")

# ✅ Upload ZIP
@app.post("/upload_zip")
async def upload_zip(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    zip_path = os.path.join(session_path, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.infolist():
            if member.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                zip_ref.extract(member, session_path)

    threading.Thread(target=background_task, args=(session_id, session_path), daemon=True).start()
    return {"session_id": session_id}

# ✅ Upload singolo
@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    for file in files:
        file_path = os.path.join(session_path, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    threading.Thread(target=background_task, args=(session_id, session_path), daemon=True).start()
    return {"session_id": session_id}

# ✅ Check status
@app.get("/status/{session_id}")
def status(session_id: str):
    return get_status(session_id)

# ✅ Download modello
@app.get("/result/{session_id}")
def get_result(session_id: str):
    model_path = os.path.join(OUTPUT_DIR, session_id, "final_model.ply")
    if os.path.exists(model_path):
        return FileResponse(model_path, media_type="model/ply", filename="auto3d.ply")
    return {"error": "Modello non trovato o non ancora pronto"}
