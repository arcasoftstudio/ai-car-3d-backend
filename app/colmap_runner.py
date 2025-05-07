import os
import subprocess
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def run_colmap_sparse_only(upload_folder):
    images_path = os.path.join(upload_folder, "images")
    sparse_path = os.path.join(upload_folder, "sparse")
    database_path = os.path.join(upload_folder, "database.db")

    os.makedirs(images_path, exist_ok=True)
    os.makedirs(sparse_path, exist_ok=True)

    logger.info("\n🔍 Estrazione feature...")
    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_path,
        "--ImageReader.single_camera", "1"
    ], check=True)

    logger.info("\n🔍 Matching sequenziale (come nella GUI)...")
    subprocess.run([
        "colmap", "sequential_matcher",
        "--database_path", database_path,
        "--SiftMatching.guided_matching", "1"
    ], check=True)

    logger.info("\n🏗️ Ricostruzione sparsa...")
    subprocess.run([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", images_path,
        "--output_path", sparse_path,
        "--Mapper.extract_colors", "1"
    ], check=True)

    # ✅ Verifica sparse
    sparse_model_dir = os.path.join(sparse_path, "0")
    if not os.path.exists(os.path.join(sparse_model_dir, "cameras.bin")):
        raise Exception("❌ Errore: ricostruzione sparsa fallita, sparse/0 mancante o incompleto.")
    else:
        logger.info(f"📸 Ricostruzione sparsa completata. File presenti: {os.listdir(sparse_model_dir)}")

    logger.info("\n✅ Solo punti (sparse) generati. Fine processo.")
    return sparse_model_dir
