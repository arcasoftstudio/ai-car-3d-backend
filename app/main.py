from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import uuid
import os
from scripts.run_meshroom import run_meshroom

app = FastAPI()

UPLOAD_DIR = "/workspace/uploads"
OUTPUT_DIR = "/workspace/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    for file in files:
        file_path = os.path.join(session_path, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    # Lancia Meshroom
    run_meshroom(session_path, os.path.join(OUTPUT_DIR, session_id))

    return {"session_id": session_id}

@app.get("/result/{session_id}")
def get_result(session_id: str):
    model_path = os.path.join(OUTPUT_DIR, session_id, "texturedMesh.obj")
    if os.path.exists(model_path):
        return FileResponse(model_path, media_type="model/obj", filename="auto3d.obj")
    return {"error": "Modello non trovato"}
