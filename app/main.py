from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import shutil
import uuid
import os
import zipfile
from app.colmap_runner import run_colmap_pipeline  # 👈 nuovo import

app = FastAPI()

UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ✅ CARICAMENTO FILE SINGOLI (list[UploadFile])
@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    for file in files:
        file_path = os.path.join(session_path, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    output_model_path = run_colmap_pipeline(session_path, os.path.join(OUTPUT_DIR, session_id))
    return {"session_id": session_id, "output_model": output_model_path}


# ✅ CARICAMENTO .ZIP con tutte le immagini
@app.post("/upload_zip")
async def upload_zip(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    zip_path = os.path.join(session_path, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(session_path)

    output_model_path = run_colmap_pipeline(session_path, os.path.join(OUTPUT_DIR, session_id))
    return {"session_id": session_id, "output_model": output_model_path}


# ✅ DOWNLOAD del modello 3D
@app.get("/result/{session_id}")
def get_result(session_id: str):
    model_path = os.path.join(OUTPUT_DIR, session_id, "final_model.ply")
    if os.path.exists(model_path):
        return FileResponse(model_path, media_type="model/ply", filename="auto3d.ply")
    return {"error": "Modello non trovato"}
