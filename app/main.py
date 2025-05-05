
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

UPLOAD_FOLDER = "/workspace/uploads"
STATUS_FOLDER = "/workspace/status"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATUS_FOLDER, exist_ok=True)

def process_colmap(file_id, file_folder):
    try:
        run_colmap_pipeline(file_folder)
        # ✅ Salva stato completato
        status_path = os.path.join(STATUS_FOLDER, f"{file_id}.json")
        with open(status_path, "w") as f:
            json.dump({"status": "completed"}, f)
    except Exception as e:
        # ✅ Salva stato failed + errore dettagliato
        status_path = os.path.join(STATUS_FOLDER, f"{file_id}.json")
        with open(status_path, "w") as f:
            json.dump({"status": "failed", "error": str(e)}, f)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_folder = os.path.join(UPLOAD_FOLDER, file_id)
    images_folder = os.path.join(file_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    file_location = os.path.join(file_folder, "uploaded.zip")
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with zipfile.ZipFile(file_location, 'r') as zip_ref:
        zip_ref.extractall(images_folder)

    # ✅ Scrivi subito che è in processing
    status_path = os.path.join(STATUS_FOLDER, f"{file_id}.json")
    with open(status_path, "w") as f:
        json.dump({"status": "processing"}, f)

    # ✅ Avvia COLMAP in background
    threading.Thread(target=process_colmap, args=(file_id, file_folder)).start()

    return {
        "file_id": file_id,
        "message": "Processing started",
        "status_url": f"/status/{file_id}",
        "download_url": f"/download/{file_id}"
    }

@app.get("/status/{file_id}")
async def check_status(file_id: str):
    status_path = os.path.join(STATUS_FOLDER, f"{file_id}.json")
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            status = json.load(f)
        return status
    return {"status": "not_found"}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = os.path.join(UPLOAD_FOLDER, file_id, "final_mesh.ply")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename="final_mesh.ply")
    return {"error": "File not found"}
